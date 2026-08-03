import os
import requests

from dotenv import load_dotenv

from firebase_admin import auth
from firebase_admin._auth_utils import EmailAlreadyExistsError

from authentication.firebase_auth import (
    initialize_firebase,
    get_db,
)

from authentication.models import User
from authentication.session import Session

from authentication.validators import (
    validate_email,
    validate_password,
    validate_name,
)

from authentication.exceptions import (
    UserAlreadyExists,
    InvalidCredentials,
    FirebaseError,
)

load_dotenv()

API_KEY = os.getenv("FIREBASE_API_KEY")


class AuthService:

    @staticmethod
    def signup(name, email, password):

        initialize_firebase()

        validate_name(name)
        validate_email(email)
        validate_password(password)

        try:
            firebase_user = auth.create_user(
                email=email,
                password=password,
                display_name=name,
            )

            print(f"[AUTH] Created Firebase user: {firebase_user.uid}")

            user = User(
                uid=firebase_user.uid,
                name=name,
                email=email,
            )

            db = get_db()

            print("[FIRESTORE] Writing user document...")

            db.collection("users").document(user.uid).set(
                user.to_dict()
            )

            print("[FIRESTORE] User document written successfully!")

            Session.login(user)

            return user

        except EmailAlreadyExistsError:
            raise UserAlreadyExists(
                "This email is already registered."
            )

        except Exception as e:
            raise FirebaseError(str(e))

    @staticmethod
    def login(email, password):

        initialize_firebase()

        url = (
            "https://identitytoolkit.googleapis.com/v1/"
            f"accounts:signInWithPassword?key={API_KEY}"
        )

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            raise InvalidCredentials(
                "Incorrect email or password."
            )

        uid = response.json()["localId"]

        print(f"[AUTH] Logged in UID: {uid}")

        db = get_db()

        doc = db.collection("users").document(uid).get()

        print(f"[FIRESTORE] Document exists: {doc.exists}")

        if doc.exists:
            print(f"[FIRESTORE] Document data: {doc.to_dict()}")

        if not doc.exists:
            raise FirebaseError(
                "User exists in Authentication but not Firestore."
            )

        user = User.from_dict(doc.to_dict())

        Session.login(user)

        return user

    @staticmethod
    def logout():
        """
        Logs out the currently authenticated user.
        """
        Session.logout()


    @staticmethod
    def current_user():
        """
        Returns the currently logged-in user,
        or None if no user is logged in.
        """
        return Session.current_user()


    @staticmethod
    def is_logged_in():
        """
        Returns True if a user is currently logged in.
        """
        return Session.is_logged_in()