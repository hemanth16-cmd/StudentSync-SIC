
import os
import requests
from dotenv import load_dotenv

try:
    from firebase_admin import auth
    from firebase_admin._auth_utils import EmailAlreadyExistsError
    from authentication.firebase_auth import (
        initialize_firebase,
        get_db,
    )
except ImportError:
    auth = None
    EmailAlreadyExistsError = Exception
    initialize_firebase = lambda: None
    get_db = lambda: None


from authentication.models import User
from authentication.session import Session
from authentication.validators import validate_email, validate_password, validate_name
from authentication.exceptions import UserAlreadyExists, InvalidCredentials


def _hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

class AuthService:

    @staticmethod
    def signup(name, email, password):
        validate_name(name)
        validate_email(email)
        validate_password(password)

        db = SessionLocal()
        try:
            repo = UserRepository(db)
            existing = repo.get_by_email(email)
            if existing:
                raise UserAlreadyExists("This email is already registered.")

            hashed_password = _hash_password(password)
            db_user = repo.create(name=name, email=email, password_hash=hashed_password)
            
            # Convert SQLAlchemy User to auth.User
            user = User(uid=db_user.id, name=db_user.name, email=db_user.email, role=db_user.role)
            Session.login(user)
            return user
        finally:
            db.close()

    @staticmethod
    def login(email, password):
        db = SessionLocal()
        try:
            repo = UserRepository(db)
            db_user = repo.get_by_email(email)
            if not db_user or not _verify_password(password, db_user.password_hash):
                raise InvalidCredentials("Incorrect email or password.")
            
            user = User(uid=db_user.id, name=db_user.name, email=db_user.email, role=db_user.role)
            Session.login(user)
            return user
        finally:
            db.close()

    @staticmethod
    def logout():
        Session.logout()

    @staticmethod
    def current_user():
        return Session.current_user()

    @staticmethod
    def is_logged_in():
        return Session.is_logged_in()