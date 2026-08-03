import flet as ft


def notes_view():
    return ft.Column(
        controls=[
            ft.Text(
                "📝 Notes",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                "Your notes will appear here.",
                size=15,
                color="#64748B",
            ),
        ]
    )