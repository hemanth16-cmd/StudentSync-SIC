"""
Workout Page View for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from datetime import date, timedelta
from app.theme import AppColors, get_text_primary, get_text_secondary, get_border_color
from app.database import Database
from components.common_widgets import create_card, create_section_header, create_badge, create_empty_state, create_stat_card
from components.modals import show_toast


def workout_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    name_f = ft.TextField(hint_text="Workout Name", expand=True, height=42, border_radius=10)
    dur_f  = ft.TextField(hint_text="Mins", width=80, height=42, border_radius=10)
    cal_f  = ft.TextField(hint_text="Calories", width=100, height=42, border_radius=10)
    type_dd = ft.Dropdown(
        value="strength",
        options=[ft.dropdown.Option(k, k.capitalize()) for k in ["strength", "cardio", "yoga", "sports", "other"]],
        width=120, border_radius=10,
    )

    # Exercise fields
    ex_name = ft.TextField(hint_text="Exercise Name", expand=True, height=38, border_radius=8, text_size=13)
    ex_sets = ft.TextField(hint_text="Sets", width=60, height=38, border_radius=8, text_size=13)
    ex_reps = ft.TextField(hint_text="Reps", width=60, height=38, border_radius=8, text_size=13)
    ex_weight = ft.TextField(hint_text="Weight", width=70, height=38, border_radius=8, text_size=13)
    ex_dur = ft.TextField(hint_text="Mins", width=60, height=38, border_radius=8, text_size=13)

    exercises_list = []
    ex_list_col = ft.Column(spacing=4)

    wk_col = ft.Column(spacing=10)
    stats_col = ft.Row(spacing=16, wrap=True)

    def _update_exercise_list():
        ex_list_col.controls.clear()
        for i, ex in enumerate(exercises_list):
            lbl = f"{ex['name']} - {ex['sets']} sets x {ex['reps']} reps"
            if ex.get('weight'): lbl += f" @ {ex['weight']}"
            if ex.get('duration'): lbl += f" ({ex['duration']} min)"
            
            ex_list_col.controls.append(
                ft.Row([
                    ft.Text(lbl, size=12, color=get_text_secondary(dark_mode)),
                    ft.IconButton(ft.Icons.CLOSE, icon_size=14, icon_color=AppColors.RED,
                                  on_click=lambda e, idx=i: _remove_ex(idx))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        page.update()

    def _add_ex(e):
        if not ex_name.value:
            show_toast(page, "Exercise name required", "error")
            return
        exercises_list.append({
            "name": ex_name.value,
            "sets": ex_sets.value or "1",
            "reps": ex_reps.value or "1",
            "weight": ex_weight.value,
            "duration": ex_dur.value
        })
        ex_name.value = ex_sets.value = ex_reps.value = ex_weight.value = ex_dur.value = ""
        _update_exercise_list()

    def _remove_ex(idx):
        exercises_list.pop(idx)
        _update_exercise_list()

    def _rebuild():
        logs = Database.get_workouts()
        wk_col.controls.clear()
        stats_col.controls.clear()
        
        # Calculate stats
        streak = Database.get_workout_streak()
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        this_week_count = 0
        total_mins = 0
        
        for w in logs:
            total_mins += w.get("duration", 0)
            if w.get("date") and w.get("date") >= start_of_week.isoformat():
                this_week_count += 1
                
        stats_col.controls = [
            create_stat_card("Current Streak", f"{streak} Days", "🔥 keep it up", ft.Icons.LOCAL_FIRE_DEPARTMENT, AppColors.ORANGE, dark_mode),
            create_stat_card("This Week", str(this_week_count), "Workouts", ft.Icons.FITNESS_CENTER, AppColors.GREEN, dark_mode),
            create_stat_card("Total Active", f"{total_mins} min", "All time", ft.Icons.TIMER, AppColors.BLUE, dark_mode),
        ]

        if not logs:
            wk_col.controls.append(
                create_empty_state(ft.Icons.FITNESS_CENTER_OUTLINED, "No workouts logged yet", dark_mode)
            )
            return
            
        for w in logs:
            ex_details = []
            for ex in w.get("exercises", []):
                lbl = f"• {ex['name']}: {ex['sets']}x{ex['reps']}"
                if ex.get('weight'): lbl += f" @ {ex['weight']}"
                ex_details.append(ft.Text(lbl, size=11, color=get_text_secondary(dark_mode)))

            wk_col.controls.append(
                create_card(
                    content=ft.Column([
                        ft.Row(
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
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=AppColors.RED,
                                    icon_size=18,
                                    on_click=lambda e, wid=w["id"]: _delete(wid),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Column(ex_details, spacing=2) if ex_details else ft.Container()
                    ], spacing=8),
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
            exercises=list(exercises_list)
        )
        name_f.value = dur_f.value = cal_f.value = ""
        exercises_list.clear()
        _update_exercise_list()
        show_toast(page, "Workout logged!", "success")
        _rebuild(); page.update()

    def _delete(wid):
        Database.delete_workout(wid)
        show_toast(page, "Workout deleted", "info")
        _rebuild()
        page.update()

    _rebuild()

    add_card = create_card(
        content=ft.Column([
            ft.Text("Log New Workout", size=14, weight=ft.FontWeight.BOLD, color=get_text_primary(dark_mode)),
            ft.Row(
                [name_f, dur_f, cal_f, type_dd],
                spacing=10, wrap=True,
            ),
            ft.Divider(height=1, color=get_border_color(dark_mode)),
            ft.Text("Exercises", size=12, weight=ft.FontWeight.W_600, color=get_text_secondary(dark_mode)),
            ex_list_col,
            ft.Row([
                ex_name, ex_sets, ex_reps, ex_weight, ex_dur,
                ft.IconButton(ft.Icons.ADD_CIRCLE, icon_color=AppColors.BLUE, on_click=_add_ex)
            ], wrap=True),
            ft.Row([
                ft.ElevatedButton(
                     "Log Workout",
                     icon=ft.Icons.FITNESS_CENTER,
                     style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.GREEN,
                                          shape=ft.RoundedRectangleBorder(radius=10)),
                     on_click=_add, height=42,
                 )
            ], alignment=ft.MainAxisAlignment.END)
        ], spacing=10),
        padding=16, dark_mode=dark_mode,
    )

    return ft.Column(
        [
            create_section_header("Workout Tracker", "Log exercise sessions, track streaks & stats", dark_mode=dark_mode),
            stats_col,
            add_card,
            wk_col,
        ],
        spacing=16, expand=True, scroll=ft.ScrollMode.AUTO,
    )
