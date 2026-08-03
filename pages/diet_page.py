"""
Diet Page View for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary
from app.database import Database
from components.common_widgets import create_card, create_stat_card, create_section_header, create_badge, create_empty_state
from components.modals import show_toast


def diet_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    name_f = ft.TextField(hint_text="Meal name (e.g. Oatmeal & Banana)", expand=True, height=42, border_radius=10)
    cal_f  = ft.TextField(hint_text="Calories", width=110, height=42, border_radius=10)
    meal_dd = ft.Dropdown(
        value="breakfast",
        options=[ft.dropdown.Option(k, k.capitalize()) for k in ["breakfast", "lunch", "dinner", "snack"]],
        width=130, border_radius=10,
    )

    diet_col = ft.Column(spacing=10)

    def _today_cals():
        today = Database.today_str()
        logs  = [d for d in Database.get_diet_logs() if d.get("date") == today]
        return sum(d.get("calories", 0) for d in logs), len(logs)

    cal_stat_text  = ft.Text("0 kcal", size=26, weight=ft.FontWeight.BOLD, color=get_text_primary(dark_mode))
    meal_stat_text = ft.Text("0",      size=26, weight=ft.FontWeight.BOLD, color=get_text_primary(dark_mode))

    def _rebuild():
        cals, meals = _today_cals()
        cal_stat_text.value  = f"{cals} kcal"
        meal_stat_text.value = str(meals)

        logs = Database.get_diet_logs()
        diet_col.controls.clear()
        if not logs:
            diet_col.controls.append(
                create_empty_state(ft.Icons.RESTAURANT_MENU_OUTLINED, "No meals logged yet", dark_mode)
            )
            return
        for d in logs:
            diet_col.controls.append(
                create_card(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(d["name"], size=14, weight=ft.FontWeight.BOLD,
                                            color=get_text_primary(dark_mode)),
                                    ft.Text(
                                        f"{d.get('meal','').capitalize()}  ·  {d.get('date','')}",
                                        size=12, color=get_text_secondary(dark_mode),
                                    ),
                                ],
                                spacing=3, expand=True,
                            ),
                            create_badge(f"{d.get('calories',0)} kcal",
                                         bgcolor=f"{AppColors.GREEN}22", text_color=AppColors.GREEN),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=14, dark_mode=dark_mode,
                )
            )

    def _add(e):
        if not name_f.value or not name_f.value.strip() or not (cal_f.value or "").isdigit():
            show_toast(page, "Enter meal name and valid calorie count", "error")
            return
        Database.add_diet_entry(
            name=name_f.value.strip(),
            calories=int(cal_f.value),
            meal=meal_dd.value or "breakfast",
        )
        name_f.value = cal_f.value = ""
        show_toast(page, "Meal logged!", "success")
        _rebuild(); page.update()

    _rebuild()

    stats_row = ft.Row(
        [
            create_stat_card("Today's Calories", cal_stat_text.value,  "Goal: 2000 kcal",  ft.Icons.LOCAL_FIRE_DEPARTMENT, AppColors.GREEN, dark_mode),
            create_stat_card("Meals Logged",     meal_stat_text.value, "Total entries",     ft.Icons.FLATWARE,              AppColors.ORANGE, dark_mode),
        ],
        spacing=16,
    )

    add_card = create_card(
        content=ft.Row(
            [name_f, cal_f, meal_dd,
             ft.ElevatedButton(
                 "Log Meal",
                 icon=ft.Icons.RESTAURANT,
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
            create_section_header("Diet & Nutrition", "Track daily calorie intake and meals", dark_mode=dark_mode),
            stats_row,
            add_card,
            diet_col,
        ],
        spacing=16, expand=True, scroll=ft.ScrollMode.AUTO,
    )
