from __future__ import annotations


from datetime import date
from typing import Optional

from expenses.models import AppSettings, Expense
from app.db import SessionLocal
from app.repositories import ExpenseRepository
from authentication.session import Session



class Store:
    """Thin static class — now backed by SQLAlchemy repositories."""

    @staticmethod
    def _get_user_id():
        user = Session.current_user()
        return user.uid if user else "dummy_user"

    # ── Settings ─────────────────────────────────────────────────────────

    @staticmethod
    def get_settings() -> AppSettings:


    @staticmethod
    def save_settings(s: AppSettings) -> None:


    @staticmethod
    def update_settings(**kwargs) -> AppSettings:
        s = Store.get_settings()
        for key, val in kwargs.items():
            if hasattr(s, key):
                setattr(s, key, val)
        return s

    # ── Expenses ─────────────────────────────────────────────────────────

    @staticmethod


    @staticmethod
    def add_expense(exp: Expense) -> Expense:
        db = SessionLocal()
        try:
            repo = ExpenseRepository(db, Store._get_user_id())
            db_exp = repo.add(
                amount=exp.amount,
                category=exp.category,
                description=exp.description,
                date_str=exp.date,
                exp_type=exp.type,
                recurring=exp.recurring
            )
            return Store._to_dataclass(db_exp)
        finally:
            db.close()

    @staticmethod
    def update_expense(exp_id: str, **kwargs) -> Optional[Expense]:
        db = SessionLocal()
        try:
            repo = ExpenseRepository(db, Store._get_user_id())
            db_exp = repo.update(exp_id, kwargs)
            return Store._to_dataclass(db_exp) if db_exp else None
        finally:
            db.close()

    @staticmethod
    def delete_expense(exp_id: str) -> bool:
        db = SessionLocal()
        try:
            repo = ExpenseRepository(db, Store._get_user_id())
            # SQLite doesn't natively return bool on delete so we assume True for now
            repo.delete(exp_id)
            return True
        finally:
            db.close()

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def today_str() -> str:
        return date.today().isoformat()

    @staticmethod
    def get_month_str(year: int, month: int) -> str:
        return f"{year}-{str(month).zfill(2)}"

    @staticmethod
    def filter_by_month(expenses: list[Expense], month_str: str) -> list[Expense]:
        return [e for e in expenses if e.date.startswith(month_str)]

    @staticmethod
    def export_csv(expenses: list[Expense], month_str: str) -> str:
        """Return CSV string for the given month."""
        rows = ["id,date,type,category,description,amount,notes,recurring"]
        for e in Store.filter_by_month(expenses, month_str):
            rows.append(
                f'{e.id},{e.date},{e.type},{e.category},'
                f'"{e.description}",{e.amount},"{e.notes}",{e.recurring}'
            )
        return "\n".join(rows)
