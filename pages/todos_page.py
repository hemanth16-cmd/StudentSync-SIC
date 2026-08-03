"""
To-Do Page View for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary
from app.database import Database
from components.common_widgets import (
    create_card, create_stat_card, create_section_header,
    create_badge, create_empty_state,
)
from components.modals import show_toast


def todos_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    filter_ref = ["all"]

    # ── Inputs ───────────────────────────────────────────────────────────
    task_input = ft.TextField(
        hint_text="Add a new task…",
        expand=True,
        border_radius=10,
        height=42,
        content_padding=ft.Padding(left=12, right=12, top=0, bottom=0),
    )
    priority_dd = ft.Dropdown(
        value="medium",
        options=[
            ft.dropdown.Option("low",    "Low Priority"),
            ft.dropdown.Option("medium", "Medium Priority"),
            ft.dropdown.Option("high",   "High Priority"),
        ],
        width=160,
        border_radius=10,
        content_padding=ft.Padding(left=10, right=10, top=0, bottom=0),
    )

    # ── Stats ─────────────────────────────────────────────────────────────
    def _counts():
        todos = Database.get_todos()
        done  = sum(1 for t in todos if t.get("completed"))
        return len(todos), done, len(todos) - done

    stats_col = ft.Row(spacing=16)

    def update_stats():
        total, done, pending = _counts()
        stats_col.controls = [
            create_stat_card("Total Tasks",  str(total),   "All tasks",  ft.Icons.TASK_ALT,        AppColors.ORANGE, dark_mode),
            create_stat_card("Completed",    str(done),    "Finished",   ft.Icons.CHECK_CIRCLE,    AppColors.GREEN,  dark_mode),
            create_stat_card("Pending",      str(pending), "To-do",      ft.Icons.PENDING_ACTIONS, AppColors.BLUE,   dark_mode),
        ]

    # ── Todo list ─────────────────────────────────────────────────────────
    todo_col = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    def rebuild_list():
        todos = Database.get_todos()
        flt   = filter_ref[0]
        if flt == "active":
            todos = [t for t in todos if not t.get("completed")]
        elif flt == "completed":
            todos = [t for t in todos if t.get("completed")]

        todo_col.controls.clear()
        if not todos:
            todo_col.controls.append(
                create_empty_state(ft.Icons.CHECKLIST, "No tasks here yet", dark_mode)
            )
            return

        pcolor = {"high": AppColors.RED, "medium": AppColors.ORANGE, "low": AppColors.BLUE}
        for t in todos:
            pc   = pcolor.get(t.get("priority", "medium"), AppColors.ORANGE)
            row  = ft.Row(
                [
                    ft.Checkbox(
                        value=t.get("completed", False),
                        fill_color=AppColors.GREEN,
                        on_change=lambda e, tid=t["id"]: _toggle(tid),
                    ),
                    ft.Text(
                        t["title"],
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=get_text_secondary(dark_mode) if t.get("completed") else get_text_primary(dark_mode),
                        opacity=0.55 if t.get("completed") else 1.0,
                        expand=True,
                    ),
                    create_badge(t.get("priority", "medium").upper(), bgcolor=f"{pc}22", text_color=pc),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=AppColors.RED,
                        icon_size=18,
                        on_click=lambda e, tid=t["id"]: _delete(tid),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
            todo_col.controls.append(create_card(row, padding=12, dark_mode=dark_mode))

    def _refresh():
        update_stats()
        rebuild_list()
        page.update()

    def _add(e):
        if not task_input.value or not task_input.value.strip():
            show_toast(page, "Please enter a task title", "error")
            return
        Database.add_todo(title=task_input.value.strip(), priority=priority_dd.value or "medium")
        task_input.value = ""
        show_toast(page, "Task added!", "success")
        _refresh()

    def _toggle(tid):
        Database.toggle_todo(tid)
        _refresh()

    def _delete(tid):
        Database.delete_todo(tid)
        show_toast(page, "Task deleted", "info")
        _refresh()

    task_input.on_submit = _add

    # Filter buttons
    def _filter(e):
        sel = list(e.control.selected)
        filter_ref[0] = sel[0] if sel else "all"
        rebuild_list()
        page.update()

    filter_seg = ft.SegmentedButton(
        selected=["all"],
        segments=[
            ft.Segment(value="all",       label=ft.Text("All")),
            ft.Segment(value="active",    label=ft.Text("Active")),
            ft.Segment(value="completed", label=ft.Text("Completed")),
        ],
        on_change=_filter,
    )

    # Initial build
    update_stats()
    rebuild_list()

    # stats_col is already populated by update_stats() above

    add_card = create_card(
        content=ft.Row(
            [task_input, priority_dd,
             ft.ElevatedButton(
                 "Add",
                 icon=ft.Icons.ADD,
                 style=ft.ButtonStyle(
                     color=ft.Colors.WHITE,
                     bgcolor=AppColors.ORANGE,
                     shape=ft.RoundedRectangleBorder(radius=10),
                 ),
                 on_click=_add,
                 height=42,
             )],
            spacing=12,
        ),
        padding=16,
        dark_mode=dark_mode,
    )

    return ft.Column(
        [
            create_section_header("To-Do List", "Organise and prioritise your tasks", dark_mode=dark_mode),
            stats_col,
            add_card,
            ft.Row([filter_seg], alignment=ft.MainAxisAlignment.END),
            todo_col,
        ],
        spacing=16,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
