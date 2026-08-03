"""
Academic Schemas (Subjects, Assignments, Notes)
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class SubjectCreate:
    name: str
    code: Optional[str] = ""
    teacher: Optional[str] = ""
    credits: Optional[int] = 3
    room: Optional[str] = ""
    color: Optional[str] = "#2563EB"
    emoji: Optional[str] = "📚"


@dataclass
class AssignmentCreate:
    title: str
    subject: Optional[str] = ""
    due_date: Optional[str] = ""
    priority: Optional[str] = "medium"


@dataclass
class NoteCreate:
    title: str
    content: Optional[str] = ""
    subject: Optional[str] = "General"
