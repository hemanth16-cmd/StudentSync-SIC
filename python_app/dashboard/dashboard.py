import flet as ft


def dashboard_view():
    return ft.Column(
        controls=[
            ft.Text(
                "Good morning! 👋",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                "Here's your academic overview.",
                size=15,
                color="#64748B",
            ),
        ]
    )