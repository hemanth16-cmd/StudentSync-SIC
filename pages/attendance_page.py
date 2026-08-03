"""
Attendance Tracker — Credit-based with bunk prediction & recovery calculation.
"""
import math
import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary, get_border_color
from app.database import Database
from components.common_widgets import (
    create_card, create_stat_card, create_section_header,
    create_badge, create_empty_state, create_progress_bar,
)
from components.modals import show_toast


def _bunk_allowance(attended: int, conducted: int) -> int:
    """Max classes that can be missed while staying ≥ 75%."""
    if conducted == 0:
        return 0
    # attended / (conducted + x) = 0.75  → x = (attended/0.75) - conducted
    return max(0, int(attended / 0.75 - conducted))


def _recovery_classes(attended: int, conducted: int) -> int:
    """Consecutive classes needed to reach 75% from below it."""
    # (attended + x) / (conducted + x) = 0.75
    # x = (0.75*conducted - attended) / 0.25
    x = (0.75 * conducted - attended) / 0.25
    return max(0, math.ceil(x))


def attendance_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    att_col    = ft.Column(spacing=14)
    stats_row  = ft.Row(spacing=16, wrap=True)

    def _rebuild():
        subjects = Database.get_subjects()
        att_col.controls.clear()
        stats_row.controls.clear()

        if not subjects:
            att_col.controls.append(
                create_empty_state(
                    ft.Icons.HOW_TO_REG_OUTLINED,
                    "Register subjects first (Subjects page) to track attendance",
                    dark_mode,
                )
            )
            return

        # ── Overall summary stats ──────────────────────────────────────────
        total_attended  = sum(s.get("attended", 0) for s in subjects)
        total_conducted = sum(s.get("attended", 0) + s.get("bunked", 0) for s in subjects)
        overall_pct     = (total_attended / total_conducted * 100) if total_conducted > 0 else 100.0
        safe_count      = sum(1 for s in subjects
                              if (s.get("attended", 0) + s.get("bunked", 0)) == 0
                              or s.get("attended", 0) / max(s.get("attended", 0) + s.get("bunked", 0), 1) * 100 >= 75)

        stats_row.controls = [
            create_stat_card("Subjects",      str(len(subjects)),       "Enrolled",        ft.Icons.SCHOOL,             AppColors.BLUE,   dark_mode),
            create_stat_card("Overall Avg",   f"{overall_pct:.1f}%",   "All subjects",    ft.Icons.HOW_TO_REG,         AppColors.GREEN,  dark_mode),
            create_stat_card("Safe Subjects", str(safe_count),          "Above 75%",       ft.Icons.CHECK_CIRCLE,       AppColors.PURPLE, dark_mode),
            create_stat_card("Total Attended",str(total_attended),      f"/ {total_conducted} conducted", ft.Icons.CALENDAR_TODAY, AppColors.ORANGE, dark_mode),
        ]

        # ── Per-subject cards ──────────────────────────────────────────────
        for s in subjects:
            attended  = s.get("attended", 0)
            bunked    = s.get("bunked",   0)
            conducted = attended + bunked
            credits   = s.get("credits",  3)
            total_cls = s.get("totalClasses", credits * 15)

            pct = (attended / conducted * 100) if conducted > 0 else 100.0

            if pct >= 80:
                color        = AppColors.GREEN
                status_emoji = "🟢"
                status_label = "Safe"
            elif pct >= 75:
                color        = AppColors.ORANGE
                status_emoji = "🟡"
                status_label = "Borderline"
            else:
                color        = AppColors.RED
                status_emoji = "🔴"
                status_label = "At Risk"

            # Prediction row
            if pct >= 75:
                bunk = _bunk_allowance(attended, conducted)
                pred_icon  = ft.Icons.SENTIMENT_SATISFIED
                pred_text  = f"You can bunk {bunk} more class{'es' if bunk != 1 else ''} and still stay safe"
                pred_color = AppColors.GREEN
                pred_bg    = f"{AppColors.GREEN}15"
            else:
                rec = _recovery_classes(attended, conducted)
                pred_icon  = ft.Icons.WARNING_ROUNDED
                pred_text  = f"Attend next {rec} class{'es' if rec != 1 else ''} continuously to reach 75%"
                pred_color = AppColors.RED
                pred_bg    = f"{AppColors.RED}15"

            att_col.controls.append(
                create_card(
                    content=ft.Column(
                        [
                            # ── Title row ──────────────────────────────────
                            ft.Row(
                                [
                                    ft.Row([
                                        ft.Text(s.get("emoji", "📚"), size=22),
                                        ft.Column([
                                            ft.Text(s["name"], size=15,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=get_text_primary(dark_mode)),
                                            ft.Text(
                                                f"{s.get('code','—')}  ·  {credits} Credits  ·  {total_cls} total classes",
                                                size=12, color=get_text_secondary(dark_mode),
                                            ),
                                        ], spacing=2),
                                    ], spacing=10),
                                    ft.Column([
                                        ft.Text(f"{status_emoji}  {pct:.0f}%",
                                                size=20, weight=ft.FontWeight.BOLD, color=color),
                                        ft.Text(f"{attended} attended / {conducted} conducted",
                                                size=11, color=get_text_secondary(dark_mode)),
                                        create_badge(status_label,
                                                     bgcolor=f"{color}22", text_color=color),
                                    ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=3),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            # ── Progress bar ───────────────────────────────
                            create_progress_bar(min(pct / 100.0, 1.0), color=color),
                            # 75% marker line label
                            ft.Row([
                                ft.Container(expand=True),
                                ft.Text("75% min", size=10,
                                        color=get_text_secondary(dark_mode)),
                            ]),
                            # ── Prediction banner ──────────────────────────
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(pred_icon, size=14, color=pred_color),
                                    ft.Text(pred_text, size=12, color=pred_color,
                                            weight=ft.FontWeight.W_500),
                                ], spacing=8),
                                padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                                bgcolor=pred_bg,
                                border_radius=8,
                            ),
                            ft.Divider(height=1, color=get_border_color(dark_mode)),
                            # ── Mark attendance ────────────────────────────
                            ft.Row(
                                [
                                    ft.Text("Mark Today:", size=12, weight=ft.FontWeight.W_600,
                                            color=get_text_secondary(dark_mode)),
                                    ft.FilledButton(
                                        "Present",
                                        icon=ft.Icons.CHECK_ROUNDED,
                                        style=ft.ButtonStyle(
                                            bgcolor=AppColors.GREEN,
                                            color=ft.Colors.WHITE,
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                        on_click=lambda e, sid=s["id"]: _mark(sid, "present"),
                                    ),
                                    ft.FilledButton(
                                        "Absent",
                                        icon=ft.Icons.CLOSE_ROUNDED,
                                        style=ft.ButtonStyle(
                                            bgcolor=AppColors.RED,
                                            color=ft.Colors.WHITE,
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                        on_click=lambda e, sid=s["id"]: _mark(sid, "absent"),
                                    ),
                                    ft.OutlinedButton(
                                        "Late",
                                        icon=ft.Icons.SCHEDULE,
                                        style=ft.ButtonStyle(color=AppColors.ORANGE,
                                                             side=ft.BorderSide(1, AppColors.ORANGE)),
                                        on_click=lambda e, sid=s["id"]: _mark(sid, "late"),
                                    ),
                                ],
                                spacing=10, wrap=True,
                            ),
                        ],
                        spacing=12,
                    ),
                    padding=18, dark_mode=dark_mode,
                )
            )

    def _mark(sid, status):
        Database.mark_attendance(sid, Database.today_str(), status)
        label = {"present": "Present ✅", "absent": "Absent ❌", "late": "Late ⏰"}[status]
        show_toast(page, f"Marked {label}", "success")
        _rebuild()
        page.update()

    _rebuild()

    return ft.Column(
        [
            create_section_header(
                "Attendance Tracker",
                "75% minimum · Credit-based class tracking · Bunk prediction",
                dark_mode=dark_mode,
            ),
            stats_row,
            att_col,
        ],
        spacing=16, expand=True, scroll=ft.ScrollMode.AUTO,
    )
