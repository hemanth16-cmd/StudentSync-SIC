import os
import requests
from dotenv import load_dotenv

from authentication.validators import (
    validate_email,
    validate_password,
)

from authentication.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
)

load_dotenv()

API_KEY = os.getenv("FIREBASE_API_KEY")


class AuthService:

    SIGNUP_URL = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
    )

    LOGIN_URL = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    )

    @staticmethod
    def signup(email, password):

        email = validate_email(email)
        password = validate_password(password)

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        response = requests.post(
            f"{AuthService.SIGNUP_URL}?key={API_KEY}",
            json=payload
        )

        if response.status_code == 200:
            return response.json()

        error = response.json()["error"]["message"]

        if error == "EMAIL_EXISTS":
            raise UserAlreadyExistsError("Email already registered.")

        raise Exception(error)

    @staticmethod
    def login(email, password):

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        response = requests.post(
            f"{AuthService.LOGIN_URL}?key={API_KEY}",
            json=payload
        )

        if response.status_code == 200:
            return response.json()

        raise InvalidCredentialsError(
            response.json()["error"]["message"]
        )