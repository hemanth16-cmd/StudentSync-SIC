"""
Workout Page View for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary
from app.database import Database
from components.common_widgets import create_card, create_section_header, create_badge, create_empty_state
from components.modals import show_toast


def workout_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    name_f = ft.TextField(hint_text="Workout (e.g. Upper Body Gym)", expand=True, height=42, border_radius=10)
    dur_f  = ft.TextField(hint_text="Mins", width=90, height=42, border_radius=10)
    cal_f  = ft.TextField(hint_text="Calories", width=110, height=42, border_radius=10)
    type_dd = ft.Dropdown(
        value="strength",
        options=[ft.dropdown.Option(k, k.capitalize()) for k in ["strength", "cardio", "yoga", "sports", "other"]],
        width=130, border_radius=10,
    )

    wk_col = ft.Column(spacing=10)

    def _rebuild():
        logs = Database.get_workouts()
        wk_col.controls.clear()
        if not logs:
            wk_col.controls.append(
                create_empty_state(ft.Icons.FITNESS_CENTER_OUTLINED, "No workouts logged yet", dark_mode)
            )
            return
        for w in logs:
            wk_col.controls.append(
                create_card(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(w["name"], size=14, weight=ft.FontWeight.BOLD,
                                            color=get_text_primary(dark_mode)),
                                    ft.Text(f"{w.get('type','').capitalize()}  ·  {w.get('date','')}",
                                            size=12, color=get_text_secondary(dark_mode)),
                                ],
                                spacing=3, expand=True,
                            ),
                            create_badge(f"⏱ {w.get('duration',0)} min",
                                         bgcolor=f"{AppColors.GREEN}22", text_color=AppColors.GREEN),
                            create_badge(f"🔥 {w.get('calories',0)} kcal",
                                         bgcolor=f"{AppColors.ORANGE}22", text_color=AppColors.ORANGE),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=14, dark_mode=dark_mode,
                )
            )

    def _add(e):
        if not name_f.value or not name_f.value.strip() or not (dur_f.value or "").isdigit():
            show_toast(page, "Enter workout name and valid duration", "error")
            return
        Database.add_workout(
            name=name_f.value.strip(),
            workout_type=type_dd.value or "strength",
            duration=int(dur_f.value),
            calories=int(cal_f.value) if (cal_f.value or "").isdigit() else 0,
        )
        name_f.value = dur_f.value = cal_f.value = ""
        show_toast(page, "Workout logged!", "success")
        _rebuild(); page.update()

    _rebuild()

    add_card = create_card(
        content=ft.Row(
            [name_f, dur_f, cal_f, type_dd,
             ft.ElevatedButton(
                 "Log Workout",
                 icon=ft.Icons.FITNESS_CENTER,
                 style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.GREEN,
                                      shape=ft.RoundedRectangleBorder(radius=10)),
                 on_click=_add, height=42,
             )],
            spacing=10, wrap=True,
        ),
        padding=16, dark_mode=dark_mode,
    )

    return ft.Column(
        [
            create_section_header("Workout & Fitness", "Log exercise sessions and track activity", dark_mode=dark_mode),
            add_card,
            wk_col,
        ],
        spacing=16, expand=True, scroll=ft.ScrollMode.AUTO,
    )
