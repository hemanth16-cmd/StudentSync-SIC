import flet as ft


def attendance_view(page):
    return ft.Column(
        controls=[
            ft.Text(
                "📊 Attendance",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                "Your attendance information will appear here.",
                size=15,
                color="#64748B",
            ),
        ]
    )