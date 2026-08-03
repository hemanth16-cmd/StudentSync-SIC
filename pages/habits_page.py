"""
Habit Tracker Page View for StudentSync (Python Flet 0.86+)
Full CRUD implementation with SQLite persistence.
"""

import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary, get_border_color
from app.database import Database
from components.common_widgets import create_card, create_section_header, create_empty_state
from components.modals import show_toast


def habits_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    name_f = ft.TextField(
        hint_text="Habit name (e.g. Read 20 mins, Meditate)",
        expand=True,
        height=44,
        border_radius=10
    )
    icon_f = ft.TextField(
        value="⭐",
        hint_text="Emoji",
        width=72,
        height=44,
        border_radius=10,
        text_align=ft.TextAlign.CENTER
    )

    habit_col = ft.Column(spacing=12)

    def _open_edit_dialog(h: dict):
        edit_name = ft.TextField(value=h.get("name", ""), label="Habit Name", border_radius=10)
        edit_icon = ft.TextField(value=h.get("icon", "⭐"), label="Emoji", border_radius=10, width=80)

        def save_edit(e):
            val = edit_name.value.strip() if edit_name.value else ""
            if not val:
                show_toast(page, "Habit name cannot be empty", "error")
                return
            try:
                Database.update_habit(
                    h["id"],
                    {
                        "name": val,
                        "icon": edit_icon.value.strip() if (edit_icon.value and edit_icon.value.strip()) else "⭐"
                    }
                )
                if hasattr(page, "close"):
                    try: page.close(dlg)
                    except Exception: dlg.open = False
                else:
                    dlg.open = False
                _rebuild()
                page.update()
                show_toast(page, "Habit updated successfully!", "success")
            except Exception as err:
                print(f"[Habits] Update error: {err}")

        def close_edit(e):
            if hasattr(page, "close"):
                try: page.close(dlg)
                except Exception: dlg.open = False
            else:
                dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Habit", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    [edit_name, edit_icon],
                    spacing=12,
                    tight=True
                ),
                width=340,
                padding=10
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_edit),
                ft.ElevatedButton(
                    "Save Changes",
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=AppColors.BLUE,
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=save_edit
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        if hasattr(page, "open"):
            try: page.open(dlg)
            except Exception: page.dialog = dlg; dlg.open = True
        else:
            page.dialog = dlg
            dlg.open = True
        page.update()

    def _delete(hid: str):
        try:
            Database.delete_habit(hid)
            _rebuild()
            page.update()
            show_toast(page, "Habit deleted", "info")
        except Exception as err:
            print(f"[Habits] Delete error: {err}")

    def _toggle(hid: str):
        try:
            Database.toggle_habit(hid, Database.today_str())
            _rebuild()
            page.update()
        except Exception as err:
            print(f"[Habits] Toggle error: {err}")

    def _rebuild():
        try:
            habits = Database.get_habits()
            habit_col.controls.clear()
            if not habits:
                habit_col.controls.append(
                    create_empty_state(ft.Icons.LOOP_OUTLINED, "No habits tracked yet. Add one above!", dark_mode)
                )
                return

            today = Database.today_str()
            for h in habits:
                done = h.get("completions", {}).get(today, False)
                streak = h.get("streak", 0)
                hid = h["id"]

                habit_card = create_card(
                    content=ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Text(h.get("icon", "⭐"), size=26),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                h["name"],
                                                size=15,
                                                weight=ft.FontWeight.BOLD,
                                                color=get_text_primary(dark_mode),
                                                style=ft.TextStyle(
                                                    decoration=ft.TextDecoration.LINE_THROUGH if done else None
                                                )
                                            ),
                                            ft.Row(
                                                [
                                                    ft.Text(
                                                        f"🔥 {streak} day streak",
                                                        size=12,
                                                        color=AppColors.ORANGE,
                                                        weight=ft.FontWeight.W_600
                                                    ),
                                                ],
                                                spacing=6
                                            )
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                spacing=14,
                            ),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "✓ Done" if done else "Mark Done",
                                        style=ft.ButtonStyle(
                                            color=ft.Colors.WHITE,
                                            bgcolor=AppColors.GREEN if done else (
                                                AppColors.BG_HOVER_DARK if dark_mode else AppColors.BG_HOVER_LIGHT
                                            ),
                                            shape=ft.RoundedRectangleBorder(radius=10),
                                        ),
                                        on_click=lambda e, habit_id=hid: _toggle(habit_id),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_OUTLINED,
                                        icon_size=18,
                                        icon_color=get_text_secondary(dark_mode),
                                        tooltip="Edit Habit",
                                        on_click=lambda e, habit_item=h: _open_edit_dialog(habit_item)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINED,
                                        icon_size=18,
                                        icon_color=AppColors.RED,
                                        tooltip="Delete Habit",
                                        on_click=lambda e, habit_id=hid: _delete(habit_id)
                                    ),
                                ],
                                spacing=4,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=14,
                    dark_mode=dark_mode,
                )
                habit_col.controls.append(habit_card)
        except Exception as exc:
            print(f"[Habits] Rebuild error: {exc}")

    def _add(e):
        try:
            val = name_f.value.strip() if name_f.value else ""
            if not val:
                show_toast(page, "Please enter a habit name", "error")
                return
            Database.add_habit(
                name=val,
                icon=icon_f.value.strip() if (icon_f.value and icon_f.value.strip()) else "⭐"
            )
            name_f.value = ""
            _rebuild()
            page.update()
            show_toast(page, "Habit added!", "success")
        except Exception as err:
            print(f"[Habits] Add error: {err}")
            show_toast(page, f"Error: {err}", "error")

    _rebuild()

    add_card = create_card(
        content=ft.Row(
            [
                name_f,
                icon_f,
                ft.ElevatedButton(
                    "Add Habit",
                    icon=ft.Icons.ADD,
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
        ),
        padding=16,
        dark_mode=dark_mode,
    )

    return ft.Column(
        [
            create_section_header(
                "Habit Tracker",
                "Build consistent daily routines, track your progress and maintain streaks",
                dark_mode=dark_mode
            ),
            add_card,
            habit_col,
        ],
        spacing=16,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
