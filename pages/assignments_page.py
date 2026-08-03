"""
Assignments Page View for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary
from app.database import Database
from components.common_widgets import create_card, create_section_header, create_badge, create_empty_state
from components.modals import show_toast

P_COLOR = {"high": AppColors.RED, "medium": AppColors.ORANGE, "low": AppColors.BLUE}


def assignments_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    title_f   = ft.TextField(hint_text="Assignment Title", expand=True, height=42, border_radius=10)
    subject_f = ft.TextField(hint_text="Subject", width=140, height=42, border_radius=10)
    date_f    = ft.TextField(hint_text="Due (YYYY-MM-DD)", width=160, height=42, border_radius=10)
    prio_dd   = ft.Dropdown(
        value="medium",
        options=[ft.dropdown.Option(k, k.capitalize()) for k in ["low", "medium", "high"]],
        width=120, border_radius=10,
    )

    asgn_col = ft.Column(spacing=10)

    def _rebuild():
        asgns = Database.get_assignments()
        asgn_col.controls.clear()
        if not asgns:
            asgn_col.controls.append(
                create_empty_state(ft.Icons.ASSIGNMENT_LATE_OUTLINED, "No assignments yet", dark_mode)
            )
            return
        for a in asgns:
            pc = P_COLOR.get(a.get("priority", "medium"), AppColors.ORANGE)
            asgn_col.controls.append(
                create_card(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(a["title"], size=14, weight=ft.FontWeight.BOLD,
                                            color=get_text_primary(dark_mode)),
                                    ft.Text(
                                        f"{a.get('subject','—')}  ·  Due: {a.get('dueDate','TBD')}",
                                        size=12, color=get_text_secondary(dark_mode),
                                    ),
                                ],
                                spacing=3, expand=True,
                            ),
                            create_badge(a.get("priority", "medium").upper(),
                                         bgcolor=f"{pc}22", text_color=pc),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=AppColors.RED, icon_size=18,
                                on_click=lambda e, aid=a["id"]: _delete(aid),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=14, dark_mode=dark_mode,
                )
            )

    def _add(e):
        if not title_f.value or not title_f.value.strip():
            show_toast(page, "Please enter a title", "error")
            return
        Database.add_assignment(
            title=title_f.value.strip(),
            subject=subject_f.value.strip(),
            due_date=date_f.value.strip(),
            priority=prio_dd.value or "medium",
        )
        title_f.value = subject_f.value = date_f.value = ""
        show_toast(page, "Assignment added!", "success")
        _rebuild(); page.update()

    def _delete(aid):
        Database.delete_assignment(aid)
        show_toast(page, "Assignment deleted", "info")
        _rebuild(); page.update()

    _rebuild()

    add_card = create_card(
        content=ft.Row(
            [title_f, subject_f, date_f, prio_dd,
             ft.ElevatedButton(
                 "Add",
                 icon=ft.Icons.ASSIGNMENT_TURNED_IN,
                 style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.BLUE,
                                      shape=ft.RoundedRectangleBorder(radius=10)),
                 on_click=_add, height=42,
             )],
            spacing=10, wrap=True,
        ),
        padding=16, dark_mode=dark_mode,
    )

    return ft.Column(
        [
            create_section_header("Assignments", "Track homework and deadline status", dark_mode=dark_mode),
            add_card,
            asgn_col,
        ],
        spacing=16, expand=True, scroll=ft.ScrollMode.AUTO,
    )
