"""
expenses/models.py
Dataclasses for the Expense Tracker module.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date


# ── Category definitions ────────────────────────────────────────────────────

CATEGORIES: dict[str, str] = {
    "food":           "🍔 Food",
    "transport":      "🚌 Transport",
    "books":          "📚 Books",
    "entertainment":  "🎬 Entertainment",
    "clothing":       "👕 Clothing",
    "health":         "💊 Health",
    "subscription":   "📱 Subscription",
    "tuition":        "🏫 Tuition",
    "income":         "💵 Income",
    "other":          "💰 Other",
}

CATEGORY_COLORS: dict[str, str] = {
    "food":           "#F59E0B",
    "transport":      "#3B82F6",
    "books":          "#8B5CF6",
    "entertainment":  "#EC4899",
    "clothing":       "#14B8A6",
    "health":         "#10B981",
    "subscription":   "#6366F1",
    "tuition":        "#2563EB",
    "income":         "#059669",
    "other":          "#94A3B8",
}


# ── Expense entry ───────────────────────────────────────────────────────────

@dataclass
class Expense:
    id: str              = field(default_factory=lambda: str(uuid.uuid4())[:12])
    date: str            = field(default_factory=lambda: date.today().isoformat())
    type: str            = "expense"   # "expense" | "income"
    category: str        = "other"
    description: str     = ""
    amount: float        = 0.0
    notes: str           = ""
    recurring: bool      = False

    # ── serialisation helpers ─────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "date":        self.date,
            "type":        self.type,
            "category":    self.category,
            "description": self.description,
            "amount":      self.amount,
            "notes":       self.notes,
            "recurring":   self.recurring,
        }

    @staticmethod
    def from_dict(d: dict) -> "Expense":
        return Expense(
            id=d.get("id", str(uuid.uuid4())[:12]),
            date=d.get("date", date.today().isoformat()),
            type=d.get("type", "expense"),
            category=d.get("category", "other"),
            description=d.get("description", ""),
            amount=float(d.get("amount", 0)),
            notes=d.get("notes", ""),
            recurring=bool(d.get("recurring", False)),
        )


# ── Settings ─────────────────────────────────────────────────────────────────

@dataclass
class AppSettings:
    name: str           = "Student"
    budget_monthly: float = 5000.0
    savings_goal: float = 1000.0
    currency: str       = "₹"

    def to_dict(self) -> dict:
        return {
            "name":           self.name,
            "budget_monthly": self.budget_monthly,
            "savings_goal":   self.savings_goal,
            "currency":       self.currency,
        }

    @staticmethod
    def from_dict(d: dict) -> "AppSettings":
        return AppSettings(
            name=d.get("name", "Student"),
            budget_monthly=float(d.get("budget_monthly", 5000)),
            savings_goal=float(d.get("savings_goal", 1000)),
            currency=d.get("currency", "₹"),
        )
