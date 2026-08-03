"""
Subjects Page View for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary, get_border_color
from app.database import Database
from components.common_widgets import create_card, create_section_header, create_badge, create_empty_state, create_progress_bar
from components.modals import show_toast


def subjects_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    name_f    = ft.TextField(hint_text="Subject Name (e.g. Data Structures)", expand=True, height=42, border_radius=10)
    code_f    = ft.TextField(hint_text="Code (e.g. CS201)", width=120, height=42, border_radius=10)
    teacher_f = ft.TextField(hint_text="Instructor", width=140, height=42, border_radius=10)
    credits_f = ft.TextField(value="3", hint_text="Credits", width=80, height=42, border_radius=10)
    room_f    = ft.TextField(hint_text="Room", width=110, height=42, border_radius=10)

    subj_col = ft.Column(spacing=12)

    def _rebuild():
        subjects = Database.get_subjects()
        subj_col.controls.clear()
        if not subjects:
            subj_col.controls.append(
                create_empty_state(ft.Icons.BOOK_OUTLINED, "No subjects registered yet", dark_mode)
            )
            return
        for s in subjects:
            attended = s.get("attended", 0)
            bunked   = s.get("bunked", 0)
            total    = attended + bunked
            pct      = (attended / total * 100) if total > 0 else 100.0
            color    = AppColors.GREEN if pct >= 75 else AppColors.RED

            subj_col.controls.append(
                create_card(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(s.get("emoji", "📚"), size=24),
                                            ft.Column(
                                                [
                                                    ft.Text(s["name"], size=15, weight=ft.FontWeight.BOLD,
                                                            color=get_text_primary(dark_mode)),
                                                    ft.Text(
                                                        f"{s.get('code','—')}  ·  {s.get('teacher','—')}",
                                                        size=12, color=get_text_secondary(dark_mode),
                                                    ),
                                                ],
                                                spacing=2,
                                            ),
                                        ],
                                        spacing=12,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color=AppColors.RED,
                                        on_click=lambda e, sid=s["id"]: _delete(sid),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Row(
                                [
                                    create_badge(f"{s.get('credits',3)} cr", bgcolor=f"{AppColors.BLUE}22",  text_color=AppColors.BLUE),
                                    create_badge(f"Room {s.get('room','—')}",  bgcolor=f"{AppColors.PURPLE}22", text_color=AppColors.PURPLE),
                                    create_badge(f"Att. {pct:.0f}%",           bgcolor=f"{color}22",          text_color=color),
                                ],
                                spacing=8,
                            ),
                            create_progress_bar(pct / 100.0, color=color),
                        ],
                        spacing=12,
                    ),
                    padding=16,
                    dark_mode=dark_mode,
                )
            )

    def _add(e):
        if not name_f.value or not name_f.value.strip():
            show_toast(page, "Please enter a subject name", "error")
            return
        Database.add_subject(
            name=name_f.value.strip(),
            code=code_f.value.strip(),
            teacher=teacher_f.value.strip(),
            credits=int(credits_f.value) if (credits_f.value or "").isdigit() else 3,
            room=room_f.value.strip(),
        )
        name_f.value = code_f.value = teacher_f.value = room_f.value = ""
        show_toast(page, "Subject added!", "success")
        _rebuild()
        page.update()

    def _delete(sid):
        Database.delete_subject(sid)
        show_toast(page, "Subject deleted", "info")
        _rebuild()
        page.update()

    _rebuild()

    add_card = create_card(
        content=ft.Row(
            [name_f, code_f, teacher_f, credits_f, room_f,
             ft.ElevatedButton(
                 "Add Subject",
                 icon=ft.Icons.BOOKMARK_ADD,
                 style=ft.ButtonStyle(
                     color=ft.Colors.WHITE,
                     bgcolor=AppColors.BLUE,
                     shape=ft.RoundedRectangleBorder(radius=10),
                 ),
                 on_click=_add, height=42,
             )],
            spacing=10, wrap=True,
        ),
        padding=16, dark_mode=dark_mode,
    )

    return ft.Column(
        [
            create_section_header("Academic Subjects", "Manage enrolled courses and attendance", dark_mode=dark_mode),
            add_card,
            subj_col,
        ],
        spacing=16, expand=True, scroll=ft.ScrollMode.AUTO,
    )
