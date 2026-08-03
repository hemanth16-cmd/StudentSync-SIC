"""
main.py — StudentSync Expense Tracker entry point.

Run with:
    python main.py

Flet version: 0.86.5
Python:       3.14+
"""
import flet as ft
from expenses.expense_tracker import ExpenseTrackerView


def main(page: ft.Page) -> None:
    # ── Window / page config ──────────────────────────────────────────────
    page.title = "StudentSync — Expense Tracker"
    page.window.width  = 1100
    page.window.height = 800
    page.window.min_width  = 760
    page.window.min_height = 560
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor    = "#0C1117"
    page.padding    = 0
    page.fonts      = {
        "PlusJakarta": "https://fonts.gstatic.com/s/plusjakartasans/v3/"
                       "LDIoajtzIs2g18Ew1wJHmQ.woff2",
    }
    page.theme = ft.Theme(font_family="PlusJakarta")
    page.scroll = ft.ScrollMode.AUTO

    # ── Build and mount the Expense Tracker view ──────────────────────────
    tracker = ExpenseTrackerView(page)
    page.add(tracker.build())


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550)
