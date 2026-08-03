"""
Analytics Business Logic Service (SQLite connection layer)
"""

from typing import Dict, Any, Optional
from backend.services.todo_service import TodoService
from backend.services.academic_service import AcademicService
from backend.services.lifestyle_service import LifestyleService


class AnalyticsService:
    @staticmethod
    def get_dashboard_summary(conn, user_id: Optional[str] = None) -> Dict[str, Any]:
        todos = TodoService.get_user_todos(conn, user_id)
        subjects = AcademicService.get_subjects(conn, user_id)
        habits = LifestyleService.get_habits(conn, user_id)
        sleep_logs = LifestyleService.get_sleep_logs(conn, user_id)

        completed_todos = sum(1 for t in todos if t.get("completed"))
        total_todos = len(todos)
        todo_rate = (completed_todos / total_todos * 100) if total_todos > 0 else 0.0

        avg_sleep = (sum(s.get("duration", 0) for s in sleep_logs) / len(sleep_logs)) if sleep_logs else 0.0

        score = int(
            (todo_rate * 0.4)
            + min(len(habits) * 8, 24)
            + min((avg_sleep / 8.0) * 20, 20)
            + min(len(subjects) * 4, 16)
        )
        productivity_index = min(score, 100)

        return {
            "productivity_score": productivity_index,
            "total_todos": total_todos,
            "completed_todos": completed_todos,
            "pending_todos": total_todos - completed_todos,
            "todo_completion_rate": round(todo_rate, 1),
            "active_subjects": len(subjects),
            "active_habits": len(habits),
            "avg_sleep_hours": round(avg_sleep, 1),
        }
