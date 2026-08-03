"""
Notes Page View for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary, get_border_color
from app.database import Database
from components.common_widgets import create_card, create_section_header, create_empty_state
from components.modals import show_toast


def notes_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    title_f   = ft.TextField(hint_text="Note Title", expand=True, height=42, border_radius=10)
    subject_f = ft.TextField(hint_text="Subject / Tag", width=160, height=42, border_radius=10)
    content_f = ft.TextField(
        hint_text="Write your study note…",
        multiline=True, min_lines=2, max_lines=5,
        border_radius=10, expand=True,
    )

    notes_col = ft.Column(spacing=12)

    def _rebuild():
        notes = Database.get_notes()
        notes_col.controls.clear()
        if not notes:
            notes_col.controls.append(
                create_empty_state(ft.Icons.DESCRIPTION_OUTLINED, "No notes created yet", dark_mode)
            )
            return
        cards = []
        for n in notes:
            cards.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(n["title"], size=15, weight=ft.FontWeight.BOLD,
                                                    color=get_text_primary(dark_mode)),
                                            ft.Text(n.get("subject", "General"), size=11,
                                                    color=AppColors.BLUE, weight=ft.FontWeight.W_600),
                                        ],
                                        spacing=2, expand=True,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color=AppColors.RED, icon_size=18,
                                        on_click=lambda e, nid=n["id"]: _delete(nid),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(height=1, color=get_border_color(dark_mode)),
                            ft.Text(
                                n.get("content", ""),
                                size=13, color=get_text_secondary(dark_mode),
                                max_lines=4, overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(f"📅 {n.get('createdAt','')[:10]}", size=10,
                                    color=get_text_secondary(dark_mode)),
                        ],
                        spacing=8,
                    ),
                    padding=16,
                    bgcolor=None,
                    border=ft.Border(
                        top=ft.BorderSide(1, get_border_color(dark_mode)),
                        right=ft.BorderSide(1, get_border_color(dark_mode)),
                        bottom=ft.BorderSide(1, get_border_color(dark_mode)),
                        left=ft.BorderSide(1, get_border_color(dark_mode)),
                    ),
                    border_radius=14,
                    col={"sm": 12, "md": 6},
                )
            )
        notes_col.controls.append(ft.ResponsiveRow(cards, spacing=12))

    def _add(e):
        if not title_f.value or not title_f.value.strip():
            show_toast(page, "Please enter a title", "error")
            return
        Database.add_note(
            title=title_f.value.strip(),
            subject=subject_f.value.strip(),
            content=content_f.value.strip(),
        )
        title_f.value = subject_f.value = content_f.value = ""
        show_toast(page, "Note saved!", "success")
        _rebuild(); page.update()

    def _delete(nid):
        Database.delete_note(nid)
        show_toast(page, "Note deleted", "info")
        _rebuild(); page.update()

    _rebuild()

    add_card = create_card(
        content=ft.Column(
            [
                ft.Row(
                    [title_f, subject_f,
                     ft.ElevatedButton(
                         "Save Note",
                         icon=ft.Icons.NOTE_ADD,
                         style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.BLUE,
                                              shape=ft.RoundedRectangleBorder(radius=10)),
                         on_click=_add, height=42,
                     )],
                    spacing=10,
                ),
                content_f,
            ],
            spacing=10,
        ),
        padding=16, dark_mode=dark_mode,
    )

    return ft.Column(
        [
            create_section_header("Study Notes", "Organise quick-reference notes by course", dark_mode=dark_mode),
            add_card,
            notes_col,
        ],
        spacing=16, expand=True, scroll=ft.ScrollMode.AUTO,
    )
