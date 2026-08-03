"""
Authentication Business Logic Service (SQLite connection layer)
"""

import uuid
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from backend.config.settings import settings
from backend.models.user import UserCreate


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = settings.SECRET_KEY.encode('utf-8')
        return hmac.new(salt, password.encode('utf-8'), hashlib.sha256).hexdigest()

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.hash_password(plain_password) == hashed_password

    @classmethod
    def register_user(cls, conn, user_data: UserCreate) -> Dict[str, Any]:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (user_data.username, user_data.email))
        if cursor.fetchone():
            raise ValueError("User with this username or email already exists")

        user_id = f"usr_{uuid.uuid4().hex[:8]}"
        hashed_pw = cls.hash_password(user_data.password)
        created_at = datetime.utcnow().isoformat()

        cursor.execute(
            """
            INSERT INTO users (id, username, email, full_name, hashed_password, college, gpa_scale, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
            """,
            (user_id, user_data.username, user_data.email, user_data.full_name, hashed_pw, user_data.college or "", user_data.gpa_scale or 10, created_at)
        )
        conn.commit()
        return {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "college": user_data.college or "",
            "gpa_scale": user_data.gpa_scale or 10,
            "is_active": True,
            "created_at": created_at
        }

    @classmethod
    def authenticate_user(cls, conn, username: str, password: str) -> Optional[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            return None
        user_dict = dict(row)
        if not cls.verify_password(password, user_dict["hashed_password"]):
            return None
        user_dict.pop("hashed_password", None)
        return user_dict

    @classmethod
    def create_access_token(cls, data: dict) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = f"{data.get('sub')}:{expire.timestamp()}"
        return hashlib.sha256(f"{payload}:{settings.SECRET_KEY}".encode('utf-8')).hexdigest()
