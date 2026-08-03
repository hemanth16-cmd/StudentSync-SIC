"""
Habit Tracker Page View for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary
from app.database import Database
from components.common_widgets import create_card, create_section_header, create_empty_state
from components.modals import show_toast


def habits_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    name_f = ft.TextField(hint_text="Habit name (e.g. Read 20 mins)", expand=True, height=42, border_radius=10)
    icon_f = ft.TextField(value="⭐", hint_text="Emoji", width=72, height=42, border_radius=10)

    habit_col = ft.Column(spacing=12)

    def _rebuild():
        habits = Database.get_habits()
        habit_col.controls.clear()
        if not habits:
            habit_col.controls.append(
                create_empty_state(ft.Icons.LOOP_OUTLINED, "No habits tracked yet", dark_mode)
            )
            return
        today = Database.today_str()
        for h in habits:
            done   = h.get("completions", {}).get(today, False)
            streak = h.get("streak", 0)
            habit_col.controls.append(
                create_card(
                    content=ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Text(h.get("icon", "⭐"), size=26),
                                    ft.Column(
                                        [
                                            ft.Text(h["name"], size=14, weight=ft.FontWeight.BOLD,
                                                    color=get_text_primary(dark_mode)),
                                            ft.Text(f"🔥 {streak} day streak", size=12,
                                                    color=AppColors.ORANGE, weight=ft.FontWeight.W_600),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                spacing=12,
                            ),
                            ft.ElevatedButton(
                                "✓ Done" if done else "Mark Done",
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor=AppColors.GREEN if done else AppColors.BG_HOVER_DARK if dark_mode else AppColors.BG_HOVER_LIGHT,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                                on_click=lambda e, hid=h["id"]: _toggle(hid),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=14, dark_mode=dark_mode,
                )
            )

    def _add(e):
        if not name_f.value or not name_f.value.strip():
            show_toast(page, "Please enter a habit name", "error")
            return
        Database.add_habit(name=name_f.value.strip(), icon=icon_f.value.strip() or "⭐")
        name_f.value = ""
        show_toast(page, "Habit added!", "success")
        _rebuild(); page.update()

    def _toggle(hid):
        Database.toggle_habit(hid, Database.today_str())
        _rebuild(); page.update()

    _rebuild()

    add_card = create_card(
        content=ft.Row(
            [name_f, icon_f,
             ft.ElevatedButton(
                 "Add Habit",
                 icon=ft.Icons.ADD,
                 style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.GREEN,
                                      shape=ft.RoundedRectangleBorder(radius=10)),
                 on_click=_add, height=42,
             )],
            spacing=10,
        ),
        padding=16, dark_mode=dark_mode,
    )

    return ft.Column(
        [
            create_section_header("Habit Tracker", "Build consistent daily routines and track streaks", dark_mode=dark_mode),
            add_card,
            habit_col,
        ],
        spacing=16, expand=True, scroll=ft.ScrollMode.AUTO,
    )
