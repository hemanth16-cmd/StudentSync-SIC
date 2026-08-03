"""
Attendance Page View for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary
from app.database import Database
from components.common_widgets import create_card, create_section_header, create_badge, create_empty_state, create_progress_bar
from components.modals import show_toast


def attendance_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    att_col = ft.Column(spacing=12)

    def _rebuild():
        subjects = Database.get_subjects()
        att_col.controls.clear()
        if not subjects:
            att_col.controls.append(
                create_empty_state(ft.Icons.HOW_TO_REG_OUTLINED,
                                   "Register subjects first to track attendance", dark_mode)
            )
            return
        for s in subjects:
            attended = s.get("attended", 0)
            bunked   = s.get("bunked", 0)
            total    = attended + bunked
            pct      = (attended / total * 100) if total > 0 else 100.0
            color    = AppColors.GREEN if pct >= 75 else AppColors.RED

            att_col.controls.append(
                create_card(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(s["name"], size=15, weight=ft.FontWeight.BOLD,
                                                    color=get_text_primary(dark_mode)),
                                            ft.Text(
                                                f"Code: {s.get('code','—')}  ·  {attended}/{total} classes attended",
                                                size=12, color=get_text_secondary(dark_mode),
                                            ),
                                        ],
                                        spacing=2, expand=True,
                                    ),
                                    create_badge(f"{pct:.0f}%", bgcolor=f"{color}22", text_color=color),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            create_progress_bar(pct / 100.0, color=color),
                            ft.Divider(height=1),
                            ft.Row(
                                [
                                    ft.Text("Mark Today:", size=12, weight=ft.FontWeight.W_600,
                                            color=get_text_secondary(dark_mode)),
                                    ft.OutlinedButton(
                                        "Present",
                                        icon=ft.Icons.CHECK,
                                        style=ft.ButtonStyle(color=AppColors.GREEN),
                                        on_click=lambda e, sid=s["id"]: _mark(sid, "present"),
                                    ),
                                    ft.OutlinedButton(
                                        "Absent",
                                        icon=ft.Icons.CLOSE,
                                        style=ft.ButtonStyle(color=AppColors.RED),
                                        on_click=lambda e, sid=s["id"]: _mark(sid, "absent"),
                                    ),
                                    ft.OutlinedButton(
                                        "Late",
                                        icon=ft.Icons.SCHEDULE,
                                        style=ft.ButtonStyle(color=AppColors.ORANGE),
                                        on_click=lambda e, sid=s["id"]: _mark(sid, "late"),
                                    ),
                                ],
                                spacing=10,
                            ),
                        ],
                        spacing=12,
                    ),
                    padding=16, dark_mode=dark_mode,
                )
            )

    def _mark(sid, status):
        Database.mark_attendance(sid, Database.today_str(), status)
        show_toast(page, f"Marked {status.capitalize()} for today", "success")
        _rebuild(); page.update()

    _rebuild()

    return ft.Column(
        [
            create_section_header("Attendance Tracker",
                                  "Maintain the 75% attendance target for each subject",
                                  dark_mode=dark_mode),
            att_col,
        ],
        spacing=16, expand=True, scroll=ft.ScrollMode.AUTO,
    )
