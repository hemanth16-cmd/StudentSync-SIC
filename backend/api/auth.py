"""
Authentication API Router (Standard library compatibility)
"""

from backend.database import get_db
from backend.models.user import UserCreate
from backend.services.auth_service import AuthService


def handle_register(user_data: dict, conn=None):
    if conn is None:
        conn = next(get_db())
    user_in = UserCreate(**user_data)
    return AuthService.register_user(conn, user_in)


def handle_login(credentials: dict, conn=None):
    if conn is None:
        conn = next(get_db())
    user = AuthService.authenticate_user(conn, credentials.get("username", ""), credentials.get("password", ""))
    if not user:
        return {"error": "Invalid username or password"}
    token = AuthService.create_access_token({"sub": user["username"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }
