"""
Academic Services Business Logic (Subjects, Assignments, Notes)
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from backend.models.academic import SubjectCreate, AssignmentCreate, NoteCreate


class AcademicService:
    # ── SUBJECTS ──
    @staticmethod
    def get_subjects(conn, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        if user_id:
            cursor.execute("SELECT * FROM subjects WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("SELECT * FROM subjects")
        return [dict(r) for r in cursor.fetchall()]

    @staticmethod
    def create_subject(conn, subject_in: SubjectCreate, user_id: Optional[str] = None) -> Dict[str, Any]:
        cursor = conn.cursor()
        sid = f"subj_{uuid.uuid4().hex[:8]}"
        cursor.execute(
            """
            INSERT INTO subjects (id, user_id, name, code, teacher, credits, room, color, emoji)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (sid, user_id, subject_in.name, subject_in.code or "", subject_in.teacher or "", subject_in.credits or 3, subject_in.room or "", subject_in.color or "#2563EB", subject_in.emoji or "📚")
        )
        conn.commit()
        return {
            "id": sid, "user_id": user_id, "name": subject_in.name, "code": subject_in.code or "",
            "teacher": subject_in.teacher or "", "credits": subject_in.credits or 3,
            "attended": 0, "bunked": 0, "room": subject_in.room or "", "color": subject_in.color or "#2563EB", "emoji": subject_in.emoji or "📚"
        }

    # ── ASSIGNMENTS ──
    @staticmethod
    def get_assignments(conn, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assignments")
        return [dict(r) for r in cursor.fetchall()]

    @staticmethod
    def create_assignment(conn, asgn_in: AssignmentCreate, user_id: Optional[str] = None) -> Dict[str, Any]:
        cursor = conn.cursor()
        aid = f"asgn_{uuid.uuid4().hex[:8]}"
        cursor.execute(
            """
            INSERT INTO assignments (id, user_id, title, subject, due_date, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, 'not_started')
            """,
            (aid, user_id, asgn_in.title, asgn_in.subject or "", asgn_in.due_date or "", asgn_in.priority or "medium")
        )
        conn.commit()
        return {"id": aid, "user_id": user_id, "title": asgn_in.title, "subject": asgn_in.subject or "", "due_date": asgn_in.due_date or "", "priority": asgn_in.priority or "medium", "status": "not_started"}

    # ── NOTES ──
    @staticmethod
    def get_notes(conn, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes ORDER BY created_at DESC")
        return [dict(r) for r in cursor.fetchall()]

    @staticmethod
    def create_note(conn, note_in: NoteCreate, user_id: Optional[str] = None) -> Dict[str, Any]:
        cursor = conn.cursor()
        nid = f"note_{uuid.uuid4().hex[:8]}"
        created_at = datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO notes (id, user_id, title, content, subject, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (nid, user_id, note_in.title, note_in.content or "", note_in.subject or "General", created_at)
        )
        conn.commit()
        return {"id": nid, "user_id": user_id, "title": note_in.title, "content": note_in.content or "", "subject": note_in.subject or "General", "created_at": created_at}
