"""
Lifestyle API Router (Habits, Diet, Workout, Sleep)
"""

from backend.database import get_db
from backend.models.lifestyle import HabitCreate, DietCreate, WorkoutCreate, SleepCreate
from backend.services.lifestyle_service import LifestyleService


def get_habits(conn=None):
    if conn is None: conn = next(get_db())
    return LifestyleService.get_habits(conn)


def create_habit(data: dict, conn=None):
    if conn is None: conn = next(get_db())
    return LifestyleService.create_habit(conn, HabitCreate(**data))


def get_diet(conn=None):
    if conn is None: conn = next(get_db())
    return LifestyleService.get_diet(conn)


def create_diet(data: dict, conn=None):
    if conn is None: conn = next(get_db())
    return LifestyleService.create_diet_entry(conn, DietCreate(**data))


def get_workouts(conn=None):
    if conn is None: conn = next(get_db())
    return LifestyleService.get_workouts(conn)


def create_workout(data: dict, conn=None):
    if conn is None: conn = next(get_db())
    return LifestyleService.create_workout(conn, WorkoutCreate(**data))


def get_sleep(conn=None):
    if conn is None: conn = next(get_db())
    return LifestyleService.get_sleep_logs(conn)


def create_sleep(data: dict, conn=None):
    if conn is None: conn = next(get_db())
    return LifestyleService.create_sleep_log(conn, SleepCreate(**data))
