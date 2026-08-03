"""
Navigation Sidebar Component for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_card_bg, get_text_primary, get_text_secondary, get_border_color
from app.state import AppState

NAV_SECTIONS = [
    {
        "section": "Main",
        "items": [
            {"key": "dashboard",   "label": "Dashboard",  "icon": ft.Icons.DASHBOARD_ROUNDED},
            {"key": "todos",       "label": "To-Do",      "icon": ft.Icons.CHECKLIST_ROUNDED},
            {"key": "planner",     "label": "Planner",    "icon": ft.Icons.CALENDAR_MONTH_ROUNDED},
        ],
    },
    {
        "section": "Academics",
        "items": [
            {"key": "subjects",    "label": "Subjects",    "icon": ft.Icons.BOOK_ROUNDED},
            {"key": "assignments", "label": "Assignments", "icon": ft.Icons.ASSIGNMENT_ROUNDED},
            {"key": "notes",       "label": "Notes",       "icon": ft.Icons.DESCRIPTION_ROUNDED},
            {"key": "attendance",  "label": "Attendance",  "icon": ft.Icons.HOW_TO_REG_ROUNDED},
        ],
    },
    {
        "section": "Lifestyle",
        "items": [
            {"key": "habits",   "label": "Habit Tracker", "icon": ft.Icons.LOOP_ROUNDED},
            {"key": "diet",     "label": "Diet",          "icon": ft.Icons.RESTAURANT_ROUNDED},
            {"key": "workout",  "label": "Workout",       "icon": ft.Icons.FITNESS_CENTER_ROUNDED},
            {"key": "sleep",    "label": "Sleep",         "icon": ft.Icons.BEDTIME_ROUNDED},
            {"key": "expenses", "label": "Expenses",      "icon": ft.Icons.ATTACH_MONEY_ROUNDED},
        ],
    },
    {
        "section": "Insights",
        "items": [
            {"key": "analytics", "label": "Analytics", "icon": ft.Icons.BAR_CHART_ROUNDED},
        ],
    },
]


def create_sidebar(page: ft.Page, dark_mode: bool = True) -> ft.Container:
    """Builds the navigation sidebar."""

    current_key = AppState.current_page

    def on_nav_click(e, key: str):
        AppState.set_page(key)

    def nav_item(item: dict) -> ft.Container:
        active = item["key"] == current_key
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        item["icon"],
                        color=ft.Colors.WHITE if active else get_text_secondary(dark_mode),
                        size=18,
                    ),
                    ft.Text(
                        item["label"],
                        size=13,
                        weight=ft.FontWeight.W_600 if active else ft.FontWeight.NORMAL,
                        color=ft.Colors.WHITE if active else get_text_secondary(dark_mode),
                    ),
                ],
                spacing=12,
            ),
            padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            border_radius=10,
            bgcolor=AppColors.BLUE if active else ft.Colors.TRANSPARENT,
            ink=True,
            on_click=lambda e, k=item["key"]: on_nav_click(e, k),
        )

    # ── Logo ──────────────────────────────────────────────────────────────
    logo = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.SCHOOL_ROUNDED, color=ft.Colors.WHITE, size=22),
                    padding=8,
                    bgcolor=AppColors.BLUE,
                    border_radius=12,
                ),
                ft.Column(
                    [
                        ft.Text("StudentSync", size=15, weight=ft.FontWeight.BOLD, color=get_text_primary(dark_mode)),
                        ft.Text("Premium Productivity", size=10, color=get_text_secondary(dark_mode)),
                    ],
                    spacing=0,
                ),
            ],
            spacing=12,
        ),
        padding=ft.Padding(left=4, right=4, top=16, bottom=20),
    )

    # ── Nav items ─────────────────────────────────────────────────────────
    nav_controls: list[ft.Control] = [logo]
    for sec in NAV_SECTIONS:
        nav_controls.append(
            ft.Container(
                content=ft.Text(
                    sec["section"].upper(),
                    size=10,
                    weight=ft.FontWeight.BOLD,
                    color=get_text_secondary(dark_mode),
                ),
                padding=ft.Padding(left=14, right=0, top=10, bottom=2),
            )
        )
        for item in sec["items"]:
            nav_controls.append(nav_item(item))

    settings_item = nav_item({"key": "settings", "label": "Settings", "icon": ft.Icons.SETTINGS_ROUNDED})

    bc = get_border_color(dark_mode)
    sidebar_col = ft.Column(
        [
            ft.Column(nav_controls, scroll=ft.ScrollMode.AUTO, expand=True),
            ft.Divider(height=1, color=bc),
            settings_item,
        ],
        expand=True,
        spacing=0,
    )

    return ft.Container(
        content=sidebar_col,
        width=240,
        padding=ft.Padding(left=10, right=10, top=8, bottom=8),
        bgcolor=get_card_bg(dark_mode),
        border=ft.Border(right=ft.BorderSide(1, bc)),
    )
