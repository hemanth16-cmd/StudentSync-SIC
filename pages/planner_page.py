"""
Planner Page View for StudentSync (Python Flet 0.86+)
Includes Timetable, Tasks, and Study Sessions.
"""

import flet as ft
from datetime import date
from app.theme import AppColors, get_text_primary, get_text_secondary, get_border_color
from app.database import Database
from components.common_widgets import create_card, create_section_header, create_badge, create_empty_state, create_progress_bar
from components.modals import show_toast

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TYPE_COLORS = {"class": AppColors.BLUE, "study": AppColors.PURPLE, "event": AppColors.GREEN}


def planner_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    # ── TIMETABLE TAB ────────────────────────────────────────────────────────
    tt_title = ft.TextField(hint_text="Class / Event title", expand=True, height=42, border_radius=10)
    tt_day = ft.Dropdown(
        value="0",
        options=[ft.dropdown.Option(str(i), d) for i, d in enumerate(DAYS)],
        width=130, border_radius=10,
    )
    tt_start = ft.TextField(value="09:00", hint_text="Start", width=90, height=42, border_radius=10)
    tt_end   = ft.TextField(value="10:00", hint_text="End",   width=90, height=42, border_radius=10)
    tt_faculty = ft.TextField(hint_text="Faculty", width=120, height=42, border_radius=10)
    tt_room = ft.TextField(hint_text="Room", width=90, height=42, border_radius=10)
    tt_type = ft.Dropdown(
        value="class",
        options=[
            ft.dropdown.Option("class", "Class"),
            ft.dropdown.Option("study", "Study"),
            ft.dropdown.Option("event", "Event"),
        ],
        width=110, border_radius=10,
    )

    schedule_col = ft.Column(spacing=12)

    def _rebuild_timetable():
        events = Database.get_planner_events()
        schedule_col.controls.clear()

        if not events:
            schedule_col.controls.append(
                create_empty_state(ft.Icons.CALENDAR_TODAY, "No schedule events yet", dark_mode)
            )
            return

        day_cells = []
        for i, day_name in enumerate(DAYS):
            day_evs = [e for e in events if str(e.get("day", "0")) == str(i)]
            # sort by start time
            day_evs.sort(key=lambda x: x.get("startTime", "00:00"))
            
            ev_cards = []
            for ev in day_evs:
                color = TYPE_COLORS.get(ev.get("type", "class"), AppColors.BLUE)
                
                details = []
                if ev.get("faculty"): details.append(ft.Row([ft.Icon(ft.Icons.PERSON, size=12, color=color), ft.Text(ev.get("faculty"), size=11, color=get_text_secondary(dark_mode))], spacing=4))
                if ev.get("room"): details.append(ft.Row([ft.Icon(ft.Icons.LOCATION_ON, size=12, color=color), ft.Text(ev.get("room"), size=11, color=get_text_secondary(dark_mode))], spacing=4))

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
                                            on_click=lambda e, eid=ev["id"]: _delete_timetable_event(eid),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Text(
                                    f"{ev.get('startTime','09:00')} – {ev.get('endTime','10:00')}",
                                    size=11, color=get_text_secondary(dark_mode),
                                    weight=ft.FontWeight.W_600
                                ),
                                ft.Column(details, spacing=2),
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

    def _add_timetable_event(e):
        title = (tt_title.value or "").strip()
        if not title:
            show_toast(page, "Please enter a title", "error")
            return
        Database.add_planner_event(
            title=title,
            day=int(tt_day.value) if tt_day.value is not None else 0,
            start_time=(tt_start.value or "").strip() or "09:00",
            end_time=(tt_end.value or "").strip() or "10:00",
            event_type=tt_type.value or "class",
            faculty=(tt_faculty.value or "").strip(),
            room=(tt_room.value or "").strip(),
        )
        tt_title.value = tt_faculty.value = tt_room.value = ""
        show_toast(page, "Event added!", "success")
        _rebuild_timetable()
        page.update()

    def _delete_timetable_event(eid):
        Database.delete_planner_event(eid)
        show_toast(page, "Event removed", "info")
        _rebuild_timetable()
        page.update()

    tt_add_card = create_card(
        content=ft.Column([
            ft.Text("Add to Timetable", size=14, weight=ft.FontWeight.W_600, color=get_text_primary(dark_mode)),
            ft.Row(
                [tt_title, tt_day, tt_start, tt_end, tt_type, tt_faculty, tt_room,
                 ft.ElevatedButton(
                     "Add",
                     icon=ft.Icons.ADD,
                     style=ft.ButtonStyle(
                         color=ft.Colors.WHITE,
                         bgcolor=AppColors.ORANGE,
                         shape=ft.RoundedRectangleBorder(radius=10),
                     ),
                     on_click=_add_timetable_event,
                     height=42,
                 )],
                spacing=10,
                wrap=True,
            )
        ]),
        padding=16,
        dark_mode=dark_mode,
    )

    tt_tab_content = ft.Column([
        ft.Container(height=10),
        tt_add_card,
        schedule_col
    ], spacing=16, scroll=ft.ScrollMode.AUTO)

    # ── TASKS TAB ────────────────────────────────────────────────────────────
    task_filter = ["all"]
    tk_title = ft.TextField(hint_text="Task title...", expand=True, height=42, border_radius=10)
    tk_desc = ft.TextField(hint_text="Description (optional)", expand=True, height=42, border_radius=10)
    tk_subj = ft.TextField(hint_text="Subject", width=120, height=42, border_radius=10)
    tk_due = ft.TextField(hint_text="YYYY-MM-DD", width=120, height=42, border_radius=10)
    tk_prio = ft.Dropdown(
        value="medium",
        options=[
            ft.dropdown.Option("low", "Low"),
            ft.dropdown.Option("medium", "Medium"),
            ft.dropdown.Option("high", "High"),
        ],
        width=100, border_radius=10,
    )

    tasks_col = ft.Column(spacing=10)

    def _rebuild_tasks():
        tasks = Database.get_tasks()
        flt = task_filter[0]
        
        today = date.today().isoformat()
        
        filtered = []
        for t in tasks:
            is_overdue = t.get("dueDate") and t.get("dueDate") < today and not t.get("completed")
            
            if flt == "pending" and t.get("completed"): continue
            if flt == "completed" and not t.get("completed"): continue
            if flt == "overdue" and not is_overdue: continue
            filtered.append(t)

        tasks_col.controls.clear()
        if not filtered:
            tasks_col.controls.append(create_empty_state(ft.Icons.TASK_ALT, "No tasks found", dark_mode))
            return

        pcolor = {"high": AppColors.RED, "medium": AppColors.ORANGE, "low": AppColors.BLUE}
        
        for t in filtered:
            pc = pcolor.get(t.get("priority", "medium"), AppColors.ORANGE)
            is_overdue = t.get("dueDate") and t.get("dueDate") < today and not t.get("completed")
            
            due_color = AppColors.RED if is_overdue else get_text_secondary(dark_mode)
            due_text = f"Due: {t.get('dueDate')}" if t.get('dueDate') else "No due date"
            if is_overdue: due_text = "OVERDUE: " + due_text

            row = ft.Row(
                [
                    ft.Checkbox(
                        value=t.get("completed", False),
                        fill_color=AppColors.GREEN,
                        on_change=lambda e, tid=t["id"]: _toggle_task(tid),
                    ),
                    ft.Column([
                        ft.Text(
                            t["title"], size=14, weight=ft.FontWeight.W_600,
                            color=get_text_secondary(dark_mode) if t.get("completed") else get_text_primary(dark_mode),
                            opacity=0.55 if t.get("completed") else 1.0,
                        ),
                        ft.Text(
                            due_text, size=11, color=due_color,
                        )
                    ], expand=True, spacing=2),
                    create_badge(t.get("priority", "medium").upper(), bgcolor=f"{pc}22", text_color=pc),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=AppColors.RED,
                        icon_size=18,
                        on_click=lambda e, tid=t["id"]: _delete_task(tid),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
            tasks_col.controls.append(create_card(row, padding=12, dark_mode=dark_mode))

    def _add_task(e):
        title = (tk_title.value or "").strip()
        if not title:
            show_toast(page, "Please enter a task title", "error")
            return
        Database.add_task(
            title=title,
            description=(tk_desc.value or "").strip(),
            subject=(tk_subj.value or "").strip(),
            priority=tk_prio.value or "medium",
            due_date=(tk_due.value or "").strip(),
        )
        tk_title.value = tk_desc.value = tk_subj.value = tk_due.value = ""
        show_toast(page, "Task added!", "success")
        _rebuild_tasks()
        page.update()

    def _toggle_task(tid):
        Database.toggle_task(tid)
        _rebuild_tasks()
        page.update()

    def _delete_task(tid):
        Database.delete_task(tid)
        show_toast(page, "Task deleted", "info")
        _rebuild_tasks()
        page.update()

    def _filter_tasks(e):
        selected = e.control.selected
        if isinstance(selected, (set, list, tuple)):
            task_filter[0] = next(iter(selected), "all") if selected else "all"
        elif selected:
            task_filter[0] = selected
        else:
            task_filter[0] = "all"
        _rebuild_tasks()
        page.update()

    tk_filter_seg = ft.SegmentedButton(
        selected=["all"],
        segments=[
            ft.Segment(value="all",       label=ft.Text("All")),
            ft.Segment(value="pending",   label=ft.Text("Pending")),
            ft.Segment(value="completed", label=ft.Text("Completed")),
            ft.Segment(value="overdue",   label=ft.Text("Overdue")),
        ],
        on_change=_filter_tasks,
    )

    tk_add_card = create_card(
        content=ft.Column([
            ft.Text("Add Task", size=14, weight=ft.FontWeight.W_600, color=get_text_primary(dark_mode)),
            ft.Row(
                [tk_title, tk_desc, tk_subj, tk_due, tk_prio,
                 ft.ElevatedButton(
                     "Add",
                     icon=ft.Icons.ADD,
                     style=ft.ButtonStyle(
                         color=ft.Colors.WHITE,
                         bgcolor=AppColors.BLUE,
                         shape=ft.RoundedRectangleBorder(radius=10),
                     ),
                     on_click=_add_task,
                     height=42,
                 )],
                spacing=10,
                wrap=True,
            )
        ]),
        padding=16,
        dark_mode=dark_mode,
    )

    tasks_tab_content = ft.Column([
        ft.Container(height=10),
        tk_add_card,
        ft.Row([tk_filter_seg], alignment=ft.MainAxisAlignment.END),
        tasks_col
    ], spacing=16, scroll=ft.ScrollMode.AUTO)

    # ── STUDY SESSIONS TAB ───────────────────────────────────────────────────
    st_subj = ft.TextField(hint_text="Subject", expand=True, height=42, border_radius=10)
    st_topic = ft.TextField(hint_text="Topic", expand=True, height=42, border_radius=10)
    st_plan = ft.TextField(hint_text="Planned (mins)", width=120, height=42, border_radius=10)
    st_actual = ft.TextField(hint_text="Actual (mins)", width=120, height=42, border_radius=10)

    study_col = ft.Column(spacing=10)

    def _rebuild_study():
        sessions = Database.get_study_sessions()
        study_col.controls.clear()
        
        if not sessions:
            study_col.controls.append(create_empty_state(ft.Icons.MENU_BOOK, "No study sessions logged", dark_mode))
            return
            
        for s in sessions:
            planned = s.get("plannedDuration", 1)
            actual = s.get("actualDuration", 0)
            pct = min(actual / max(planned, 1) * 100, 100)
            
            color = AppColors.GREEN if pct >= 100 else AppColors.ORANGE
            
            study_col.controls.append(
                create_card(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text(s.get("subject", "Study"), size=14, weight=ft.FontWeight.W_600, color=get_text_primary(dark_mode)),
                                ft.Text(s.get("topic", ""), size=12, color=get_text_secondary(dark_mode)),
                            ], expand=True, spacing=2),
                            ft.Column([
                                ft.Text(f"{actual} / {planned} mins", size=12, weight=ft.FontWeight.W_600, color=color),
                                ft.Text(s.get("date", ""), size=11, color=get_text_secondary(dark_mode)),
                            ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        create_progress_bar(pct / 100, color=color)
                    ], spacing=10),
                    padding=16, dark_mode=dark_mode
                )
            )

    def _add_study(e):
        subj = (st_subj.value or "").strip()
        if not subj:
            show_toast(page, "Subject is required", "error")
            return
        
        planned = int(st_plan.value) if (st_plan.value or "").isdigit() else 60
        actual = int(st_actual.value) if (st_actual.value or "").isdigit() else 0
        
        Database.add_study_session(
            subject=subj,
            topic=(st_topic.value or "").strip(),
            planned_duration=planned,
            actual_duration=actual,
        )
        st_subj.value = st_topic.value = st_plan.value = st_actual.value = ""
        show_toast(page, "Study session logged!", "success")
        _rebuild_study()
        page.update()

    st_add_card = create_card(
        content=ft.Column([
            ft.Text("Log Study Session", size=14, weight=ft.FontWeight.W_600, color=get_text_primary(dark_mode)),
            ft.Row(
                [st_subj, st_topic, st_plan, st_actual,
                 ft.ElevatedButton(
                     "Log",
                     icon=ft.Icons.SAVE,
                     style=ft.ButtonStyle(
                         color=ft.Colors.WHITE,
                         bgcolor=AppColors.PURPLE,
                         shape=ft.RoundedRectangleBorder(radius=10),
                     ),
                     on_click=_add_study,
                     height=42,
                 )],
                spacing=10,
                wrap=True,
            )
        ]),
        padding=16,
        dark_mode=dark_mode,
    )

    study_tab_content = ft.Column([
        ft.Container(height=10),
        st_add_card,
        study_col
    ], spacing=16, scroll=ft.ScrollMode.AUTO)

    # ── INIT & RENDER ────────────────────────────────────────────────────────
    _rebuild_timetable()
    _rebuild_tasks()
    _rebuild_study()

    current_tab = ["timetable"]
    tab_content_container = ft.Container(content=tt_tab_content, expand=True)

    def _switch_tab(e):
        selected = e.control.selected
        if isinstance(selected, (set, list, tuple)):
            current_tab[0] = next(iter(selected), "timetable") if selected else "timetable"
        elif selected:
            current_tab[0] = selected
        else:
            current_tab[0] = "timetable"
            
        if current_tab[0] == "timetable":
            tab_content_container.content = tt_tab_content
        elif current_tab[0] == "tasks":
            tab_content_container.content = tasks_tab_content
        else:
            tab_content_container.content = study_tab_content
        page.update()

    tab_switcher = ft.SegmentedButton(
        selected=["timetable"],
        segments=[
            ft.Segment(value="timetable", label=ft.Text("Timetable"), icon=ft.Icons.CALENDAR_VIEW_WEEK),
            ft.Segment(value="tasks", label=ft.Text("Tasks"), icon=ft.Icons.CHECKLIST),
            ft.Segment(value="study", label=ft.Text("Study"), icon=ft.Icons.MENU_BOOK),
        ],
        on_change=_switch_tab,
    )

    return ft.Column(
        [
            create_section_header("Smart Planner", "Manage timetable, tasks, and study sessions", dark_mode=dark_mode),
            ft.Row([tab_switcher], alignment=ft.MainAxisAlignment.CENTER),
            tab_content_container,
        ],
        spacing=16,
        expand=True,
    )
