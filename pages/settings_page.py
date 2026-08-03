"""
Settings Page View for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary, get_border_color
from app.database import Database
from components.common_widgets import create_card, create_section_header
from components.modals import show_toast


def settings_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    s = Database.get_settings()

    name_f    = ft.TextField(label="Full Name",                value=s.get("name", "Student"), expand=True, border_radius=10)
    college_f = ft.TextField(label="College / University",     value=s.get("college", ""),     expand=True, border_radius=10)
    gpa_f     = ft.TextField(label="GPA Scale (e.g. 10)",      value=str(s.get("gpaScale", 10)), width=160, border_radius=10)
    hours_f   = ft.TextField(label="Daily Study Goal (hours)", value=str(s.get("dailyGoalHours", 6)), width=200, border_radius=10)
    cal_f     = ft.TextField(label="Daily Calorie Goal",       value=str(s.get("calorieGoal", 2000)),  width=180, border_radius=10)
    sleep_f   = ft.TextField(label="Sleep Goal (hours)",       value=str(s.get("sleepGoal", 8)),       width=160, border_radius=10)

    def _save(e):
        Database.update_settings({
            "name":            (name_f.value    or "").strip() or "Student",
            "college":         (college_f.value or "").strip(),
            "gpaScale":        int(gpa_f.value)   if (gpa_f.value   or "").isdigit() else 10,
            "dailyGoalHours":  int(hours_f.value) if (hours_f.value or "").isdigit() else 6,
            "calorieGoal":     int(cal_f.value)   if (cal_f.value   or "").isdigit() else 2000,
            "sleepGoal":       int(sleep_f.value) if (sleep_f.value or "").isdigit() else 8,
        })
        show_toast(page, "Settings saved!", "success")

    profile_card = create_card(
        content=ft.Column(
            [
                ft.Text("User Profile", size=16, weight=ft.FontWeight.BOLD, color=get_text_primary(dark_mode)),
                ft.Divider(height=1, color=get_border_color(dark_mode)),
                ft.Row([name_f, college_f], spacing=12),
            ],
            spacing=12,
        ),
        padding=20, dark_mode=dark_mode,
    )

    academic_card = create_card(
        content=ft.Column(
            [
                ft.Text("Academic & Health Targets", size=16, weight=ft.FontWeight.BOLD, color=get_text_primary(dark_mode)),
                ft.Divider(height=1, color=get_border_color(dark_mode)),
                ft.Row([gpa_f, hours_f, cal_f, sleep_f], spacing=12, wrap=True),
            ],
            spacing=12,
        ),
        padding=20, dark_mode=dark_mode,
    )

    save_btn = ft.ElevatedButton(
        "Save Settings",
        icon=ft.Icons.SAVE_ROUNDED,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=AppColors.BLUE,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.Padding(left=24, right=24, top=12, bottom=12),
        ),
        on_click=_save,
    )

    return ft.Column(
        [
            create_section_header("Settings & Preferences", "Configure your profile and targets", dark_mode=dark_mode),
            profile_card,
            academic_card,
            ft.Row([save_btn], alignment=ft.MainAxisAlignment.END),
        ],
        spacing=16, expand=True, scroll=ft.ScrollMode.AUTO,
    )
