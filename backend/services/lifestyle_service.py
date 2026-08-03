"""
Lifestyle Business Logic Service (Habits, Diet, Workout, Sleep)
"""

import uuid
from datetime import date
from typing import List, Optional, Dict, Any
from backend.models.lifestyle import HabitCreate, DietCreate, WorkoutCreate, SleepCreate


class LifestyleService:
    # ── HABITS ──
    @staticmethod
    def get_habits(conn, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM habits")
        return [dict(r) for r in cursor.fetchall()]

    @staticmethod
    def create_habit(conn, habit_in: HabitCreate, user_id: Optional[str] = None) -> Dict[str, Any]:
        cursor = conn.cursor()
        hid = f"hbt_{uuid.uuid4().hex[:8]}"
        cursor.execute("INSERT INTO habits (id, user_id, name, icon, streak) VALUES (?, ?, ?, ?, 0)", (hid, user_id, habit_in.name, habit_in.icon or "⭐"))
        conn.commit()
        return {"id": hid, "user_id": user_id, "name": habit_in.name, "icon": habit_in.icon or "⭐", "streak": 0}

    # ── DIET ──
    @staticmethod
    def get_diet(conn, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM diet")
        return [dict(r) for r in cursor.fetchall()]

    @staticmethod
    def create_diet_entry(conn, diet_in: DietCreate, user_id: Optional[str] = None) -> Dict[str, Any]:
        cursor = conn.cursor()
        did = f"diet_{uuid.uuid4().hex[:8]}"
        today = date.today().isoformat()
        cursor.execute("INSERT INTO diet (id, user_id, date, meal, name, calories) VALUES (?, ?, ?, ?, ?, ?)", (did, user_id, today, diet_in.meal or "breakfast", diet_in.name, diet_in.calories))
        conn.commit()
        return {"id": did, "user_id": user_id, "date": today, "meal": diet_in.meal or "breakfast", "name": diet_in.name, "calories": diet_in.calories}

    # ── WORKOUT ──
    @staticmethod
    def get_workouts(conn, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM workouts")
        return [dict(r) for r in cursor.fetchall()]

    @staticmethod
    def create_workout(conn, workout_in: WorkoutCreate, user_id: Optional[str] = None) -> Dict[str, Any]:
        cursor = conn.cursor()
        wid = f"wk_{uuid.uuid4().hex[:8]}"
        today = date.today().isoformat()
        cursor.execute("INSERT INTO workouts (id, user_id, date, name, type, duration, calories) VALUES (?, ?, ?, ?, ?, ?, ?)", (wid, user_id, today, workout_in.name, workout_in.type or "strength", workout_in.duration, workout_in.calories or 0))
        conn.commit()
        return {"id": wid, "user_id": user_id, "date": today, "name": workout_in.name, "type": workout_in.type or "strength", "duration": workout_in.duration, "calories": workout_in.calories or 0}

    # ── SLEEP ──
    @staticmethod
    def get_sleep_logs(conn, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sleep")
        return [dict(r) for r in cursor.fetchall()]

    @staticmethod
    def create_sleep_log(conn, sleep_in: SleepCreate, user_id: Optional[str] = None) -> Dict[str, Any]:
        cursor = conn.cursor()
        sid = f"slp_{uuid.uuid4().hex[:8]}"
        today = date.today().isoformat()
        cursor.execute("INSERT INTO sleep (id, user_id, date, duration, quality, bedtime, wake_time) VALUES (?, ?, ?, ?, ?, ?, ?)", (sid, user_id, today, sleep_in.duration, sleep_in.quality or 3, sleep_in.bedtime or "", sleep_in.wake_time or ""))
        conn.commit()
        return {"id": sid, "user_id": user_id, "date": today, "duration": sleep_in.duration, "quality": sleep_in.quality or 3, "bedtime": sleep_in.bedtime or "", "wake_time": sleep_in.wake_time or ""}
