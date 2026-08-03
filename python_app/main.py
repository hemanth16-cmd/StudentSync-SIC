import flet as ft

from dashboard.dashboard import dashboard_view
from dashboard.timetable import timetable_view
from dashboard.attendance import attendance_view
from dashboard.notes import notes_view
from dashboard.study_planner import study_planner_view


def main(page: ft.Page):
    page.title = "StudentSync"
    page.window.width = 1200
    page.window.height = 750
    page.padding = 0

    # ---------- COLORS ----------
    PRIMARY = "#4F46E5"
    BACKGROUND = "#F8FAFC"
    CARD = "#FFFFFF"
    TEXT = "#1E293B"
    MUTED = "#64748B"

    page.bgcolor = BACKGROUND

    # ---------- MAIN CONTENT AREA ----------
    content_area = ft.Container(
        expand=True,
        padding=30,
    )

    # ---------- PAGE NAVIGATION ----------
    def show_page(view):
        content_area.content = view(page)
        page.update()

    # ---------- SIDEBAR ----------
    sidebar = ft.Container(
        width=220,
        bgcolor=CARD,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text(
                    "StudentSync",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=PRIMARY,
                ),

                ft.Divider(),

                ft.TextButton(
                    "🏠  Dashboard",
                    on_click=lambda e: show_page(dashboard_view),
                ),

                ft.TextButton(
                    "📅  Timetable",
                    on_click=lambda e: show_page(timetable_view),
                ),

                ft.TextButton(
                    "📊  Attendance",
                    on_click=lambda e: show_page(attendance_view),
                ),

                ft.TextButton(
                    "📝  Notes",
                    on_click=lambda e: show_page(notes_view),
                ),

                ft.TextButton(
                    "🤖  Study Planner",
                    on_click=lambda e: show_page(study_planner_view),
                ),
            ],
        ),
    )

    # ---------- CONTENT ----------
    content = ft.Container(
        expand=True,
        content=content_area,
    )

    # ---------- INITIAL PAGE ----------
    show_page(dashboard_view)

    # ---------- APP LAYOUT ----------
    page.add(
        ft.Row(
            controls=[
                sidebar,
                content,
            ],
            expand=True,
            spacing=0,
        )
    )


ft.run(main)