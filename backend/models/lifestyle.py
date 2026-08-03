"""
Lifestyle Schemas (Habits, Diet, Workout, Sleep)
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class HabitCreate:
    name: str
    icon: Optional[str] = "⭐"


@dataclass
class DietCreate:
    name: str
    calories: int
    meal: Optional[str] = "breakfast"


@dataclass
class WorkoutCreate:
    name: str
    duration: int
    type: Optional[str] = "strength"
    calories: Optional[int] = 0


@dataclass
class SleepCreate:
    duration: float
    quality: Optional[int] = 3
    bedtime: Optional[str] = ""
    wake_time: Optional[str] = ""
