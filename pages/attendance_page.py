"""
Credit-Based Attendance Tracker Page View for StudentSync (Python Flet 0.86+)
Features:
- Credit-based total classes calculation (1 Credit = 15 classes)
- Real-time attendance percentage computation
- Bunk prediction & Safe bunks calculator
- Shortage recovery logic (continuous classes needed to reach 75%)
- Visual risk indicators (Green: Safe >=80%, Yellow: Warning 75-79%, Red: Shortage <75%)
- Full Subject CRUD (Add, Edit, Delete, Mark Present/Absent/Late)
"""

import math
import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary, get_border_color
from app.database import Database
from components.common_widgets import create_card, create_section_header, create_badge, create_empty_state, create_progress_bar
from components.modals import show_toast


def calculate_attendance_metrics(credits: int, attended: int, bunked: int, target_pct: float = 75.0):
    """
    Computes total classes, attendance percentage, safe bunks, recovery requirement, and risk level.
    Rule: 1 Credit = 15 total semester classes.
    """
    total_semester_classes = credits * 15
    conducted = attended + bunked

    if conducted == 0:
        current_pct = 100.0
    else:
        current_pct = (attended / conducted) * 100.0

    target_ratio = target_pct / 100.0

    # Safe bunks right now (consecutive future classes student can skip right now while keeping pct >= 75%)
    if conducted == 0:
        safe_bunks_now = math.floor(total_semester_classes * (1.0 - target_ratio))
    else:
        val = (attended - target_ratio * conducted) / target_ratio
        safe_bunks_now = math.floor(val) if val > 0 else 0

    # Max bunks allowed in entire semester
    min_classes_needed_sem = math.ceil(total_semester_classes * target_ratio)
    max_semester_bunks = max(0, total_semester_classes - min_classes_needed_sem)
    semester_bunks_left = max(0, max_semester_bunks - bunked)

    # Recovery classes needed if attendance < 75%
    if current_pct < target_pct:
        needed = (target_ratio * conducted - attended) / (1.0 - target_ratio)
        recovery_classes = max(0, math.ceil(needed))
    else:
        recovery_classes = 0

    # Risk level classification
    if current_pct >= 80.0:
        risk_level = "safe"      # Green
        color = AppColors.GREEN
    elif current_pct >= 75.0:
        risk_level = "warning"   # Yellow
        color = AppColors.ORANGE
    else:
        risk_level = "danger"    # Red
        color = AppColors.RED

    return {
        "credits": credits,
        "total_semester_classes": total_semester_classes,
        "conducted": conducted,
        "attended": attended,
        "bunked": bunked,
        "current_pct": current_pct,
        "safe_bunks_now": safe_bunks_now,
        "semester_bunks_left": semester_bunks_left,
        "recovery_classes": recovery_classes,
        "risk_level": risk_level,
        "color": color
    }


def attendance_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    att_col = ft.Column(spacing=14)
    summary_row = ft.Container()

    # ── Add / Edit Subject Dialog ─────────────────────────────────────────
    def _open_subject_modal(subject_data: dict = None):
        is_edit = subject_data is not None
        title_text = "Edit Subject" if is_edit else "Add New Subject"

        name_f = ft.TextField(
            value=subject_data.get("name", "") if is_edit else "",
            label="Subject Name",
            hint_text="e.g. Data Structures & Algorithms",
            border_radius=10
        )
        code_f = ft.TextField(
            value=subject_data.get("code", "") if is_edit else "",
            label="Subject Code",
            hint_text="e.g. CS201",
            border_radius=10
        )
        emoji_f = ft.TextField(
            value=subject_data.get("emoji", "📚") if is_edit else "📚",
            label="Emoji",
            width=70,
            border_radius=10,
            text_align=ft.TextAlign.CENTER
        )

        credit_dd = ft.Dropdown(
            value=str(subject_data.get("credits", 3)) if is_edit else "3",
            options=[ft.dropdown.Option(str(c), f"{c} Credit{'s' if c > 1 else ''} ({c*15} Classes)") for c in range(1, 7)],
            label="Course Credits",
            border_radius=10,
            expand=True
        )

        attended_f = ft.TextField(
            value=str(subject_data.get("attended", 0)) if is_edit else "0",
            label="Attended Classes",
            width=140,
            border_radius=10,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        bunked_f = ft.TextField(
            value=str(subject_data.get("bunked", 0)) if is_edit else "0",
            label="Bunked Classes",
            width=140,
            border_radius=10,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        total_classes_info = ft.Text(
            f"Total Semester Classes: {int(credit_dd.value)*15} (1 Credit = 15 Classes)",
            size=12,
            color=AppColors.BLUE,
            weight=ft.FontWeight.W_600
        )

        def on_credit_change(e):
            try:
                c = int(credit_dd.value or 3)
                total_classes_info.value = f"Total Semester Classes: {c*15} (1 Credit = 15 Classes)"
                dlg.update()
            except Exception:
                pass

        credit_dd.on_change = on_credit_change

        def save_subject(e):
            name_val = name_f.value.strip() if name_f.value else ""
            if not name_val:
                show_toast(page, "Subject name is required", "error")
                return

            try:
                credits_val = int(credit_dd.value or 3)
                att_val = int(attended_f.value or 0)
                bunk_val = int(bunked_f.value or 0)
            except ValueError:
                show_toast(page, "Please enter valid numbers for credits and classes", "error")
                return

            payload = {
                "name": name_val,
                "code": code_f.value.strip() if code_f.value else "",
                "emoji": emoji_f.value.strip() if emoji_f.value else "📚",
                "credits": credits_val,
                "totalClasses": credits_val * 15,
                "attended": att_val,
                "bunked": bunk_val
            }

            try:
                if is_edit:
                    Database.update_subject(subject_data["id"], payload)
                    show_toast(page, "Subject updated!", "success")
                else:
                    Database.add_subject(
                        name=payload["name"],
                        code=payload["code"],
                        credits=payload["credits"],
                        emoji=payload["emoji"]
                    )
                    show_toast(page, "Subject added!", "success")

                if hasattr(page, "close"):
                    try: page.close(dlg)
                    except Exception: dlg.open = False
                else:
                    dlg.open = False

                _rebuild()
                page.update()

            except Exception as exc:
                print(f"[Attendance] Subject save error: {exc}")
                show_toast(page, f"Error saving subject: {exc}", "error")

        def close_modal(e):
            if hasattr(page, "close"):
                try: page.close(dlg)
                except Exception: dlg.open = False
            else:
                dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title_text, size=18, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row([emoji_f, name_f], spacing=10),
                        code_f,
                        credit_dd,
                        total_classes_info,
                        ft.Row([attended_f, bunked_f], spacing=10)
                    ],
                    spacing=12,
                    tight=True
                ),
                width=380,
                padding=10
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_modal),
                ft.ElevatedButton(
                    "Save Subject",
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=AppColors.BLUE,
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=save_subject
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

    def _delete_subject(sid: str):
        try:
            Database.delete_subject(sid)
            show_toast(page, "Subject deleted", "info")
            _rebuild()
            page.update()
        except Exception as exc:
            print(f"[Attendance] Delete subject error: {exc}")

    def _mark(sid: str, status: str):
        try:
            Database.mark_attendance(sid, Database.today_str(), status)
            show_toast(page, f"Marked {status.capitalize()} for today", "success")
            _rebuild()
            page.update()
        except Exception as exc:
            print(f"[Attendance] Mark attendance error: {exc}")

    def _rebuild():
        subjects = Database.get_subjects()
        att_col.controls.clear()

        if not subjects:
            summary_row.content = ft.Container()
            att_col.controls.append(
                create_empty_state(
                    ft.Icons.HOW_TO_REG_OUTLINED,
                    "No subjects enrolled yet. Click '+ Add Subject' above to start tracking attendance!",
                    dark_mode
                )
            )
            return

        total_attended_all = sum(s.get("attended", 0) for s in subjects)
        total_conducted_all = sum(s.get("attended", 0) + s.get("bunked", 0) for s in subjects)
        overall_pct = (total_attended_all / total_conducted_all * 100.0) if total_conducted_all > 0 else 100.0
        total_credits = sum(s.get("credits", 3) for s in subjects)

        safe_count = 0
        warning_count = 0
        danger_count = 0

        # Build cards
        for s in subjects:
            credits_val = s.get("credits", 3)
            attended_val = s.get("attended", 0)
            bunked_val = s.get("bunked", 0)

            m = calculate_attendance_metrics(credits_val, attended_val, bunked_val, target_pct=75.0)

            if m["risk_level"] == "safe":
                safe_count += 1
            elif m["risk_level"] == "warning":
                warning_count += 1
            else:
                danger_count += 1

            pct_str = f"{m['current_pct']:.1f}%"
            card_color = m["color"]
            sid = s["id"]

            # Dynamic Banner Message
            if m["current_pct"] >= 75.0:
                if m["safe_bunks_now"] > 0:
                    guidance_text = f"✅ Safe to bunk: You can skip {m['safe_bunks_now']} class{'es' if m['safe_bunks_now'] > 1 else ''} right now while keeping attendance >= 75%."
                else:
                    guidance_text = "⚡ Borderline safe: Attending your next class is recommended to stay above 75%."
                banner_bg = f"{card_color}1A"
                banner_border = card_color
            else:
                guidance_text = f"🚨 Attendance Shortage Warning: You must attend the next {m['recovery_classes']} class{'es' if m['recovery_classes'] > 1 else ''} continuously to recover to 75%!"
                banner_bg = f"{AppColors.RED}22"
                banner_border = AppColors.RED

            guidance_box = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.VERIFIED_ROUNDED if m["current_pct"] >= 75.0 else ft.Icons.WARNING_AMBER_ROUNDED,
                            color=card_color,
                            size=18
                        ),
                        ft.Text(
                            guidance_text,
                            size=12,
                            weight=ft.FontWeight.W_600,
                            color=get_text_primary(dark_mode),
                            expand=True
                        ),
                    ],
                    spacing=8,
                ),
                padding=ft.Padding(12, 8, 12, 8),
                bgcolor=banner_bg,
                border_radius=8,
                border=ft.Border(left=ft.BorderSide(3, banner_border))
            )

            subject_card = create_card(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Row(
                                    [
                                        ft.Text(s.get("emoji", "📚"), size=24),
                                        ft.Column(
                                            [
                                                ft.Text(
                                                    s["name"],
                                                    size=16,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=get_text_primary(dark_mode)
                                                ),
                                                ft.Text(
                                                    f"Code: {s.get('code','—')}  ·  {s.get('teacher','Prof. Assigned')}",
                                                    size=12,
                                                    color=get_text_secondary(dark_mode),
                                                ),
                                            ],
                                            spacing=2,
                                            expand=True,
                                        ),
                                    ],
                                    spacing=10,
                                    expand=True,
                                ),
                                ft.Row(
                                    [
                                        create_badge(
                                            f"{credits_val} Credit{'s' if credits_val > 1 else ''}",
                                            bgcolor=f"{AppColors.BLUE}22",
                                            text_color=AppColors.BLUE
                                        ),
                                        create_badge(
                                            pct_str,
                                            bgcolor=f"{card_color}22",
                                            text_color=card_color
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.EDIT_OUTLINED,
                                            icon_size=18,
                                            icon_color=get_text_secondary(dark_mode),
                                            tooltip="Edit Subject",
                                            on_click=lambda e, item=s: _open_subject_modal(item)
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINED,
                                            icon_size=18,
                                            icon_color=AppColors.RED,
                                            tooltip="Delete Subject",
                                            on_click=lambda e, subject_id=sid: _delete_subject(subject_id)
                                        ),
                                    ],
                                    spacing=6,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        create_progress_bar(m["current_pct"] / 100.0, color=card_color),
                        ft.Row(
                            [
                                ft.Text(
                                    f"Attended: {m['attended']} / {m['conducted']} conducted",
                                    size=12,
                                    color=get_text_secondary(dark_mode),
                                    weight=ft.FontWeight.W_500
                                ),
                                ft.Text(
                                    f"Bunked: {m['bunked']}  ·  Total Semester Target: {m['total_semester_classes']} classes",
                                    size=12,
                                    color=get_text_secondary(dark_mode)
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        guidance_box,
                        ft.Divider(height=1),
                        ft.Row(
                            [
                                ft.Text("Mark Today:", size=12, weight=ft.FontWeight.W_600, color=get_text_secondary(dark_mode)),
                                ft.OutlinedButton(
                                    "Present",
                                    icon=ft.Icons.CHECK,
                                    style=ft.ButtonStyle(
                                        color=AppColors.GREEN,
                                        shape=ft.RoundedRectangleBorder(radius=8)
                                    ),
                                    on_click=lambda e, subject_id=sid: _mark(subject_id, "present"),
                                ),
                                ft.OutlinedButton(
                                    "Absent (Bunk)",
                                    icon=ft.Icons.CLOSE,
                                    style=ft.ButtonStyle(
                                        color=AppColors.RED,
                                        shape=ft.RoundedRectangleBorder(radius=8)
                                    ),
                                    on_click=lambda e, subject_id=sid: _mark(subject_id, "absent"),
                                ),
                                ft.OutlinedButton(
                                    "Late",
                                    icon=ft.Icons.SCHEDULE,
                                    style=ft.ButtonStyle(
                                        color=AppColors.ORANGE,
                                        shape=ft.RoundedRectangleBorder(radius=8)
                                    ),
                                    on_click=lambda e, subject_id=sid: _mark(subject_id, "late"),
                                ),
                            ],
                            spacing=8,
                        ),
                    ],
                    spacing=10,
                ),
                padding=16,
                dark_mode=dark_mode,
            )
            att_col.controls.append(subject_card)

        # Summary Header Bar
        overall_color = AppColors.GREEN if overall_pct >= 80.0 else (AppColors.ORANGE if overall_pct >= 75.0 else AppColors.RED)
        summary_row.content = create_card(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("Overall Attendance", size=12, color=get_text_secondary(dark_mode), weight=ft.FontWeight.W_600),
                            ft.Text(f"{overall_pct:.1f}%", size=24, weight=ft.FontWeight.BOLD, color=overall_color),
                            ft.Text(f"{total_attended_all} / {total_conducted_all} classes attended", size=12, color=get_text_secondary(dark_mode)),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Column(
                        [
                            ft.Text("Enrolled Subjects", size=12, color=get_text_secondary(dark_mode), weight=ft.FontWeight.W_600),
                            ft.Text(f"{len(subjects)} Subjects", size=20, weight=ft.FontWeight.BOLD, color=get_text_primary(dark_mode)),
                            ft.Text(f"{total_credits} Total Credits", size=12, color=get_text_secondary(dark_mode)),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Column(
                        [
                            ft.Text("Status Summary", size=12, color=get_text_secondary(dark_mode), weight=ft.FontWeight.W_600),
                            ft.Row(
                                [
                                    create_badge(f"{safe_count + warning_count} Safe", bgcolor=f"{AppColors.GREEN}22", text_color=AppColors.GREEN),
                                    create_badge(f"{danger_count} Shortage", bgcolor=f"{AppColors.RED}22", text_color=AppColors.RED) if danger_count > 0 else ft.Container()
                                ],
                                spacing=6
                            ),
                            ft.Text("Minimum target: 75%", size=12, color=get_text_secondary(dark_mode)),
                        ],
                        spacing=2,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=16,
            dark_mode=dark_mode
        )

    _rebuild()

    add_btn = ft.ElevatedButton(
        "+ Add Subject",
        icon=ft.Icons.ADD,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=AppColors.BLUE,
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=lambda e: _open_subject_modal(),
        height=42
    )

    return ft.Column(
        [
            create_section_header(
                "Attendance Tracker",
                "Credit-based attendance calculator & smart bunk predictor (75% Minimum Requirement)",
                action_button=add_btn,
                dark_mode=dark_mode
            ),
            summary_row,
            att_col,
        ],
        spacing=16,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
