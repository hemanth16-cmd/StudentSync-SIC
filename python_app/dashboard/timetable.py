import flet as ft


def timetable_view():
    return ft.Column(
        controls=[
            ft.Text(
                "📅 Timetable",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                "Your weekly class schedule will appear here.",
                size=15,
                color="#64748B",
            ),
        ]
    )