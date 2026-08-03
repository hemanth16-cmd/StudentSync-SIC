"""
expenses/store.py
JSON-backed persistence layer — mirrors the JS Store pattern used by the
rest of the StudentSync project, but implemented in Python.

Data is saved to:  <cwd>/data/expenses_data.json
"""
from __future__ import annotations

from app.database import Database

from datetime import date
from typing import Optional

from expenses.models import AppSettings, Expense

# ── Public API ───────────────────────────────────────────────────────────────

class Store:
    """Thin static class — call from anywhere without instantiation."""

    # ── Settings ─────────────────────────────────────────────────────────

    @staticmethod
    def get_settings() -> AppSettings:
        return AppSettings.from_dict(
            Database.get("expense_settings", {})
        )

    @staticmethod
    def save_settings(s: AppSettings) -> None:
        Database.set(
            "expense_settings",
            s.to_dict()
    )       

    @staticmethod
    def update_settings(**kwargs) -> AppSettings:
        s = Store.get_settings()
        for key, val in kwargs.items():
            if hasattr(s, key):
                setattr(s, key, val)
        Store.save_settings(s)
        return s

    # ── Expenses ─────────────────────────────────────────────────────────

    @staticmethod
    def get_expenses() -> list[Expense]:
        items = Database.get("expenses", [])
        return [
            Expense.from_dict(d)
            for d in reversed(items)
        ]

    @staticmethod
    def _save_expenses(expenses: list[Expense]) -> None:
        Database.set(
            "expenses",
            [
                e.to_dict()
                for e in reversed(expenses)
            ]
        )

    @staticmethod
    def add_expense(exp: Expense) -> Expense:
        expenses = Store.get_expenses()
        expenses.insert(0, exp)
        Store._save_expenses(expenses)
        return exp

    @staticmethod
    def update_expense(exp_id: str, **kwargs) -> Optional[Expense]:
        expenses = Store.get_expenses()
        for exp in expenses:
            if exp.id == exp_id:
                for key, val in kwargs.items():
                    if hasattr(exp, key):
                        setattr(exp, key, val)
                Store._save_expenses(expenses)
                return exp
        return None

    @staticmethod
    def delete_expense(exp_id: str) -> bool:
        expenses = Store.get_expenses()
        new_list = [e for e in expenses if e.id != exp_id]
        if len(new_list) == len(expenses):
            return False
        Store._save_expenses(new_list)
        return True

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
