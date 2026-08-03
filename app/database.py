"""
Database & Local Persistence Layer for StudentSync (Python Flet)
Replaces localStorage (store.js) with local JSON storage backend.
"""
from authentication.auth_service import AuthService
from authentication.firebase_auth import get_db

import json
import os
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional

DB_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "studentsync_data.json")

class Database:
    _data: Dict[str, Any] = {}
    @classmethod
    def load(cls):
        """Load the current user's data from Firestore."""

        user = AuthService.current_user()

        # No logged-in user -> keep old local behavior
        if user is None:
            if os.path.exists(DB_FILE_PATH):
                try:
                    with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
                        cls._data = json.load(f)
                except Exception as e:
                    print(f"Error loading local database: {e}")
                    cls._init_defaults()
            else:
                cls._init_defaults()
            return

        # Logged in -> load from Firestore
        try:
            db = get_db()

            doc = (
                db.collection("users")
                .document(user.uid)
                .collection("appData")
                .document("database")
                .get()
            )

            if doc.exists:
                cls._data = doc.to_dict()
                print(f"[DATABASE] Loaded cloud data for {user.email}")
            else:
                print("[DATABASE] No cloud data found. Initializing defaults.")
                cls._init_defaults()

        except Exception as e:
            print(f"[DATABASE] Failed to load cloud data: {e}")
            cls._init_defaults()
            
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
            "daily_goals": []
        }
        cls.save()

    @classmethod
    def save(cls):
        """Save to Firestore if logged in, otherwise save locally."""

        user = AuthService.current_user()

        if user is None:
            try:
                with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
                    json.dump(cls._data, f, indent=2)
            except Exception as e:
                print(f"Error saving local database: {e}")
            return

        try:
            db = get_db()

            (
                db.collection("users")
                .document(user.uid)
                .collection("appData")
                .document("database")
                .set(cls._data)
            )

            print(f"[DATABASE] Saved cloud data for {user.email}")

        except Exception as e:
            print(f"[DATABASE] Failed to save cloud data: {e}")
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        return cls._data.get(key, default)

    @classmethod
    def set(cls, key: str, value: Any):
        cls._data[key] = value
        cls.save()

    @staticmethod
    def gen_id() -> str:
        return f"_{uuid.uuid4().hex[:9]}_{int(datetime.now().timestamp())}"

    @staticmethod
    def today_str() -> str:
        return date.today().isoformat()

    # ── SETTINGS ──
    @classmethod
    def get_settings(cls) -> Dict[str, Any]:
        return cls.get("settings", {})

    @classmethod
    def update_settings(cls, updates: Dict[str, Any]):
        settings = cls.get_settings()
        settings.update(updates)
        cls.set("settings", settings)

    # ── TODOS ──
    @classmethod
    def get_todos(cls) -> List[Dict[str, Any]]:
        return cls.get("todos", [])

    @classmethod
    def add_todo(cls, title: str, description: str = "", subject: str = "", priority: str = "medium", due_date: str = "", tags: Optional[List[str]] = None) -> Dict[str, Any]:
        todos = cls.get_todos()
        new_todo = {
            "id": cls.gen_id(),
            "title": title,
            "description": description,
            "subject": subject,
            "priority": priority,
            "dueDate": due_date,
            "completed": False,
            "pinned": False,
            "createdAt": datetime.now().isoformat(),
            "completedAt": None,
            "tags": tags or []
        }
        todos.insert(0, new_todo)
        cls.set("todos", todos)
        return new_todo

    @classmethod
    def update_todo(cls, todo_id: str, updates: Dict[str, Any]):
        todos = cls.get_todos()
        for t in todos:
            if t["id"] == todo_id:
                t.update(updates)
                break
        cls.set("todos", todos)

    @classmethod
    def delete_todo(cls, todo_id: str):
        todos = [t for t in cls.get_todos() if t["id"] != todo_id]
        cls.set("todos", todos)

    @classmethod
    def toggle_todo(cls, todo_id: str) -> Optional[Dict[str, Any]]:
        todos = cls.get_todos()
        target = None
        for t in todos:
            if t["id"] == todo_id:
                t["completed"] = not t["completed"]
                t["completedAt"] = datetime.now().isoformat() if t["completed"] else None
                target = t
                break
        cls.set("todos", todos)
        return target

    # ── SUBJECTS ──
    @classmethod
    def get_subjects(cls) -> List[Dict[str, Any]]:
        return cls.get("subjects", [])

    @classmethod
    def add_subject(cls, name: str, code: str = "", teacher: str = "", credits: int = 3, room: str = "", color: str = "#2563EB", emoji: str = "📚") -> Dict[str, Any]:
        subjects = cls.get_subjects()
        new_sub = {
            "id": cls.gen_id(),
            "name": name,
            "code": code,
            "teacher": teacher,
            "credits": credits,
            "totalClasses": credits * 15,
            "attended": 0,
            "bunked": 0,
            "room": room,
            "color": color,
            "emoji": emoji,
            "grade": "",
            "maxGrade": 100,
            "createdAt": datetime.now().isoformat()
        }
        subjects.append(new_sub)
        cls.set("subjects", subjects)
        return new_sub

    @classmethod
    def delete_subject(cls, sub_id: str):
        subjects = [s for s in cls.get_subjects() if s["id"] != sub_id]
        cls.set("subjects", subjects)

    # ── ASSIGNMENTS ──
    @classmethod
    def get_assignments(cls) -> List[Dict[str, Any]]:
        return cls.get("assignments", [])

    @classmethod
    def add_assignment(cls, title: str, subject: str = "", due_date: str = "", priority: str = "medium", description: str = "") -> Dict[str, Any]:
        items = cls.get_assignments()
        new_item = {
            "id": cls.gen_id(),
            "title": title,
            "subject": subject,
            "dueDate": due_date,
            "priority": priority,
            "status": "not_started",
            "progress": 0,
            "description": description,
            "createdAt": datetime.now().isoformat()
        }
        items.insert(0, new_item)
        cls.set("assignments", items)
        return new_item

    @classmethod
    def delete_assignment(cls, asgn_id: str):
        items = [a for a in cls.get_assignments() if a["id"] != asgn_id]
        cls.set("assignments", items)

    # ── NOTES ──
    @classmethod
    def get_notes(cls) -> List[Dict[str, Any]]:
        return cls.get("notes", [])

    @classmethod
    def add_note(cls, title: str, content: str = "", subject: str = "", tags: Optional[List[str]] = None, color: str = "") -> Dict[str, Any]:
        notes = cls.get_notes()
        new_note = {
            "id": cls.gen_id(),
            "title": title or "Untitled Note",
            "content": content,
            "subject": subject,
            "tags": tags or [],
            "color": color,
            "pinned": False,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat()
        }
        notes.insert(0, new_note)
        cls.set("notes", notes)
        return new_note

    @classmethod
    def delete_note(cls, note_id: str):
        notes = [n for n in cls.get_notes() if n["id"] != note_id]
        cls.set("notes", notes)

    # ── ATTENDANCE ──
    @classmethod
    def get_attendance(cls) -> Dict[str, Any]:
        return cls.get("attendance", {})

    @classmethod
    def mark_attendance(cls, subject_id: str, date_str: str, status: str):
        att = cls.get_attendance()
        if subject_id not in att:
            att[subject_id] = {}
        att[subject_id][date_str] = status  # 'present', 'absent', 'late'
        cls.set("attendance", att)

        # Update subject stats
        subjects = cls.get_subjects()
        for s in subjects:
            if s["id"] == subject_id:
                log_vals = list(att[subject_id].values())
                s["attended"] = sum(1 for v in log_vals if v in ["present", "late"])
                s["bunked"] = sum(1 for v in log_vals if v == "absent")
                break
        cls.set("subjects", subjects)

    # ── HABITS ──
    @classmethod
    def get_habits(cls) -> List[Dict[str, Any]]:
        return cls.get("habits", [])

    @classmethod
    def add_habit(cls, name: str, icon: str = "⭐", color: str = "#2563EB", target: str = "daily") -> Dict[str, Any]:
        habits = cls.get_habits()
        new_h = {
            "id": cls.gen_id(),
            "name": name,
            "icon": icon,
            "color": color,
            "target": target,
            "completions": {},
            "streak": 0,
            "createdAt": datetime.now().isoformat()
        }
        habits.append(new_h)
        cls.set("habits", habits)
        return new_h

    @classmethod
    def toggle_habit(cls, habit_id: str, date_str: str) -> Optional[Dict[str, Any]]:
        habits = cls.get_habits()
        target = None
        for h in habits:
            if h["id"] == habit_id:
                curr = h.get("completions", {}).get(date_str, False)
                h["completions"][date_str] = not curr
                # Recalculate streak
                streak = 0
                d = date.today()
                while True:
                    ds = d.isoformat()
                    if h["completions"].get(ds):
                        streak += 1
                        d -= timedelta(days=1)
                    else:
                        break
                h["streak"] = streak
                target = h
                break
        cls.set("habits", habits)
        return target

    # ── PLANNER ──
    @classmethod
    def get_planner_events(cls) -> List[Dict[str, Any]]:
        return cls.get("planner", [])

    @classmethod
    def add_planner_event(cls, title: str, day: int, start_time: str, end_time: str, event_type: str = "class", color: str = "#2563EB") -> Dict[str, Any]:
        events = cls.get_planner_events()
        new_ev = {
            "id": cls.gen_id(),
            "title": title,
            "day": day,
            "startTime": start_time,
            "endTime": end_time,
            "type": event_type,
            "color": color
        }
        events.append(new_ev)
        cls.set("planner", events)
        return new_ev

    @classmethod
    def delete_planner_event(cls, event_id: str):
        events = [e for e in cls.get_planner_events() if e["id"] != event_id]
        cls.set("planner", events)

    # ── SLEEP ──
    @classmethod
    def get_sleep_logs(cls) -> List[Dict[str, Any]]:
        return cls.get("sleep", [])

    @classmethod
    def add_sleep_log(cls, duration: float, quality: int = 3, bedtime: str = "", wake_time: str = "", date_str: str = "") -> Dict[str, Any]:
        logs = cls.get_sleep_logs()
        new_log = {
            "id": cls.gen_id(),
            "date": date_str or cls.today_str(),
            "bedtime": bedtime,
            "wakeTime": wake_time,
            "duration": duration,
            "quality": quality,
        }
        logs.insert(0, new_log)
        cls.set("sleep", logs)
        return new_log

    # ── DIET ──
    @classmethod
    def get_diet_logs(cls) -> List[Dict[str, Any]]:
        return cls.get("diet", [])

    @classmethod
    def add_diet_entry(cls, name: str, calories: int, meal: str = "breakfast", protein: float = 0, carbs: float = 0, fat: float = 0) -> Dict[str, Any]:
        logs = cls.get_diet_logs()
        new_entry = {
            "id": cls.gen_id(),
            "date": cls.today_str(),
            "meal": meal,
            "name": name,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        }
        logs.insert(0, new_entry)
        cls.set("diet", logs)
        return new_entry

    # ── WORKOUT ──
    @classmethod
    def get_workouts(cls) -> List[Dict[str, Any]]:
        return cls.get("workouts", [])

    @classmethod
    def add_workout(cls, name: str, workout_type: str = "strength", duration: int = 30, calories: int = 200) -> Dict[str, Any]:
        workouts = cls.get_workouts()
        new_w = {
            "id": cls.gen_id(),
            "date": cls.today_str(),
            "type": workout_type,
            "name": name,
            "duration": duration,
            "calories": calories
        }
        workouts.insert(0, new_w)
        cls.set("workouts", workouts)
        return new_w

    # ── STREAK ──
    @classmethod
    def get_streak(cls) -> int:
        """Returns the current login streak count."""
        streak_data = cls.get("streak", {"count": 0, "lastDate": ""})
        today = cls.today_str()
        last  = streak_data.get("lastDate", "")

        if last == today:
            return streak_data.get("count", 0)

        yesterday = (date.today() - timedelta(days=1)).isoformat()
        if last == yesterday:
            streak_data["count"] = streak_data.get("count", 0) + 1
        else:
            streak_data["count"] = 1
        streak_data["lastDate"] = today
        cls.set("streak", streak_data)
        return streak_data["count"]

# Initialize on module load
Database.load()
