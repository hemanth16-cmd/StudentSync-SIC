"""
Database & Local Persistence Layer for StudentSync (Python Flet)
Routes all operations through SQLAlchemy repositories (SQLite backend).
"""


from authentication.auth_service import AuthService
from authentication.session import Session

import json
import os

import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from app.db import SessionLocal, Base, engine
from app.repositories import (
    UserRepository, NoteRepository, TodoRepository, SubjectRepository,
    AssignmentRepository, ExpenseRepository, HabitRepository,
    NotificationRepository, EventRepository, ResultRepository, FeeRepository,
    DietRepository, WaterRepository
)

def _get_user_id() -> str:
    user = AuthService.current_user()
    return user.uid if user else "anonymous"

def _obj_to_dict(obj) -> Dict[str, Any]:
    """Convert a SQLAlchemy ORM row to a plain dict."""
    if obj is None:
        return {}
    d = {}
    for c in obj.__table__.columns:
        v = getattr(obj, c.name)
        if isinstance(v, datetime):
            d[c.name] = v.isoformat()
        elif isinstance(v, date):
            d[c.name] = v.isoformat()
        else:
            d[c.name] = v
    return d


DB_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "studentsync_data.json")

class Database:
    _data: Dict[str, Any] = {}

    @classmethod
    def _init_defaults(cls):
        cls._data = {
            "visited": False,
            "settings": {
                "name": "Student",
                "college": "",
                "theme": "dark",
                "accentColor": "#2563EB",
                "gpaScale": 10,
                "semesterStart": "",
                "dailyGoalHours": 6,
                "calorieGoal": 2000,
                "sleepGoal": 8,
                "budgetMonthly": 5000,
            },
            "todos": [],
            "subjects": [],
            "assignments": [],
            "notes": [],
            "attendance": {},
            "habits": [],
            "planner": [],
            "sleep": [],
            "diet": [],
            "workouts": [],
            "expenses": [],
            "streak": {"count": 0, "lastDate": ""},
            "daily_goals": [],
            "tasks": [],
            "study_sessions": [],
        }
        cls.save()

    @classmethod
    def save(cls):
        """Save locally."""
        try:
            with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(cls._data, f, indent=2)
        except Exception as e:
            print(f"Error saving local database: {e}")


    @classmethod
    def load(cls):
        """Ensure SQLite tables exist and legacy JSON cache is initialized."""
        import app.models  # noqa: F401 — register ORM models with Base.metadata
        Base.metadata.create_all(bind=engine)
        if cls._data:
            return
        if os.path.exists(DB_FILE_PATH):
            try:
                with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
                    cls._data = json.load(f)
            except Exception as e:
                print(f"Error loading local database: {e}")
                cls._init_defaults()
        else:
            cls._init_defaults()

    @staticmethod
    def today_str() -> str:
        return date.today().isoformat()

    @staticmethod
    def gen_id() -> str:
        return f"_{uuid.uuid4().hex[:9]}_{int(datetime.now().timestamp())}"

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        if key == "visited":
            return True
        return default

    # ── Settings ──────────────────────────────────────────────────────────
    @classmethod
    def get_settings(cls) -> Dict[str, Any]:
        return {
            "name": "Student",
            "theme": "dark",
            "budgetMonthly": 5000,
            "savings_goal": 2000,
            "currency": "₹",
            "gpaScale": 10,
            "dailyGoalHours": 6,
            "calorieGoal": 2000,
            "sleepGoal": 8,
        }

    @classmethod
    def update_settings(cls, updates: Dict[str, Any]):
        pass  # Settings repo can be added later; non-critical for now.

    # ── Streak ────────────────────────────────────────────────────────────
    @classmethod
    def get_streak(cls) -> int:
        return 1  # Simple stub; real streak via StreakRepository is a future enhancement.

    # ── Todos ─────────────────────────────────────────────────────────────
    @classmethod
    def get_todos(cls) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            return [_obj_to_dict(t) for t in TodoRepository(db, _get_user_id()).get_all()]
        finally:
            db.close()

    @classmethod
    def add_todo(cls, title: str, description: str = "", subject: str = "",
                 priority: str = "medium", due_date: str = "",
                 tags: Optional[List[str]] = None) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            t = TodoRepository(db, _get_user_id()).add(
                title, description, subject, priority, due_date,
                tags=",".join(tags) if tags else ""
            )
            return _obj_to_dict(t)
        finally:
            db.close()

    @classmethod
    def update_todo(cls, todo_id: str, updates: Dict[str, Any]):
        db = SessionLocal()
        try:
            TodoRepository(db, _get_user_id()).update(todo_id, updates)
        finally:
            db.close()

    @classmethod
    def delete_todo(cls, todo_id: str):
        db = SessionLocal()
        try:
            TodoRepository(db, _get_user_id()).delete(todo_id)
        finally:
            db.close()

    @classmethod
    def toggle_todo(cls, todo_id: str) -> Optional[Dict[str, Any]]:
        db = SessionLocal()
        try:
            return _obj_to_dict(TodoRepository(db, _get_user_id()).toggle(todo_id))
        finally:
            db.close()

    # ── Subjects ──────────────────────────────────────────────────────────
    @classmethod
    def get_subjects(cls) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            return [_obj_to_dict(s) for s in SubjectRepository(db, _get_user_id()).get_all()]
        finally:
            db.close()

    @classmethod
    def add_subject(cls, name: str, code: str = "", teacher: str = "",
                    credits: int = 3, room: str = "", color: str = "#2563EB",
                    emoji: str = "📚") -> Dict[str, Any]:
        db = SessionLocal()
        try:
            s = SubjectRepository(db, _get_user_id()).add(name, code, teacher, credits, room, color, emoji)
            return _obj_to_dict(s)
        finally:
            db.close()

    @classmethod
    def delete_subject(cls, sub_id: str):
        db = SessionLocal()
        try:
            SubjectRepository(db, _get_user_id()).delete(sub_id)
        finally:
            db.close()

    # ── Attendance ────────────────────────────────────────────────────────
    @classmethod
    def get_attendance(cls) -> Dict[str, Any]:
        """Return attendance as {subject_id: {date: status}} for the current user."""
        from app.models import Attendance
        db = SessionLocal()
        try:
            rows = db.query(Attendance).filter(Attendance.user_id == _get_user_id()).all()
            result: Dict[str, Dict[str, str]] = {}
            for row in rows:
                if row.subject_id not in result:
                    result[row.subject_id] = {}
                result[row.subject_id][row.date] = row.status
            return result
        finally:
            db.close()

    @classmethod
    def mark_attendance(cls, subject_id: str, date_str: str, status: str):
        from app.models import Attendance
        db = SessionLocal()
        try:
            uid = _get_user_id()
            existing = db.query(Attendance).filter(
                Attendance.user_id == uid,
                Attendance.subject_id == subject_id,
                Attendance.date == date_str
            ).first()
            if existing:
                existing.status = status
            else:
                db.add(Attendance(user_id=uid, subject_id=subject_id, date=date_str, status=status))
            db.commit()

            # Update subject attended/bunked counts
            subjects = db.query(__import__('app.models', fromlist=['Subject']).Subject).filter_by(id=subject_id).all()
            for s in subjects:
                att_rows = db.query(Attendance).filter(Attendance.subject_id == subject_id, Attendance.user_id == uid).all()
                s.attended = sum(1 for r in att_rows if r.status in ("present", "late"))
                s.bunked   = sum(1 for r in att_rows if r.status == "absent")
            db.commit()
        finally:
            db.close()

    # ── Assignments ───────────────────────────────────────────────────────
    @classmethod
    def get_assignments(cls) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            return [_obj_to_dict(a) for a in AssignmentRepository(db, _get_user_id()).get_all()]
        finally:
            db.close()

    @classmethod
    def add_assignment(cls, title: str, subject: str = "", due_date: str = "",
                       priority: str = "medium", description: str = "") -> Dict[str, Any]:
        db = SessionLocal()
        try:
            a = AssignmentRepository(db, _get_user_id()).add(title, subject, due_date, priority, description)
            return _obj_to_dict(a)
        finally:
            db.close()

    @classmethod
    def delete_assignment(cls, asgn_id: str):
        db = SessionLocal()
        try:
            AssignmentRepository(db, _get_user_id()).delete(asgn_id)
        finally:
            db.close()

    # ── Notes ─────────────────────────────────────────────────────────────
    @classmethod
    def get_notes(cls) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            return [_obj_to_dict(n) for n in NoteRepository(db, _get_user_id()).get_all()]
        finally:
            db.close()

    @classmethod
    def add_note(cls, title: str, content: str = "", subject: str = "",
                 tags: Optional[List[str]] = None, color: str = "") -> Dict[str, Any]:
        db = SessionLocal()
        try:
            n = NoteRepository(db, _get_user_id()).add(
                title, content, subject,
                tags=",".join(tags) if tags else "", color=color
            )
            return _obj_to_dict(n)
        finally:
            db.close()

    @classmethod
    def delete_note(cls, note_id: str):
        db = SessionLocal()
        try:
            NoteRepository(db, _get_user_id()).delete(note_id)
        finally:
            db.close()

    # ── Habits ────────────────────────────────────────────────────────────
    @classmethod
    def get_habits(cls) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            repo = HabitRepository(db, _get_user_id())
            habits = repo.get_all()
            result = []
            for h in habits:
                d = _obj_to_dict(h)
                completions = repo.get_completions(h.id)
                d["completions"] = completions
                result.append(d)
            return result
        finally:
            db.close()

    @classmethod
    def add_habit(cls, name: str, icon: str = "⭐", color: str = "#2563EB",
                  target: str = "daily") -> Dict[str, Any]:
        db = SessionLocal()
        try:
            h = HabitRepository(db, _get_user_id()).add(name, icon, color, target)
            return _obj_to_dict(h)
        finally:
            db.close()

    @classmethod
    def update_habit(cls, habit_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        db = SessionLocal()
        try:
            h = HabitRepository(db, _get_user_id()).update(habit_id, updates)
            return _obj_to_dict(h) if h else None
        finally:
            db.close()

    @classmethod
    def delete_habit(cls, habit_id: str):
        db = SessionLocal()
        try:
            HabitRepository(db, _get_user_id()).delete(habit_id)
        finally:
            db.close()

    @classmethod
    def toggle_habit(cls, habit_id: str, date_str: str) -> Optional[Dict[str, Any]]:
        db = SessionLocal()
        try:
            h = HabitRepository(db, _get_user_id()).toggle(habit_id, date_str)
            return _obj_to_dict(h) if h else None
        finally:
            db.close()

    # ── Sleep ─────────────────────────────────────────────────────────────
    # ── Sleep ─────────────────────────────────────────────────────────────
    @classmethod
    def get_sleep_logs(cls) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            from sqlalchemy import text
            # Fetch logs ordered by newest first
            result = db.execute(text("SELECT * FROM sleep_logs ORDER BY date DESC")).mappings().all()
            return [dict(row) for row in result]
        except Exception:
            return []  # Return empty if table doesn't exist yet
        finally:
            db.close()

    @classmethod
    def add_sleep_log(cls, duration: float, quality: int = 3, bedtime: str = "",
                      wake_time: str = "", date_str: str = "") -> Dict[str, Any]:
        if not date_str:
            date_str = Database.today_str()
        log_id = str(uuid.uuid4())
        
        db = SessionLocal()
        try:
            from sqlalchemy import text
            # Ensure the table exists dynamically
            db.execute(text('''
                CREATE TABLE IF NOT EXISTS sleep_logs (
                    id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    duration REAL NOT NULL,
                    quality INTEGER NOT NULL,
                    bedtime TEXT,
                    wake_time TEXT
                )
            '''))
            # Insert the new log
            db.execute(text('''
                INSERT INTO sleep_logs (id, date, duration, quality, bedtime, wake_time)
                VALUES (:id, :date, :duration, :quality, :bedtime, :wake_time)
            '''), {
                "id": log_id, "date": date_str, "duration": duration,
                "quality": quality, "bedtime": bedtime, "wake_time": wake_time
            })
            db.commit()
            return {
                "id": log_id, "date": date_str, "duration": duration, 
                "quality": quality, "bedtime": bedtime, "wake_time": wake_time
            }
        finally:
            db.close()

    @classmethod
    def delete_sleep_log(cls, log_id: str):
        db = SessionLocal()
        try:
            from sqlalchemy import text
            db.execute(text("DELETE FROM sleep_logs WHERE id = :id"), {"id": log_id})
            db.commit()
        finally:
            db.close()


    # ── Workout ───────────────────────────────────────────────────────────
    
    @classmethod
    def get_workouts(cls):
        db = SessionLocal()
        try:
            from sqlalchemy import text
            db.execute(text('''
                CREATE TABLE IF NOT EXISTS workouts (
                    id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    name TEXT NOT NULL,
                    workout_type TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    calories INTEGER NOT NULL
                )
            '''))
            db.commit()
            
            result = db.execute(text("SELECT id, date, name, workout_type, duration, calories FROM workouts ORDER BY date DESC"))
            rows = result.fetchall()
            return [
                {
                    "id": row[0],
                    "date": row[1],
                    "name": row[2],
                    "workout_type": row[3],
                    "duration": row[4],
                    "calories": row[5]
                }
                for row in rows
            ]
        finally:
            db.close()

    
    @classmethod
    def add_workout(cls, name: str, workout_type: str = "strength", duration: int = 30, calories: int = 200, date_str: str = ""):
        import uuid
        if not date_str:
            date_str = Database.today_str()
        workout_id = str(uuid.uuid4())
        
        db = SessionLocal()
        try:
            from sqlalchemy import text
            db.execute(text('''
                CREATE TABLE IF NOT EXISTS workouts (
                    id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    name TEXT NOT NULL,
                    workout_type TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    calories INTEGER NOT NULL
                )
            '''))
            db.execute(text('''
                INSERT INTO workouts (id, date, name, workout_type, duration, calories)
                VALUES (:id, :date, :name, :type, :duration, :calories)
            '''), {
                "id": workout_id, "date": date_str, "name": name, 
                "type": workout_type, "duration": duration, "calories": calories
            })
            db.commit()
        finally:
            db.close() 

    @classmethod
    def delete_workout(cls, log_id: str):
        db = SessionLocal()
        try:
            from sqlalchemy import text
            db.execute(text("DELETE FROM workouts WHERE id = :id"), {"id": log_id})
            db.commit()
        finally:
            db.close()
        
    # ── Diet ──────────────────────────────────────────────────────────────
    @classmethod
    def get_diet_logs(cls) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            return [_obj_to_dict(d) for d in DietRepository(db, _get_user_id()).get_all()]
        finally:
            db.close()

    @classmethod
    def get_diet_logs_by_date(cls, date_str: str) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            return [_obj_to_dict(d) for d in DietRepository(db, _get_user_id()).get_by_date(date_str)]
        finally:
            db.close()

    @classmethod
    def add_diet_entry(cls, name: str, calories: int, meal: str = "breakfast",
                       date_str: str = "", protein: float = 0, carbs: float = 0, fat: float = 0) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            log = DietRepository(db, _get_user_id()).add(name, calories, meal, date_str, protein, carbs, fat)
            return _obj_to_dict(log)
        finally:
            db.close()

    @classmethod
    def update_diet_entry(cls, log_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        db = SessionLocal()
        try:
            log = DietRepository(db, _get_user_id()).update(log_id, updates)
            return _obj_to_dict(log) if log else None
        finally:
            db.close()

    @classmethod
    def delete_diet_entry(cls, log_id: str):
        db = SessionLocal()
        try:
            DietRepository(db, _get_user_id()).delete(log_id)
        finally:
            db.close()

    # ── Water ─────────────────────────────────────────────────────────────
    @classmethod
    def get_water_intake(cls, date_str: str = "") -> int:
        db = SessionLocal()
        try:
            if not date_str:
                date_str = date.today().isoformat()
            return WaterRepository(db, _get_user_id()).get_water(date_str)
        finally:
            db.close()

    @classmethod
    def add_water_intake(cls, amount: int, date_str: str = "") -> int:
        db = SessionLocal()
        try:
            if not date_str:
                date_str = date.today().isoformat()
            return WaterRepository(db, _get_user_id()).add_water(date_str, amount)
        finally:
            db.close()



    # ── Workout ───────────────────────────────────────────────────────────

    # ── Planner ───────────────────────────────────────────────────────────
    @classmethod
    def get_planner_events(cls) -> List[Dict[str, Any]]:
        from app.models import PlannerEvent
        db = SessionLocal()
        try:
            rows = db.query(PlannerEvent).filter(PlannerEvent.user_id == _get_user_id()).all()
            return [_obj_to_dict(r) for r in rows]
        finally:
            db.close()

    @classmethod
    def add_planner_event(cls, title: str, day: int, start_time: str, end_time: str,
                          event_type: str = "class", color: str = "#2563EB") -> Dict[str, Any]:
        from app.models import PlannerEvent
        db = SessionLocal()
        try:
            ev = PlannerEvent(user_id=_get_user_id(), title=title, day=day,
                              start_time=start_time, end_time=end_time,
                              event_type=event_type, color=color)
            db.add(ev)
            db.commit()
            db.refresh(ev)
            return _obj_to_dict(ev)
        finally:
            db.close()

    @classmethod
    def delete_planner_event(cls, event_id: str):
        from app.models import PlannerEvent
        db = SessionLocal()
        try:
            ev = db.query(PlannerEvent).filter(PlannerEvent.id == event_id).first()
            if ev:
                db.delete(ev)
                db.commit()
        finally:
            db.close()
