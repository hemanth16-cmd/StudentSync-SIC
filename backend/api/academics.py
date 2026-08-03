"""
Academics API Router (Subjects, Assignments, Notes)
"""

from backend.database import get_db
from backend.models.academic import SubjectCreate, AssignmentCreate, NoteCreate
from backend.services.academic_service import AcademicService


def get_subjects(conn=None):
    if conn is None: conn = next(get_db())
    return AcademicService.get_subjects(conn)


def create_subject(data: dict, conn=None):
    if conn is None: conn = next(get_db())
    return AcademicService.create_subject(conn, SubjectCreate(**data))


def get_assignments(conn=None):
    if conn is None: conn = next(get_db())
    return AcademicService.get_assignments(conn)


def create_assignment(data: dict, conn=None):
    if conn is None: conn = next(get_db())
    return AcademicService.create_assignment(conn, AssignmentCreate(**data))


def get_notes(conn=None):
    if conn is None: conn = next(get_db())
    return AcademicService.get_notes(conn)


def create_note(data: dict, conn=None):
    if conn is None: conn = next(get_db())
    return AcademicService.create_note(conn, NoteCreate(**data))
