"""
To-Do Task Schemas
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class TodoCreate:
    title: str
    description: Optional[str] = ""
    subject: Optional[str] = ""
    priority: Optional[str] = "medium"
    due_date: Optional[str] = ""


@dataclass
class TodoResponse:
    id: str
    title: str
    description: str
    subject: str
    priority: str
    due_date: str
    completed: bool
    created_at: str
