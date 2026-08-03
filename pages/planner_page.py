"""
Planner Page View for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary, get_border_color
from app.database import Database
from components.common_widgets import create_card, create_section_header, create_badge, create_empty_state
from components.modals import show_toast

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TYPE_COLORS = {"class": AppColors.BLUE, "study": AppColors.PURPLE, "event": AppColors.GREEN}


def planner_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    title_input = ft.TextField(hint_text="Class / Event title", expand=True, height=42, border_radius=10)
    day_dd = ft.Dropdown(
        value=0,
        options=[ft.dropdown.Option(i, d) for i, d in enumerate(DAYS)],
        width=140,
        border_radius=10,
    )
    start_input = ft.TextField(value="09:00", hint_text="Start", width=90, height=42, border_radius=10)
    end_input   = ft.TextField(value="10:00", hint_text="End",   width=90, height=42, border_radius=10)
    type_dd = ft.Dropdown(
        value="class",
        options=[
            ft.dropdown.Option("class", "Class"),
            ft.dropdown.Option("study", "Study"),
            ft.dropdown.Option("event", "Event"),
        ],
        width=120,
        border_radius=10,
    )

    schedule_col = ft.Column(spacing=12)

    def _rebuild():
        events = Database.get_planner_events()
        schedule_col.controls.clear()

        if not events:
            schedule_col.controls.append(
                create_empty_state(ft.Icons.CALENDAR_TODAY, "No schedule events yet", dark_mode)
            )
            return

        day_cells = []
        for i, day_name in enumerate(DAYS):
            day_evs = [e for e in events if int(e.get("day", 0)) == i]
            ev_cards = []
            for ev in day_evs:
                color = TYPE_COLORS.get(ev.get("type", "class"), AppColors.BLUE)
                ev_cards.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(ev["title"], size=12, weight=ft.FontWeight.BOLD,
                                                color=get_text_primary(dark_mode), expand=True),
                                        ft.IconButton(
                                            icon=ft.Icons.CLOSE,
                                            icon_size=14,
                                            icon_color=AppColors.RED,
                                            on_click=lambda e, eid=ev["id"]: _delete(eid),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Text(
                                    f"{ev.get('startTime','09:00')} – {ev.get('endTime','10:00')}",
                                    size=11, color=get_text_secondary(dark_mode),
                                ),
                                create_badge(ev.get("type", "class").upper(),
                                             bgcolor=f"{color}22", text_color=color),
                            ],
                            spacing=4,
                        ),
                        padding=10,
                        bgcolor=f"{color}10",
                        border=ft.Border(top=ft.BorderSide(1, f"{color}33"), right=ft.BorderSide(1, f"{color}33"), bottom=ft.BorderSide(1, f"{color}33"), left=ft.BorderSide(1, f"{color}33")),
                        border_radius=10,
                    )
                )

            day_cells.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(day_name, size=13, weight=ft.FontWeight.BOLD, color=AppColors.ORANGE),
                            ft.Divider(height=1, color=get_border_color(dark_mode)),
                            ft.Column(
                                ev_cards if ev_cards
                                else [ft.Text("Free", size=12, color=get_text_secondary(dark_mode))],
                                spacing=6,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=12,
                    bgcolor=None,
                    border=ft.Border(
                        top=ft.BorderSide(1, get_border_color(dark_mode)),
                        right=ft.BorderSide(1, get_border_color(dark_mode)),
                        bottom=ft.BorderSide(1, get_border_color(dark_mode)),
                        left=ft.BorderSide(1, get_border_color(dark_mode)),
                    ),
                    border_radius=14,
                    col={"sm": 12, "md": 6, "lg": 3},
                )
            )
        schedule_col.controls.append(ft.ResponsiveRow(day_cells, spacing=12))

    def _add(e):
        if not title_input.value or not title_input.value.strip():
            show_toast(page, "Please enter a title", "error")
            return
        Database.add_planner_event(
            title=title_input.value.strip(),
            day=int(day_dd.value) if day_dd.value is not None else 0,
            start_time=start_input.value or "09:00",
            end_time=end_input.value or "10:00",
            event_type=type_dd.value or "class",
        )
        title_input.value = ""
        show_toast(page, "Event added!", "success")
        _rebuild()
        page.update()

    def _delete(eid):
        Database.delete_planner_event(eid)
        show_toast(page, "Event removed", "info")
        _rebuild()
        page.update()

    _rebuild()

    add_card = create_card(
        content=ft.Row(
            [title_input, day_dd, start_input, end_input, type_dd,
             ft.ElevatedButton(
                 "Add",
                 icon=ft.Icons.CALENDAR_MONTH,
                 style=ft.ButtonStyle(
                     color=ft.Colors.WHITE,
                     bgcolor=AppColors.ORANGE,
                     shape=ft.RoundedRectangleBorder(radius=10),
                 ),
                 on_click=_add,
                 height=42,
             )],
            spacing=10,
            wrap=True,
        ),
        padding=16,
        dark_mode=dark_mode,
    )

    return ft.Column(
        [
            create_section_header("Planner & Timetable", "Manage weekly classes and study blocks", dark_mode=dark_mode),
            add_card,
            schedule_col,
        ],
        spacing=16,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
