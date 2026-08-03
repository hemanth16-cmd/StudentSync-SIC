"""
Sleep Tracker Page View for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_text_primary, get_text_secondary
from app.database import Database
from components.common_widgets import create_card, create_stat_card, create_section_header, create_badge, create_empty_state
from components.modals import show_toast


def sleep_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:

    dur_f  = ft.TextField(hint_text="Hours slept (e.g. 7.5)", expand=True, height=42, border_radius=10)
    bed_f  = ft.TextField(hint_text="Bedtime (23:00)", width=130, height=42, border_radius=10)
    wake_f = ft.TextField(hint_text="Wake (07:00)",    width=130, height=42, border_radius=10)
    qual_dd = ft.Dropdown(
        value=3,
        options=[ft.dropdown.Option(i, f"{'⭐'*i} {['','Poor','Fair','Good','Great','Excellent'][i]}") for i in range(1, 6)],
        width=170, border_radius=10,
    )

    sleep_col = ft.Column(spacing=10)

    def _avg():
        logs = Database.get_sleep_logs()
        return (sum(l.get("duration", 0) for l in logs) / len(logs)) if logs else 0.0

    # ── Stats container – rebuilt on every refresh ──────────────────────────
    stats_col = ft.Row(spacing=16)

    def _rebuild():
        # Rebuild stat cards with current values
        stats_col.controls = [
            create_stat_card("Avg Sleep",  f"{_avg():.1f} hrs",
                             "Goal: 8.0 hrs", ft.Icons.BEDTIME,          AppColors.INDIGO, dark_mode),
            create_stat_card("Total Logs", str(len(Database.get_sleep_logs())),
                             "Sleep records",  ft.Icons.NIGHTLIGHT_ROUND, AppColors.PURPLE, dark_mode),
        ]

        logs = Database.get_sleep_logs()
        sleep_col.controls.clear()
        if not logs:
            sleep_col.controls.append(
                create_empty_state(ft.Icons.BEDTIME_OUTLINED, "No sleep records yet", dark_mode)
            )
            return
        for s in logs:
            stars = "⭐" * int(s.get("quality", 3))
            sleep_col.controls.append(
                create_card(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(f"😴  {s.get('duration', 0)} hrs", size=14,
                                            weight=ft.FontWeight.BOLD, color=get_text_primary(dark_mode)),
                                    ft.Text(
                                        f"{s.get('date','')}  ·  Bed: {s.get('bedtime','—')}  ·  Wake: {s.get('wakeTime','—')}",
                                        size=12, color=get_text_secondary(dark_mode),
                                    ),
                                ],
                                spacing=3, expand=True,
                            ),
                            create_badge(stars, bgcolor=f"{AppColors.INDIGO}22", text_color=AppColors.INDIGO),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=14, dark_mode=dark_mode,
                )
            )

    def _add(e):
        try:
            dur = float(dur_f.value or "")
        except ValueError:
            show_toast(page, "Enter a valid duration (e.g. 7.5)", "error")
            return
        Database.add_sleep_log(
            duration=dur,
            quality=int(qual_dd.value) if qual_dd.value else 3,
            bedtime=bed_f.value.strip(),
            wake_time=wake_f.value.strip(),
        )
        dur_f.value = bed_f.value = wake_f.value = ""
        show_toast(page, "Sleep logged!", "success")
        _rebuild(); page.update()

    _rebuild()

    add_card = create_card(
        content=ft.Row(
            [dur_f, bed_f, wake_f, qual_dd,
             ft.ElevatedButton(
                 "Log Sleep",
                 icon=ft.Icons.BEDTIME,
                 style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=AppColors.INDIGO,
                                      shape=ft.RoundedRectangleBorder(radius=10)),
                 on_click=_add, height=42,
             )],
            spacing=10, wrap=True,
        ),
        padding=16, dark_mode=dark_mode,
    )

    return ft.Column(
        [
            create_section_header("Sleep Tracker", "Monitor sleep duration and rest quality", dark_mode=dark_mode),
            stats_col,
            add_card,
            sleep_col,
        ],
        spacing=16, expand=True, scroll=ft.ScrollMode.AUTO,
    )
