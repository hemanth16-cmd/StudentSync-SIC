"""
expenses/dialogs.py
Add / Edit / Delete / Settings dialogs for the Expense Tracker.
All dialogs are pure Flet — no web tech.
"""
from __future__ import annotations

import flet as ft
from datetime import date

from expenses.models import CATEGORIES, CATEGORY_COLORS, Expense, AppSettings
from expenses.store import Store
from expenses.ui_helpers import BLUE, GREEN, DANGER, ORANGE, TEXT_1, TEXT_2, TEXT_3, BORDER


def _close(page: ft.Page) -> None:
    page.pop_dialog()


# ── Add / Edit ────────────────────────────────────────────────────────────────

def open_add_edit_dialog(
    page: ft.Page,
    on_saved,
    expense: Expense | None = None,
) -> None:
    """Open modal for adding (expense=None) or editing an existing expense."""
    is_edit = expense is not None
    title   = "Edit Transaction" if is_edit else "Add Transaction"

    # ── state refs ────────────────────────────────────────────────────────
    tx_type = [expense.type if is_edit else "expense"]

    amount_field = ft.TextField(
        label="Amount",
        prefix=ft.Text(Store.get_settings().currency + " "),
        value=str(expense.amount) if is_edit else "",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=BORDER,
        focused_border_color=BLUE,
        label_style=ft.TextStyle(color=TEXT_2, size=12),
        color=TEXT_1,
        expand=True,
    )
    desc_field = ft.TextField(
        label="Description",
        value=expense.description if is_edit else "",
        border_color=BORDER,
        focused_border_color=BLUE,
        label_style=ft.TextStyle(color=TEXT_2, size=12),
        color=TEXT_1,
        expand=True,
    )
    notes_field = ft.TextField(
        label="Notes (optional)",
        value=expense.notes if is_edit else "",
        multiline=True, min_lines=2,
        border_color=BORDER,
        focused_border_color=BLUE,
        label_style=ft.TextStyle(color=TEXT_2, size=12),
        color=TEXT_1,
    )
    date_field = ft.TextField(
        label="Date (YYYY-MM-DD)",
        value=expense.date if is_edit else Store.today_str(),
        border_color=BORDER,
        focused_border_color=BLUE,
        label_style=ft.TextStyle(color=TEXT_2, size=12),
        color=TEXT_1,
        expand=True,
    )
    recurring_check = ft.Checkbox(
        label="Recurring expense",
        value=expense.recurring if is_edit else False,
        active_color=BLUE,
        label_style=ft.TextStyle(color=TEXT_2, size=12),
    )

    cat_options = [
        ft.dropdown.Option(key=k, text=v) for k, v in CATEGORIES.items()
    ]
    cat_dropdown = ft.Dropdown(
        label="Category",
        value=expense.category if is_edit else "other",
        options=cat_options,
        border_color=BORDER,
        focused_border_color=BLUE,
        label_style=ft.TextStyle(color=TEXT_2, size=12),
        color=TEXT_1,
        expand=True,
    )

    # ── type toggle ────────────────────────────────────────────────────────
    type_row_ref = ft.Ref[ft.Row]()

    def _build_type_row():
        return ft.Row([
            _type_btn("💸 Expense", "expense"),
            _type_btn("💵 Income", "income"),
        ], spacing=8)

    def _type_btn(label: str, value: str) -> ft.ElevatedButton:
        active = tx_type[0] == value
        return ft.ElevatedButton(
            label,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.with_opacity(0.15, BLUE) if active else "transparent",
                color=BLUE if active else TEXT_2,
                side=ft.BorderSide(1, ft.Colors.with_opacity(0.4, BLUE) if active else BORDER),
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=lambda e, v=value: _select_type(v),
        )

    type_row_container = ft.Column([_build_type_row()], spacing=0)

    def _select_type(value: str):
        tx_type[0] = value
        type_row_container.controls = [_build_type_row()]
        page.update()

    # ── save handler ───────────────────────────────────────────────────────
    def _save(e):
        try:
            amt = float(amount_field.value or 0)
        except ValueError:
            amt = 0
        if amt <= 0:
            amount_field.error_text = "Enter a valid amount"
            page.update()
            return

        # Resolve category: income-type forces income category
        cat = cat_dropdown.value or "other"
        if tx_type[0] == "income":
            cat = "income"

        if is_edit:
            Store.update_expense(
                expense.id,
                type=tx_type[0],
                amount=amt,
                description=desc_field.value.strip(),
                category=cat,
                date=date_field.value or Store.today_str(),
                notes=notes_field.value.strip(),
                recurring=recurring_check.value,
            )
        else:
            new_exp = Expense(
                type=tx_type[0],
                amount=amt,
                description=desc_field.value.strip(),
                category=cat,
                date=date_field.value or Store.today_str(),
                notes=notes_field.value.strip(),
                recurring=recurring_check.value,
            )
            Store.add_expense(new_exp)

        _close(page)
        on_saved()

    # ── dialog ────────────────────────────────────────────────────────────
    dlg = ft.AlertDialog(
        title=ft.Text(title, size=16, weight=ft.FontWeight.W_800, color=TEXT_1),
        bgcolor="#161B26",
        content=ft.Container(
            width=420,
            content=ft.Column([
                ft.Text("Type", size=11, color=TEXT_2, weight=ft.FontWeight.W_600),
                type_row_container,
                ft.Row([amount_field, date_field], spacing=10),
                desc_field,
                ft.Row([cat_dropdown], spacing=10),
                notes_field,
                recurring_check,
            ], spacing=14, scroll=ft.ScrollMode.AUTO),
        ),
        actions=[
            ft.TextButton("Cancel",
                          style=ft.ButtonStyle(color=TEXT_2),
                          on_click=lambda e: _close(page)),
            ft.FilledButton(
                "Save",
                style=ft.ButtonStyle(bgcolor=BLUE),
                on_click=_save,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dlg)


# ── Delete confirm ────────────────────────────────────────────────────────────

def open_delete_dialog(page: ft.Page, expense: Expense, on_deleted) -> None:
    def _confirm(e):
        Store.delete_expense(expense.id)
        _close(page)
        on_deleted()

    dlg = ft.AlertDialog(
        title=ft.Text("Delete Transaction?", size=15,
                      weight=ft.FontWeight.W_700, color=TEXT_1),
        bgcolor="#161B26",
        content=ft.Text(
            f'Remove "{expense.description or CATEGORIES.get(expense.category, expense.category)}" '
            f'({Store.get_settings().currency}{expense.amount:,.2f})?',
            color=TEXT_2, size=13,
        ),
        actions=[
            ft.TextButton("Cancel",
                          style=ft.ButtonStyle(color=TEXT_2),
                          on_click=lambda e: _close(page)),
            ft.FilledButton(
                "Delete",
                style=ft.ButtonStyle(bgcolor=DANGER),
                on_click=_confirm,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dlg)


# ── Settings dialog ───────────────────────────────────────────────────────────

def open_settings_dialog(page: ft.Page, on_saved) -> None:
    s = Store.get_settings()
    name_field = ft.TextField(
        label="Your name",
        value=s.name,
        border_color=BORDER, focused_border_color=BLUE,
        label_style=ft.TextStyle(color=TEXT_2, size=12), color=TEXT_1,
    )
    budget_field = ft.TextField(
        label="Monthly budget",
        value=str(s.budget_monthly),
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=BORDER, focused_border_color=BLUE,
        label_style=ft.TextStyle(color=TEXT_2, size=12), color=TEXT_1,
    )
    goal_field = ft.TextField(
        label="Monthly savings goal",
        value=str(s.savings_goal),
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=BORDER, focused_border_color=BLUE,
        label_style=ft.TextStyle(color=TEXT_2, size=12), color=TEXT_1,
    )
    currency_field = ft.TextField(
        label="Currency symbol",
        value=s.currency,
        border_color=BORDER, focused_border_color=BLUE,
        label_style=ft.TextStyle(color=TEXT_2, size=12), color=TEXT_1,
    )

    def _save(e):
        try:
            budget = float(budget_field.value or 5000)
            goal   = float(goal_field.value or 1000)
        except ValueError:
            budget, goal = 5000, 1000
        Store.update_settings(
            name=name_field.value.strip() or "Student",
            budget_monthly=budget,
            savings_goal=goal,
            currency=currency_field.value.strip() or "₹",
        )
        _close(page)
        on_saved()

    dlg = ft.AlertDialog(
        title=ft.Text("Settings", size=16, weight=ft.FontWeight.W_800, color=TEXT_1),
        bgcolor="#161B26",
        content=ft.Container(
            width=380,
            content=ft.Column(
                [name_field, budget_field, goal_field, currency_field],
                spacing=14,
            ),
        ),
        actions=[
            ft.TextButton("Cancel",
                          style=ft.ButtonStyle(color=TEXT_2),
                          on_click=lambda e: _close(page)),
            ft.FilledButton("Save", style=ft.ButtonStyle(bgcolor=BLUE), on_click=_save),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dlg)
