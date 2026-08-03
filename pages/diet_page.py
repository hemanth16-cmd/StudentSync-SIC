"""
Diet Page View for StudentSync (Python Flet 0.86+)
Full CRUD implementation with SQLite persistence.
"""

import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary, get_border_color
from app.database import Database
from components.common_widgets import create_card, create_stat_card, create_section_header, create_badge, create_empty_state
from components.modals import show_toast


def diet_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    name_f = ft.TextField(
        hint_text="Meal name (e.g. Oatmeal & Banana)",
        expand=True,
        height=44,
        border_radius=10
    )
    cal_f = ft.TextField(
        hint_text="Calories",
        width=110,
        height=44,
        border_radius=10,
        keyboard_type=ft.KeyboardType.NUMBER
    )
    meal_dd = ft.Dropdown(
        value="breakfast",
        options=[ft.dropdown.Option(k, k.capitalize()) for k in ["breakfast", "lunch", "dinner", "snack"]],
        width=140,
        border_radius=10,
    )

    diet_col = ft.Column(spacing=10)

    cal_stat_text = ft.Text("0 kcal", size=26, weight=ft.FontWeight.BOLD, color=get_text_primary(dark_mode))
    meal_stat_text = ft.Text("0", size=26, weight=ft.FontWeight.BOLD, color=get_text_primary(dark_mode))
    progress_bar = ft.ProgressBar(value=0.0, color=AppColors.GREEN, bgcolor=f"{AppColors.GREEN}30", height=8, border_radius=4)

    def _today_cals():
        today = Database.today_str()
        logs = [d for d in Database.get_diet_logs() if d.get("date") == today]
        cals = sum(d.get("calories", 0) for d in logs)
        return cals, len(logs)

    def _open_edit_dialog(d: dict):
        edit_name = ft.TextField(value=d.get("name", ""), label="Meal Name", border_radius=10)
        edit_cals = ft.TextField(
            value=str(d.get("calories", 0)),
            label="Calories (kcal)",
            border_radius=10,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        edit_meal_dd = ft.Dropdown(
            value=d.get("meal", "breakfast"),
            options=[ft.dropdown.Option(k, k.capitalize()) for k in ["breakfast", "lunch", "dinner", "snack"]],
            label="Meal Type",
            border_radius=10,
        )

        def save_edit(e):
            if not edit_name.value or not edit_name.value.strip():
                show_toast(page, "Meal name cannot be empty", "error")
                return
            if not edit_cals.value or not edit_cals.value.isdigit():
                show_toast(page, "Enter valid integer calories", "error")
                return

            Database.update_diet_entry(
                d["id"],
                {
                    "name": edit_name.value.strip(),
                    "calories": int(edit_cals.value),
                    "meal": edit_meal_dd.value or "breakfast"
                }
            )
            dlg.open = False
            page.update()
            show_toast(page, "Meal entry updated!", "success")
            _rebuild()
            page.update()

        def close_edit(e):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Meal Entry", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    [edit_name, edit_cals, edit_meal_dd],
                    spacing=12,
                    tight=True
                ),
                width=360,
                padding=10
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_edit),
                ft.ElevatedButton(
                    "Save Changes",
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=AppColors.GREEN,
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=save_edit
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def _delete(log_id: str):
        Database.delete_diet_entry(log_id)
        show_toast(page, "Meal entry deleted", "info")
        _rebuild()
        page.update()

    def _rebuild():
        cals, meals = _today_cals()
        cal_stat_text.value = f"{cals} kcal"
        meal_stat_text.value = str(meals)
        progress_bar.value = min(cals / 2000.0, 1.0)

        logs = Database.get_diet_logs()
        diet_col.controls.clear()
        if not logs:
            diet_col.controls.append(
                create_empty_state(ft.Icons.RESTAURANT_MENU_OUTLINED, "No meals logged yet. Track your intake!", dark_mode)
            )
            return

        for d in logs:
            log_id = d["id"]
            meal_type = d.get("meal", "breakfast").capitalize()
            calories = d.get("calories", 0)

            meal_card = create_card(
                content=ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(ft.Icons.RESTAURANT_ROUNDED, color=AppColors.GREEN, size=20),
                                    padding=10,
                                    bgcolor=f"{AppColors.GREEN}22",
                                    border_radius=10,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            d["name"],
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=get_text_primary(dark_mode)
                                        ),
                                        ft.Text(
                                            f"{meal_type}  ·  {d.get('date', '')}",
                                            size=12,
                                            color=get_text_secondary(dark_mode),
                                        ),
                                    ],
                                    spacing=3,
                                    expand=True,
                                ),
                            ],
                            spacing=12,
                            expand=True,
                        ),
                        ft.Row(
                            [
                                create_badge(
                                    f"{calories} kcal",
                                    bgcolor=f"{AppColors.GREEN}22",
                                    text_color=AppColors.GREEN
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_size=18,
                                    icon_color=get_text_secondary(dark_mode),
                                    tooltip="Edit Meal",
                                    on_click=lambda e, item=d: _open_edit_dialog(item)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINED,
                                    icon_size=18,
                                    icon_color=AppColors.RED,
                                    tooltip="Delete Meal",
                                    on_click=lambda e, lid=log_id: _delete(lid)
                                ),
                            ],
                            spacing=6,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=14,
                dark_mode=dark_mode,
            )
            diet_col.controls.append(meal_card)

    def _add(e):
        if not name_f.value or not name_f.value.strip():
            show_toast(page, "Please enter a meal name", "error")
            return
        if not cal_f.value or not cal_f.value.isdigit():
            show_toast(page, "Please enter a valid calorie amount", "error")
            return

        Database.add_diet_entry(
            name=name_f.value.strip(),
            calories=int(cal_f.value),
            meal=meal_dd.value or "breakfast",
        )
        name_f.value = ""
        cal_f.value = ""
        show_toast(page, "Meal logged successfully!", "success")
        _rebuild()
        page.update()

    _rebuild()

    stats_card = create_card(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Today's Intake", size=13, weight=ft.FontWeight.W_600, color=get_text_secondary(dark_mode)),
                                cal_stat_text,
                                ft.Text("Daily Goal: 2000 kcal", size=12, color=get_text_secondary(dark_mode)),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Column(
                            [
                                ft.Text("Meals Logged", size=13, weight=ft.FontWeight.W_600, color=get_text_secondary(dark_mode)),
                                meal_stat_text,
                                ft.Text("Total Entries", size=12, color=get_text_secondary(dark_mode)),
                            ],
                            spacing=2,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=8),
                progress_bar,
            ],
            spacing=4,
        ),
        padding=18,
        dark_mode=dark_mode,
    )

    add_card = create_card(
        content=ft.Row(
            [
                name_f,
                cal_f,
                meal_dd,
                ft.ElevatedButton(
                    "Log Meal",
                    icon=ft.Icons.RESTAURANT,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=AppColors.GREEN,
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    on_click=_add,
                    height=44,
                )
            ],
            spacing=10,
            wrap=True,
        ),
        padding=16,
        dark_mode=dark_mode,
    )

    return ft.Column(
        [
            create_section_header(
                "Diet & Nutrition Tracker",
                "Track daily calorie intake, log your meals, and stay healthy",
                dark_mode=dark_mode
            ),
            stats_card,
            add_card,
            diet_col,
        ],
        spacing=16,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
