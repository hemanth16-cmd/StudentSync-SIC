from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Dict, Any
from app.models import (
    User, Todo, Subject, Assignment, Note, Attendance,
    Habit, HabitCompletion, PlannerEvent, Expense, Streak,
    Notification, Event, Result, Fee, DietLog
)
from datetime import datetime, date, timedelta


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, name: str, email: str, password_hash: str) -> User:
        user = User(name=name, email=email, password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class NoteRepository:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    def get_all(self) -> List[Note]:
        return self.db.query(Note).filter(Note.user_id == self.user_id).order_by(Note.created_at.desc()).all()

    def add(self, title: str, content: str = "", subject: str = "", tags: str = "", color: str = "") -> Note:
        n = Note(user_id=self.user_id, title=title, content=content, subject=subject, tags=tags, color=color)
        self.db.add(n)
        self.db.commit()
        self.db.refresh(n)
        return n

    def delete(self, note_id: str):
        n = self.db.query(Note).filter(Note.id == note_id, Note.user_id == self.user_id).first()
        if n:
            self.db.delete(n)
            self.db.commit()


class TodoRepository:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    def get_all(self) -> List[Todo]:
        return self.db.query(Todo).filter(Todo.user_id == self.user_id).order_by(Todo.created_at.desc()).all()

    def add(self, title: str, description: str = "", subject: str = "", priority: str = "medium", due_date: str = "", tags: str = "") -> Todo:
        t = Todo(user_id=self.user_id, title=title, description=description,
                 subject=subject, priority=priority, due_date=due_date, tags=tags)
        self.db.add(t)
        self.db.commit()
        self.db.refresh(t)
        return t

    def update(self, todo_id: str, updates: Dict[str, Any]):
        t = self.db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == self.user_id).first()
        if t:
            for k, v in updates.items():
                if hasattr(t, k):
                    setattr(t, k, v)
            self.db.commit()

    def delete(self, todo_id: str):
        t = self.db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == self.user_id).first()
        if t:
            self.db.delete(t)
            self.db.commit()

    def toggle(self, todo_id: str) -> Optional[Todo]:
        t = self.db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == self.user_id).first()
        if t:
            t.completed = not t.completed
            t.completed_at = datetime.utcnow() if t.completed else None
            self.db.commit()
            self.db.refresh(t)
        return t


class SubjectRepository:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    def get_all(self) -> List[Subject]:
        return self.db.query(Subject).filter(Subject.user_id == self.user_id).all()

    def add(self, name: str, code: str = "", teacher: str = "", credits: int = 3,
            room: str = "", color: str = "#2563EB", emoji: str = "📚") -> Subject:
        s = Subject(user_id=self.user_id, name=name, code=code, teacher=teacher,
                    credits=credits, total_classes=credits * 15, room=room, color=color, emoji=emoji)
        self.db.add(s)
        self.db.commit()
        self.db.refresh(s)
        return s

    def delete(self, subject_id: str):
        s = self.db.query(Subject).filter(Subject.id == subject_id, Subject.user_id == self.user_id).first()
        if s:
            self.db.delete(s)
            self.db.commit()


class AssignmentRepository:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    def get_all(self) -> List[Assignment]:
        return self.db.query(Assignment).filter(Assignment.user_id == self.user_id).order_by(Assignment.created_at.desc()).all()

    def add(self, title: str, subject: str = "", due_date: str = "", priority: str = "medium", description: str = "") -> Assignment:
        a = Assignment(user_id=self.user_id, title=title, subject=subject,
                       due_date=due_date, priority=priority, description=description)
        self.db.add(a)
        self.db.commit()
        self.db.refresh(a)
        return a

    def delete(self, asgn_id: str):
        a = self.db.query(Assignment).filter(Assignment.id == asgn_id, Assignment.user_id == self.user_id).first()
        if a:
            self.db.delete(a)
            self.db.commit()


class ExpenseRepository:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    def get_all(self) -> List[Expense]:
        return self.db.query(Expense).filter(Expense.user_id == self.user_id).order_by(Expense.created_at.desc()).all()

    def add(self, amount: float, category: str, description: str, date_str: str,
            exp_type: str = "expense", recurring: bool = False) -> Expense:
        e = Expense(user_id=self.user_id, amount=amount, category=category,
                    description=description, date=date_str, type=exp_type, recurring=recurring)
        self.db.add(e)
        self.db.commit()
        self.db.refresh(e)
        return e

    def update(self, exp_id: str, updates: Dict[str, Any]) -> Optional[Expense]:
        e = self.db.query(Expense).filter(Expense.id == exp_id, Expense.user_id == self.user_id).first()
        if e:
            for k, v in updates.items():
                if hasattr(e, k):
                    setattr(e, k, v)
            self.db.commit()
            self.db.refresh(e)
        return e

    def delete(self, exp_id: str):
        e = self.db.query(Expense).filter(Expense.id == exp_id, Expense.user_id == self.user_id).first()
        if e:
            self.db.delete(e)
            self.db.commit()


class HabitRepository:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    def get_all(self) -> List[Habit]:
        return self.db.query(Habit).filter(Habit.user_id == self.user_id).all()

    def add(self, name: str, icon: str = "⭐", color: str = "#2563EB", target: str = "daily") -> Habit:
        h = Habit(user_id=self.user_id, name=name, icon=icon, color=color, target=target)
        self.db.add(h)
        self.db.commit()
        self.db.refresh(h)
        return h

    def update(self, habit_id: str, updates: Dict[str, Any]) -> Optional[Habit]:
        h = self.db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == self.user_id).first()
        if h:
            for k, v in updates.items():
                if hasattr(h, k):
                    setattr(h, k, v)
            self.db.commit()
            self.db.refresh(h)
        return h

    def get_completions(self, habit_id: str) -> Dict[str, bool]:
        completions = self.db.query(HabitCompletion).filter(HabitCompletion.habit_id == habit_id).all()
        return {hc.date: hc.completed for hc in completions}

    def toggle(self, habit_id: str, date_str: str) -> Optional[Habit]:
        h = self.db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == self.user_id).first()
        if not h:
            return None
        hc = self.db.query(HabitCompletion).filter(
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.date == date_str
        ).first()
        if hc:
            hc.completed = not hc.completed
        else:
            hc = HabitCompletion(habit_id=habit_id, date=date_str, completed=True)
            self.db.add(hc)
        self.db.commit()
        # Recalculate streak
        streak = 0
        d = date.today()
        while True:
            ds = d.isoformat()
            completion = self.db.query(HabitCompletion).filter(
                HabitCompletion.habit_id == habit_id,
                HabitCompletion.date == ds,
                HabitCompletion.completed == True
            ).first()
            if completion:
                streak += 1
                d -= timedelta(days=1)
            else:
                break
        h.streak = streak
        self.db.commit()
        self.db.refresh(h)
        return h

    def delete(self, habit_id: str):
        h = self.db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == self.user_id).first()
        if h:
            self.db.query(HabitCompletion).filter(HabitCompletion.habit_id == habit_id).delete()
            self.db.delete(h)
            self.db.commit()


class DietRepository:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    def get_all(self) -> List[DietLog]:
        return self.db.query(DietLog).filter(DietLog.user_id == self.user_id).order_by(DietLog.created_at.desc()).all()

    def add(self, name: str, calories: int, meal: str = "breakfast", date_str: str = "") -> DietLog:
        if not date_str:
            date_str = date.today().isoformat()
        log = DietLog(user_id=self.user_id, name=name, calories=calories, meal=meal, date=date_str)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def update(self, log_id: str, updates: Dict[str, Any]) -> Optional[DietLog]:
        log = self.db.query(DietLog).filter(DietLog.id == log_id, DietLog.user_id == self.user_id).first()
        if log:
            for k, v in updates.items():
                if hasattr(log, k):
                    setattr(log, k, v)
            self.db.commit()
            self.db.refresh(log)
        return log

    def delete(self, log_id: str):
        log = self.db.query(DietLog).filter(DietLog.id == log_id, DietLog.user_id == self.user_id).first()
        if log:
            self.db.delete(log)
            self.db.commit()



class NotificationRepository:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    def get_all(self) -> List[Notification]:
        return self.db.query(Notification).filter(
            Notification.user_id == self.user_id
        ).order_by(Notification.created_at.desc()).all()

    def add(self, title: str, message: str = "") -> Notification:
        n = Notification(user_id=self.user_id, title=title, message=message)
        self.db.add(n)
        self.db.commit()
        self.db.refresh(n)
        return n

    def mark_read(self, notif_id: str):
        n = self.db.query(Notification).filter(
            Notification.id == notif_id, Notification.user_id == self.user_id
        ).first()
        if n:
            n.read = True
            self.db.commit()


class EventRepository:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    def get_all(self) -> List[Event]:
        return self.db.query(Event).filter(Event.user_id == self.user_id).order_by(Event.date).all()

    def add(self, title: str, event_date: str, location: str = "", description: str = "") -> Event:
        e = Event(user_id=self.user_id, title=title, date=event_date,
                  location=location, description=description)
        self.db.add(e)
        self.db.commit()
        self.db.refresh(e)
        return e

    def delete(self, event_id: str):
        e = self.db.query(Event).filter(Event.id == event_id, Event.user_id == self.user_id).first()
        if e:
            self.db.delete(e)
            self.db.commit()


class ResultRepository:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    def get_all(self) -> List[Result]:
        return self.db.query(Result).filter(Result.user_id == self.user_id).all()

    def add(self, subject: str, grade: str, semester: str = "",
            score: float = 0.0, max_score: float = 100.0) -> Result:
        r = Result(user_id=self.user_id, subject=subject, grade=grade,
                   semester=semester, score=score, max_score=max_score)
        self.db.add(r)
        self.db.commit()
        self.db.refresh(r)
        return r

    def delete(self, result_id: str):
        r = self.db.query(Result).filter(Result.id == result_id, Result.user_id == self.user_id).first()
        if r:
            self.db.delete(r)
            self.db.commit()


class FeeRepository:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    def get_all(self) -> List[Fee]:
        return self.db.query(Fee).filter(Fee.user_id == self.user_id).order_by(Fee.due_date).all()

    def add(self, title: str, amount: float, due_date: str, status: str = "pending") -> Fee:
        f = Fee(user_id=self.user_id, title=title, amount=amount, due_date=due_date, status=status)
        self.db.add(f)
        self.db.commit()
        self.db.refresh(f)
        return f

    def mark_paid(self, fee_id: str):
        f = self.db.query(Fee).filter(Fee.id == fee_id, Fee.user_id == self.user_id).first()
        if f:
            f.status = "paid"
            self.db.commit()

    def delete(self, fee_id: str):
        f = self.db.query(Fee).filter(Fee.id == fee_id, Fee.user_id == self.user_id).first()
        if f:
            self.db.delete(f)
            self.db.commit()
