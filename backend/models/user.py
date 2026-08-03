"""
User Model Schemas for StudentSync
"""

from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class UserCreate:
    username: str
    email: str
    full_name: str
    password: str
    college: Optional[str] = ""
    gpa_scale: Optional[int] = 10


@dataclass
class UserResponse:
    id: str
    username: str
    email: str
    full_name: str
    college: str = ""
    gpa_scale: int = 10
    is_active: bool = True
    created_at: str = ""
