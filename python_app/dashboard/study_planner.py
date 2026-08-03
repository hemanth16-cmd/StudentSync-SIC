import flet as ft


def study_planner_view():
    return ft.Column(
        controls=[
            ft.Text(
                "🤖 AI Study Planner",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                "Your personalized study plan will appear here.",
                size=15,
                color="#64748B",
            ),
        ]
    )