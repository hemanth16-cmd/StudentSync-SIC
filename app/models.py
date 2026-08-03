import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, Float, ForeignKey, DateTime, Text, Date
from sqlalchemy.orm import relationship
from app.db import Base

def gen_uuid():
    return uuid.uuid4().hex

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="student")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships can be added here if needed

class Setting(Base):
    __tablename__ = "settings"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

class Todo(Base):
    __tablename__ = "todos"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    subject = Column(String, default="")
    priority = Column(String, default="medium")
    due_date = Column(String, default="")
    completed = Column(Boolean, default=False)
    pinned = Column(Boolean, default=False)
    tags = Column(String, default="") # comma separated
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    code = Column(String, default="")
    teacher = Column(String, default="")
    credits = Column(Integer, default=3)
    total_classes = Column(Integer, default=45)
    attended = Column(Integer, default=0)
    bunked = Column(Integer, default=0)
    room = Column(String, default="")
    color = Column(String, default="#2563EB")
    emoji = Column(String, default="📚")
    grade = Column(String, default="")
    max_grade = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    subject = Column(String, default="")
    due_date = Column(String, default="")
    priority = Column(String, default="medium")
    status = Column(String, default="not_started")
    progress = Column(Integer, default=0)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class Note(Base):
    __tablename__ = "notes"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    content = Column(Text, default="")
    subject = Column(String, default="")
    tags = Column(String, default="")
    color = Column(String, default="")
    pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    subject_id = Column(String, ForeignKey("subjects.id"))
    date = Column(String, nullable=False) # ISO string
    status = Column(String, default="present") # present, absent, late

class Habit(Base):
    __tablename__ = "habits"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    icon = Column(String, default="⭐")
    color = Column(String, default="#2563EB")
    target = Column(String, default="daily")
    streak = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class HabitCompletion(Base):
    __tablename__ = "habit_completions"
    id = Column(String, primary_key=True, default=gen_uuid)
    habit_id = Column(String, ForeignKey("habits.id"))
    date = Column(String, nullable=False) # ISO string
    completed = Column(Boolean, default=False)

class PlannerEvent(Base):
    __tablename__ = "planner_events"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    day = Column(Integer, default=0) # 0 = Monday, etc.
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    event_type = Column(String, default="class")
    color = Column(String, default="#2563EB")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, default="")
    date = Column(String, nullable=False) # ISO String
    type = Column(String, default="expense") # expense, income
    recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Streak(Base):
    __tablename__ = "streaks"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    count = Column(Integer, default=0)
    last_date = Column(String, default="")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    message = Column(Text, default="")
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    date = Column(String, nullable=False)
    location = Column(String, default="")
    description = Column(Text, default="")

class Result(Base):
    __tablename__ = "results"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    subject = Column(String, nullable=False)
    semester = Column(String, default="")
    grade = Column(String, nullable=False)
    score = Column(Float, default=0.0)
    max_score = Column(Float, default=100.0)

class Fee(Base):
    __tablename__ = "fees"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(String, nullable=False)
    status = Column(String, default="pending") # pending, paid

class DietLog(Base):
    __tablename__ = "diet_logs"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    calories = Column(Integer, nullable=False)
    meal = Column(String, default="breakfast")
    date = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


