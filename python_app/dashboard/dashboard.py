import flet as ft


def dashboard_view(page):
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