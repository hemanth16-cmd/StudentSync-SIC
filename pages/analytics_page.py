"""
Analytics Page View for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary, get_border_color
from app.database import Database
from components.common_widgets import create_card, create_stat_card, create_section_header, create_progress_bar


def analytics_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    todos      = Database.get_todos()
    habits     = Database.get_habits()
    subjects   = Database.get_subjects()
    sleep_logs = Database.get_sleep_logs()

    done_todos = sum(1 for t in todos if t.get("completed"))
    todo_rate  = (done_todos / len(todos) * 100) if todos else 0.0
    avg_sleep  = (sum(l.get("duration", 0) for l in sleep_logs) / len(sleep_logs)) if sleep_logs else 0.0

    # Simple productivity index
    score = int(
        (todo_rate * 0.4)
        + (min(len(habits) * 8, 24))
        + (min(avg_sleep / 8.0 * 20, 20))
        + (min(len(subjects) * 4, 16))
    )
    score = min(score, 100)

    stats_grid = ft.ResponsiveRow(
        [
            ft.Container(
                create_stat_card("Productivity Score", f"{score} / 100", "Overall index",
                                 ft.Icons.SPEED, AppColors.PURPLE, dark_mode),
                col={"sm": 12, "md": 6, "lg": 3},
            ),
            ft.Container(
                create_stat_card("Tasks Done", f"{done_todos}/{len(todos)}",
                                 f"{todo_rate:.0f}% completion",
                                 ft.Icons.TASK_ALT, AppColors.GREEN, dark_mode),
                col={"sm": 12, "md": 6, "lg": 3},
            ),
            ft.Container(
                create_stat_card("Active Habits", str(len(habits)), "Habits tracked",
                                 ft.Icons.LOOP, AppColors.ORANGE, dark_mode),
                col={"sm": 12, "md": 6, "lg": 3},
            ),
            ft.Container(
                create_stat_card("Subjects", str(len(subjects)), "Enrolled courses",
                                 ft.Icons.SCHOOL, AppColors.BLUE, dark_mode),
                col={"sm": 12, "md": 6, "lg": 3},
            ),
        ],
        spacing=16,
    )

    perf_card = create_card(
        content=ft.Column(
            [
                ft.Text("Performance Overview", size=17, weight=ft.FontWeight.BOLD,
                        color=get_text_primary(dark_mode)),
                ft.Divider(height=1, color=get_border_color(dark_mode)),
                ft.Container(height=4),
                ft.Row(
                    [
                        ft.Text("Task Completion Rate", size=13, color=get_text_secondary(dark_mode), expand=True),
                        ft.Text(f"{todo_rate:.0f}%", size=13, weight=ft.FontWeight.BOLD, color=AppColors.GREEN),
                    ],
                ),
                create_progress_bar(todo_rate / 100.0, color=AppColors.GREEN),
                ft.Container(height=8),
                ft.Row(
                    [
                        ft.Text("Avg Sleep / Goal", size=13, color=get_text_secondary(dark_mode), expand=True),
                        ft.Text(f"{avg_sleep:.1f} / 8.0 hrs", size=13, weight=ft.FontWeight.BOLD, color=AppColors.INDIGO),
                    ],
                ),
                create_progress_bar(min(avg_sleep / 8.0, 1.0), color=AppColors.INDIGO),
                ft.Container(height=8),
                ft.Row(
                    [
                        ft.Text("Habit Coverage", size=13, color=get_text_secondary(dark_mode), expand=True),
                        ft.Text(f"{min(len(habits)*10, 100)}%", size=13, weight=ft.FontWeight.BOLD, color=AppColors.ORANGE),
                    ],
                ),
                create_progress_bar(min(len(habits) / 10.0, 1.0), color=AppColors.ORANGE),
            ],
            spacing=10,
        ),
        padding=20, dark_mode=dark_mode,
    )

    return ft.Column(
        [
            create_section_header("Analytics & Insights",
                                  "Visual summary of academic and lifestyle performance",
                                  dark_mode=dark_mode),
            stats_grid,
            ft.Container(height=4),
            perf_card,
        ],
        spacing=16, expand=True, scroll=ft.ScrollMode.AUTO,
    )
