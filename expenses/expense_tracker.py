"""
expenses/expense_tracker.py
Main Expense Tracker view — mounts onto the Flet Page.
Handles: month navigation, stat cards, budget bar, category breakdown,
         spending insights, transaction list (search + filter), CSV export.

Integration contract:
    from expenses.expense_tracker import ExpenseTrackerView
    view = ExpenseTrackerView(page)
    page.add(view.build())
"""
from __future__ import annotations

import calendar
import csv
import io
import os
from collections import defaultdict
from datetime import date, datetime

import flet as ft

from expenses.dialogs import (
    open_add_edit_dialog,
    open_delete_dialog,
    open_settings_dialog,
)
from expenses.models import CATEGORIES, CATEGORY_COLORS, Expense
from expenses.store import Store
from expenses.ui_helpers import (
    BLUE, BORDER, DANGER, GRAD_BG, GREEN, INDIGO, ORANGE, PURPLE, TEXT_1,
    TEXT_2, TEXT_3, build_bar_chart, build_pie_chart, card, chip_button,
    divider, icon_box, pie_legend, progress_bar, progress_bar_row,
    section_title, stat_card,
)


class ExpenseTrackerView:
    """
    Self-contained Expense Tracker view.
    Call build() to get the root Flet control, then add it to the page.
    """

    def __init__(self, page: ft.Page) -> None:
        self.page = page

        # ── view state ────────────────────────────────────────────────────
        now = date.today()
        self._year  = now.year
        self._month = now.month

        self._filter_cat: str = "all"
        self._search_q:   str = ""

        # ── root container reference (rebuilt on every render) ─────────────
        self._root = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0, expand=True)

    # ═════════════════════════════════════════════════════════════════════════
    # Public
    # ═════════════════════════════════════════════════════════════════════════

    def build(self) -> ft.Control:
        self._render()
        return ft.Container(
            content=self._root,
            expand=True,
            gradient=GRAD_BG,
            padding=ft.Padding.all(0),
        )

    # ═════════════════════════════════════════════════════════════════════════
    # Core render
    # ═════════════════════════════════════════════════════════════════════════

    def _render(self) -> None:
        settings     = Store.get_settings()
        all_expenses = Store.get_expenses()
        month_str    = Store.get_month_str(self._year, self._month)
        month_exps   = Store.filter_by_month(all_expenses, month_str)

        income  = sum(e.amount for e in month_exps if e.type == "income")
        spent   = sum(e.amount for e in month_exps if e.type == "expense")
        balance = income - spent
        savings_rate = round((balance / income * 100) if income > 0 else 0)
        budget  = settings.budget_monthly
        cur     = settings.currency

        budget_pct = min(round(spent / budget * 100) if budget > 0 else 0, 100)

        # category totals
        cat_totals: dict[str, float] = defaultdict(float)
        for e in month_exps:
            if e.type == "expense":
                cat_totals[e.category] += e.amount
        sorted_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)

        # savings goal progress
        s_goal = settings.savings_goal
        s_pct  = min(round(balance / s_goal * 100) if s_goal > 0 else 0, 100)

        # monthly totals (last 6 months for bar chart)
        monthly_data = self._monthly_data(all_expenses, cur)
        
        # daily totals (last 7 days for bar chart)
        daily_data = self._daily_data(all_expenses, cur)

        # insights
        top_cat    = sorted_cats[0] if sorted_cats else None
        max_single = max((e.amount for e in month_exps if e.type == "expense"),
                         default=0)
        days_in_mo = calendar.monthrange(self._year, self._month)[1]
        daily_avg  = round(spent / days_in_mo, 2)

        # ── assemble sections ─────────────────────────────────────────────
        self._root.controls = [
            ft.Container(  # page padding wrapper
                padding=ft.Padding.all(24),
                content=ft.Column([
                    self._header(month_str, settings),
                    self._stat_row(income, spent, balance, savings_rate, cur),
                    self._budget_bar(spent, budget, budget_pct, cur),
                    self._two_col(
                        self._category_breakdown(sorted_cats, spent, cur),
                        self._savings_goal(balance, s_goal, s_pct, cur),
                    ),
                    self._insights_strip(top_cat, max_single, daily_avg, cur),
                    self._two_col(
                        self._daily_chart(daily_data, cur),
                        self._monthly_chart(monthly_data, cur),
                    ),
                    self._transactions_section(all_expenses, month_exps, cur),
                ], spacing=20),
            )
        ]
        self.page.update()

    # ═════════════════════════════════════════════════════════════════════════
    # Sections
    # ═════════════════════════════════════════════════════════════════════════

    def _header(self, month_str: str, settings) -> ft.Row:
        mo_name = datetime(self._year, self._month, 1).strftime("%B %Y")

        def _prev(_):
            if self._month == 1:
                self._month, self._year = 12, self._year - 1
            else:
                self._month -= 1
            self._render()

        def _next(_):
            if self._month == 12:
                self._month, self._year = 1, self._year + 1
            else:
                self._month += 1
            self._render()

        def _export(_):
            self._export_csv(month_str, settings.currency)

        def _open_settings(_):
            open_settings_dialog(self.page, on_saved=self._render)

        return ft.Row([
            ft.Column([
                ft.Text("💰 Expense Tracker", size=22,
                        weight=ft.FontWeight.W_800, color=TEXT_1),
                ft.Row([
                    ft.IconButton(ft.Icons.CHEVRON_LEFT,
                                  icon_color=TEXT_2, on_click=_prev,
                                  tooltip="Previous month"),
                    ft.Text(mo_name, size=14, color=TEXT_2,
                            weight=ft.FontWeight.W_600),
                    ft.IconButton(ft.Icons.CHEVRON_RIGHT,
                                  icon_color=TEXT_2, on_click=_next,
                                  tooltip="Next month"),
                ], spacing=2),
            ], spacing=4),
            ft.Row([
                ft.OutlinedButton(
                    "Export CSV",
                    icon=ft.Icons.DOWNLOAD_OUTLINED,
                    style=ft.ButtonStyle(
                        color=TEXT_2,
                        side=ft.BorderSide(1, BORDER),
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    on_click=_export,
                ),
                ft.FilledButton(
                    "+ Add Entry",
                    style=ft.ButtonStyle(
                        bgcolor=BLUE,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    on_click=lambda _: open_add_edit_dialog(
                        self.page, on_saved=self._render),
                ),
                ft.IconButton(ft.Icons.SETTINGS_OUTLINED,
                              icon_color=TEXT_2, on_click=_open_settings,
                              tooltip="Settings"),
            ], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # ─────────────────────────────────────────────────────────────────────────

    def _stat_row(self, income, spent, balance, savings_rate, cur) -> ft.Row:
        bal_color  = GREEN if balance >= 0 else DANGER
        sign       = "+" if balance >= 0 else "-"
        bal_label  = "Balance" if balance >= 0 else "Deficit"

        return ft.Row([
            stat_card("Income",  f"{cur}{income:,.0f}",
                      ft.Icons.TRENDING_UP,    GREEN),
            stat_card("Spent",   f"{cur}{spent:,.0f}",
                      ft.Icons.TRENDING_DOWN,  DANGER),
            stat_card(bal_label, f"{sign}{cur}{abs(balance):,.0f}",
                      ft.Icons.ACCOUNT_BALANCE_WALLET, bal_color),
            stat_card("Savings Rate", f"{savings_rate}%",
                      ft.Icons.SAVINGS_OUTLINED, PURPLE),
        ], spacing=12, expand=True)

    # ─────────────────────────────────────────────────────────────────────────

    def _budget_bar(self, spent, budget, pct, cur) -> ft.Container:
        fill_color = DANGER if pct >= 100 else ORANGE if pct >= 80 else GREEN
        remaining  = max(budget - spent, 0)

        bar = progress_bar(pct, fill_color, height=10)
        return card(ft.Column([
            section_title("Monthly Budget", ft.Icons.PIE_CHART_OUTLINE),
            ft.Row([
                ft.Text("Spent", size=12, color=TEXT_2),
                ft.Text(f"{cur}{spent:,.0f} / {cur}{budget:,.0f}",
                        size=12, color=TEXT_1, weight=ft.FontWeight.W_600),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bar,
            ft.Row([
                ft.Text(f"{pct}% used", size=11, color=TEXT_3),
                ft.Text(f"{cur}{remaining:,.0f} remaining",
                        size=11,
                        color=DANGER if pct >= 100 else TEXT_3),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ], spacing=10))

    # ─────────────────────────────────────────────────────────────────────────

    def _category_breakdown(self, sorted_cats, total_spent, cur) -> ft.Container:
        if not sorted_cats:
            body = ft.Text("No expenses this month",
                           size=13, color=TEXT_3, italic=True)
            return card(ft.Column([
                section_title("By Category", ft.Icons.DONUT_SMALL),
                body,
            ], spacing=14))

        # Build pie data
        pie_data = [
            (
                CATEGORIES.get(cat, cat),
                amt,
                CATEGORY_COLORS.get(cat, INDIGO),
            )
            for cat, amt in sorted_cats[:7]
        ]

        return card(ft.Column([
            section_title("By Category", ft.Icons.DONUT_SMALL),
            ft.Row([
                build_pie_chart(pie_data, size=150),
                ft.Container(width=12),
                ft.Container(
                    content=pie_legend(pie_data, currency=cur),
                    expand=True,
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.START),
        ], spacing=14))

    # ─────────────────────────────────────────────────────────────────────────

    def _savings_goal(self, balance, goal, pct, cur) -> ft.Container:
        color = GREEN if pct >= 100 else BLUE if pct >= 50 else ORANGE

        bar = progress_bar(pct, color, height=10)

        badge_text = "🎯 Goal reached!" if pct >= 100 else f"{pct}% of goal"
        return card(ft.Column([
            section_title("Savings Goal", ft.Icons.FLAG_OUTLINED),
            ft.Row([
                ft.Text("Target", size=12, color=TEXT_2),
                ft.Text(f"{cur}{goal:,.0f}", size=12,
                        color=TEXT_1, weight=ft.FontWeight.W_600),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                ft.Text("Saved", size=12, color=TEXT_2),
                ft.Text(f"{cur}{max(balance,0):,.0f}", size=12,
                        color=GREEN, weight=ft.FontWeight.W_600),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bar,
            ft.Text(badge_text, size=11, color=color),
        ], spacing=10))

    # ─────────────────────────────────────────────────────────────────────────

    def _insights_strip(self, top_cat, max_single, daily_avg, cur) -> ft.Row:
        top_label = (
            CATEGORIES.get(top_cat[0], top_cat[0]) if top_cat else "—"
        )
        top_val = (
            f"{cur}{top_cat[1]:,.0f}" if top_cat else "—"
        )

        def _insight(icon, label, value, color):
            return ft.Container(
                content=ft.Column([
                    icon_box(icon, color),
                    ft.Text(value, size=16,
                            weight=ft.FontWeight.W_800, color=TEXT_1),
                    ft.Text(label, size=11, color=TEXT_3),
                ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.START),
                padding=ft.Padding.all(16),
                border_radius=ft.BorderRadius.all(14),
                border=ft.Border.all(1, BORDER),
                bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.WHITE),
                expand=True,
            )

        return ft.Row([
            _insight(ft.Icons.STAR_OUTLINE, "Top Category",
                     f"{top_label}\n{top_val}", ORANGE),
            _insight(ft.Icons.ARROW_UPWARD, "Biggest Expense",
                     f"{cur}{max_single:,.0f}", DANGER),
            _insight(ft.Icons.CALENDAR_TODAY, "Daily Average",
                     f"{cur}{daily_avg:,.2f}", BLUE),
        ], spacing=12, expand=True)

    # ─────────────────────────────────────────────────────────────────────────

    def _daily_chart(self, daily_data: list[tuple[str, float]], cur) -> ft.Container:
        """Canvas-drawn bar chart showing last 7 days of spending."""
        return card(ft.Column([
            section_title("Daily Spending", ft.Icons.BAR_CHART),
            build_bar_chart(
                daily_data,
                bar_color=ft.Colors.with_opacity(0.45, BLUE),
                highlight_color=BLUE,
                width=300,
                height=180,
                currency=cur,
            ),
        ], spacing=14))

    # ─────────────────────────────────────────────────────────────────────────

    def _monthly_chart(self, monthly_data: list[tuple[str, float]], cur) -> ft.Container:
        """Canvas-drawn bar chart showing last 6 months of spending."""
        return card(ft.Column([
            section_title("Monthly Spending", ft.Icons.BAR_CHART),
            build_bar_chart(
                monthly_data,
                bar_color=ft.Colors.with_opacity(0.45, BLUE),
                highlight_color=BLUE,
                width=500,
                height=180,
                currency=cur,
            ),
        ], spacing=14))

    # ─────────────────────────────────────────────────────────────────────────

    def _transactions_section(self, all_exps, month_exps, cur) -> ft.Container:
        # ── filter chips ─────────────────────────────────────────────────
        used_cats = list({e.category for e in month_exps if e.type == "expense"})
        used_cats.sort()

        def _set_filter(cat: str):
            self._filter_cat = cat
            self._render()

        chips = [
            chip_button("All",
                        self._filter_cat == "all",
                        lambda _, c="all": _set_filter(c)),
            *[
                chip_button(
                    CATEGORIES.get(c, c).split()[0],  # just emoji
                    self._filter_cat == c,
                    lambda _, c=c: _set_filter(c),
                )
                for c in used_cats
            ],
        ]

        # ── search ────────────────────────────────────────────────────────
        def _on_search(e):
            self._search_q = e.control.value.lower()
            self._render()

        search = ft.TextField(
            prefix_icon=ft.Icons.SEARCH,
            hint_text="Search transactions…",
            value=self._search_q,
            on_change=_on_search,
            border_color=BORDER,
            focused_border_color=BLUE,
            hint_style=ft.TextStyle(color=TEXT_3, size=13),
            color=TEXT_1,
            height=42,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=0),
            border_radius=ft.BorderRadius.all(12),
        )

        # ── apply filters ─────────────────────────────────────────────────
        filtered = [
            e for e in month_exps
            if (self._filter_cat == "all" or e.category == self._filter_cat)
            and (not self._search_q or
                 self._search_q in e.description.lower() or
                 self._search_q in CATEGORIES.get(e.category, "").lower())
        ]

        # ── transaction rows ─────────────────────────────────────────────
        rows: list[ft.Control] = []
        for exp in filtered:
            rows.append(self._tx_row(exp, cur))
            rows.append(divider())

        if not rows:
            rows = [ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED,
                            size=48, color=TEXT_3),
                    ft.Text("No transactions found",
                            size=14, color=TEXT_3, italic=True),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   spacing=8),
                alignment=ft.Alignment(0, 0),
                padding=ft.Padding.symmetric(vertical=32),
            )]

        return card(ft.Column([
            section_title("Transactions", ft.Icons.RECEIPT_LONG_OUTLINED),
            search,
            ft.Row(chips, scroll=ft.ScrollMode.AUTO, spacing=6),
            divider(),
            ft.Column(rows, spacing=0),
        ], spacing=12))

    # ─────────────────────────────────────────────────────────────────────────

    def _tx_row(self, exp: Expense, cur: str) -> ft.Row:
        is_income  = exp.type == "income"
        color      = GREEN if is_income else DANGER
        sign       = "+" if is_income else "−"
        cat_label  = CATEGORIES.get(exp.category, exp.category)
        cat_color  = CATEGORY_COLORS.get(exp.category, INDIGO)
        desc       = exp.description or cat_label
        date_str   = exp.date

        recurring_icon = (
            ft.Icon(ft.Icons.REPEAT, size=12, color=BLUE)
            if exp.recurring else ft.Container()
        )

        edit_btn = ft.IconButton(
            ft.Icons.EDIT_OUTLINED,
            icon_size=16, icon_color=TEXT_3,
            tooltip="Edit",
            on_click=lambda _, e=exp: open_add_edit_dialog(
                self.page, on_saved=self._render, expense=e),
        )
        del_btn = ft.IconButton(
            ft.Icons.DELETE_OUTLINE,
            icon_size=16, icon_color=DANGER,
            tooltip="Delete",
            on_click=lambda _, e=exp: open_delete_dialog(
                self.page, expense=e, on_deleted=self._render),
        )

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    width=4, height=36,
                    border_radius=ft.BorderRadius.all(4),
                    bgcolor=cat_color,
                ),
                ft.Column([
                    ft.Row([
                        ft.Text(desc, size=13,
                                weight=ft.FontWeight.W_600, color=TEXT_1,
                                expand=True, overflow=ft.TextOverflow.ELLIPSIS),
                        recurring_icon,
                    ], spacing=4),
                    ft.Text(f"{cat_label}  ·  {date_str}",
                            size=11, color=TEXT_3),
                ], spacing=2, expand=True),
                ft.Text(f"{sign}{cur}{exp.amount:,.2f}",
                        size=14, weight=ft.FontWeight.W_700, color=color),
                ft.Row([edit_btn, del_btn], spacing=0),
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding.symmetric(vertical=8),
        )

    # ═════════════════════════════════════════════════════════════════════════
    # Layout helpers
    # ═════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _two_col(left: ft.Control, right: ft.Control) -> ft.Row:
        return ft.Row([
            ft.Container(content=left,  expand=True),
            ft.Container(content=right, expand=True),
        ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START)

    # ═════════════════════════════════════════════════════════════════════════
    # Data helpers
    # ═════════════════════════════════════════════════════════════════════════

    def _daily_data(self, all_exps: list[Expense], cur: str) -> list[tuple[str, float]]:
        """Return (weekday-label, total-spent) for the last 7 calendar days."""
        from datetime import timedelta
        today = date.today()
        result = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            d_str = d.isoformat()
            total = sum(
                e.amount for e in all_exps
                if e.date == d_str and e.type == "expense"
            )
            result.append((d.strftime("%a"), total))
        return result

    def _monthly_data(self, all_exps: list[Expense], cur: str) -> list[tuple[str, float]]:
        """Return (month-label, total-spent) for the last 6 months."""
        result = []
        for i in range(5, -1, -1):
            m = self._month - i
            y = self._year
            while m <= 0:
                m += 12
                y -= 1
            ms = Store.get_month_str(y, m)
            total = sum(
                e.amount for e in all_exps
                if e.date.startswith(ms) and e.type == "expense"
            )
            label = datetime(y, m, 1).strftime("%b")
            result.append((label, total))
        return result

    # ═════════════════════════════════════════════════════════════════════════
    # CSV export
    # ═════════════════════════════════════════════════════════════════════════

    def _export_csv(self, month_str: str, cur: str) -> None:
        """Save CSV to user's Downloads folder and show snack bar."""
        all_exps  = Store.get_expenses()
        csv_str   = Store.export_csv(all_exps, month_str)

        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(downloads, exist_ok=True)
        filename = os.path.join(downloads, f"expenses_{month_str}.csv")

        with open(filename, "w", encoding="utf-8", newline="") as fh:
            fh.write(csv_str)

        sb = ft.SnackBar(
            content=ft.Text(f"✅ Exported to {filename}", color="#F0F6FF"),
            bgcolor="#161B26",
        )
        self.page.overlay.append(sb)
        sb.open = True
        self.page.update()
