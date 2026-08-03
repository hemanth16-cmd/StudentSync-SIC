"""
Topbar Header Component for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_card_bg, get_text_primary, get_text_secondary, get_border_color
from app.state import AppState
from app.database import Database

_PAGE_TITLES = {
    "dashboard":   "Dashboard",
    "todos":       "To-Do List",
    "planner":     "Planner",
    "subjects":    "Subjects",
    "assignments": "Assignments",
    "notes":       "Notes",
    "attendance":  "Attendance",
    "habits":      "Habit Tracker",
    "diet":        "Diet & Nutrition",
    "workout":     "Workout",
    "sleep":       "Sleep Tracker",
    "expenses":    "Expenses",
    "analytics":   "Analytics",
    "settings":    "Settings",
}


def create_topbar(page: ft.Page, dark_mode: bool = True) -> ft.Container:
    """Builds the application topbar."""

    settings  = Database.get_settings()
    user_name = settings.get("name", "Student")
    initials  = (user_name[:2]).upper() if user_name else "ST"
    title_str = _PAGE_TITLES.get(AppState.current_page, AppState.current_page.replace("_", " ").title())
    bc = get_border_color(dark_mode)

    def on_search_change(e):
        AppState.set_search(e.control.value)

    def on_theme_click(e):
        AppState.toggle_theme()

    def on_profile_click(e):
        AppState.set_page("settings")

    search_box = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.SEARCH, color=get_text_secondary(dark_mode), size=16),
                ft.TextField(
                    hint_text="Search tasks...",
                    hint_style=ft.TextStyle(size=12, color=get_text_secondary(dark_mode)),
                    text_style=ft.TextStyle(size=12, color=get_text_primary(dark_mode)),
                    border=ft.InputBorder.NONE,
                    height=32,
                    content_padding=ft.Padding(left=0, right=0, top=0, bottom=10),
                    expand=True,
                    on_change=on_search_change,
                ),
            ],
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=220,
        height=38,
        bgcolor=AppColors.BG_APP_DARK if dark_mode else AppColors.BG_APP_LIGHT,
        border_radius=20,
        border=ft.Border(
            top=ft.BorderSide(1, bc),
            right=ft.BorderSide(1, bc),
            bottom=ft.BorderSide(1, bc),
            left=ft.BorderSide(1, bc),
        ),
        padding=ft.Padding(left=12, right=12, top=0, bottom=0),
    )

    theme_btn = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE if dark_mode else ft.Icons.DARK_MODE,
        icon_color=AppColors.ORANGE_LIGHT if dark_mode else AppColors.BLUE,
        icon_size=20,
        tooltip="Toggle Light/Dark Theme",
        on_click=on_theme_click,
    )

    profile_pill = ft.Container(
        content=ft.Row(
            [
                ft.CircleAvatar(
                    content=ft.Text(initials, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=AppColors.BLUE,
                    radius=14,
                ),
                ft.Text(user_name, size=13, weight=ft.FontWeight.W_600, color=get_text_primary(dark_mode)),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=10, right=10, top=6, bottom=6),
        border_radius=24,
        border=ft.Border(
            top=ft.BorderSide(1, bc),
            right=ft.BorderSide(1, bc),
            bottom=ft.BorderSide(1, bc),
            left=ft.BorderSide(1, bc),
        ),
        ink=True,
        on_click=on_profile_click,
    )

    topbar_row = ft.Row(
        [
            ft.Text(title_str, size=18, weight=ft.FontWeight.BOLD, color=get_text_primary(dark_mode)),
            ft.Row(
                [search_box, theme_btn, profile_pill],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        content=topbar_row,
        padding=ft.Padding(left=24, right=24, top=12, bottom=12),
        bgcolor=get_card_bg(dark_mode),
        border=ft.Border(bottom=ft.BorderSide(1, bc)),
        height=64,
    )
