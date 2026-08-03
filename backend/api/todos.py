"""
To-Do Tasks API Router
"""

from backend.database import get_db
from backend.models.todo import TodoCreate
from backend.services.todo_service import TodoService


def get_todos(conn=None):
    if conn is None:
        conn = next(get_db())
    return TodoService.get_user_todos(conn)


def create_todo(todo_data: dict, conn=None):
    if conn is None:
        conn = next(get_db())
    todo_in = TodoCreate(**todo_data)
    return TodoService.create_todo(conn, todo_in)


def toggle_todo(todo_id: str, conn=None):
    if conn is None:
        conn = next(get_db())
    return TodoService.toggle_todo_status(conn, todo_id)


def delete_todo(todo_id: str, conn=None):
    if conn is None:
        conn = next(get_db())
    return TodoService.delete_todo(conn, todo_id)
