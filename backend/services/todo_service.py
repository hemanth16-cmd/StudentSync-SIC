"""
To-Do Tasks Business Logic Service (SQLite connection layer)
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from backend.models.todo import TodoCreate


class TodoService:
    @staticmethod
    def get_user_todos(conn, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        if user_id:
            cursor.execute("SELECT * FROM todos WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        else:
            cursor.execute("SELECT * FROM todos ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def create_todo(conn, todo_in: TodoCreate, user_id: Optional[str] = None) -> Dict[str, Any]:
        cursor = conn.cursor()
        todo_id = f"todo_{uuid.uuid4().hex[:8]}"
        created_at = datetime.utcnow().isoformat()
        cursor.execute(
            """
            INSERT INTO todos (id, user_id, title, description, subject, priority, due_date, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (todo_id, user_id, todo_in.title, todo_in.description or "", todo_in.subject or "", todo_in.priority or "medium", todo_in.due_date or "", created_at)
        )
        conn.commit()
        return {
            "id": todo_id,
            "user_id": user_id,
            "title": todo_in.title,
            "description": todo_in.description or "",
            "subject": todo_in.subject or "",
            "priority": todo_in.priority or "medium",
            "due_date": todo_in.due_date or "",
            "completed": False,
            "created_at": created_at
        }

    @staticmethod
    def toggle_todo_status(conn, todo_id: str) -> Optional[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT completed FROM todos WHERE id = ?", (todo_id,))
        row = cursor.fetchone()
        if not row:
            return None
        new_status = not bool(row["completed"])
        cursor.execute("UPDATE todos SET completed = ? WHERE id = ?", (int(new_status), todo_id))
        conn.commit()

        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        return dict(cursor.fetchone())

    @staticmethod
    def delete_todo(conn, todo_id: str) -> bool:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
        return cursor.rowcount > 0
