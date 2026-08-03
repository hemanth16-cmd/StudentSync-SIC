"""
expenses/ui_helpers.py
Reusable Flet UI builder helpers for the Expense Tracker.
Tested against Flet 0.86.5 / Python 3.14.
"""
from __future__ import annotations
import flet as ft

# ── Design tokens (mirrors JS CSS variables) ──────────────────────────────

INDIGO    = "#6366F1"
BLUE      = "#2563EB"
GREEN     = "#059669"
ORANGE    = "#D97706"
DANGER    = "#DC2626"
PURPLE    = "#7C3AED"
TEAL      = "#0D9488"

BORDER    = ft.Colors.with_opacity(0.12, ft.Colors.WHITE)
TEXT_1    = "#F0F6FF"
TEXT_2    = "#8899AF"
TEXT_3    = "#536070"

GRAD_BG   = ft.LinearGradient(
    begin=ft.Alignment(-1, -1),
    end=ft.Alignment(1, 1),
    colors=["#0C1117", "#161B26"],
)

CARD_RADIUS = ft.BorderRadius.all(16)


# ── Helpers ──────────────────────────────────────────────────────────────────

def icon_box(icon: str, color: str) -> ft.Container:
    return ft.Container(
        content=ft.Icon(icon, color=color, size=20),
        width=42, height=42,
        border_radius=ft.BorderRadius.all(12),
        bgcolor=ft.Colors.with_opacity(0.15, color),
    )


def stat_card(label: str, value: str, icon: str, color: str) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Row([
                icon_box(icon, color),
                ft.Text(label, size=11, color=TEXT_3,
                        weight=ft.FontWeight.W_600, expand=True),
            ], spacing=10),
            ft.Text(value, size=22, weight=ft.FontWeight.W_800, color=TEXT_1),
        ], spacing=10),
        padding=ft.Padding.all(16),
        border_radius=CARD_RADIUS,
        border=ft.Border.all(1, BORDER),
        bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.WHITE),
        expand=True,
    )


def section_title(text: str, icon: str | None = None) -> ft.Row:
    children: list[ft.Control] = []
    if icon:
        children.append(ft.Icon(icon, size=16, color=BLUE))
    children.append(
        ft.Text(text, size=13, weight=ft.FontWeight.W_700, color=TEXT_1)
    )
    return ft.Row(children, spacing=6)


def card(content: ft.Control, padding: int = 18) -> ft.Container:
    return ft.Container(
        content=content,
        padding=ft.Padding.all(padding),
        border_radius=CARD_RADIUS,
        border=ft.Border.all(1, BORDER),
        bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.WHITE),
    )


def progress_bar(pct: float, color: str, height: int = 8) -> ft.ProgressBar:
    """Flet ProgressBar — value is 0.0 to 1.0."""
    return ft.ProgressBar(
        value=max(0.0, min(pct / 100, 1.0)),
        color=color,
        bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
        height=height,
        border_radius=ft.BorderRadius.all(4),
    )


def progress_bar_row(label: str, amount: str, pct: float,
                     color: str) -> ft.Column:
    return ft.Column([
        ft.Row([
            ft.Text(label, size=12, color=TEXT_2, expand=True),
            ft.Text(amount, size=12, color=TEXT_1,
                    weight=ft.FontWeight.W_600),
        ]),
        progress_bar(pct, color),
    ], spacing=4)


def divider() -> ft.Divider:
    return ft.Divider(height=1, color=BORDER)


def chip_button(label: str, active: bool, on_click) -> ft.Container:
    return ft.Container(
        content=ft.Text(label, size=11,
                        color=BLUE if active else TEXT_2,
                        weight=ft.FontWeight.W_600),
        padding=ft.Padding.symmetric(horizontal=12, vertical=6),
        border_radius=ft.BorderRadius.all(20),
        bgcolor=(ft.Colors.with_opacity(0.15, BLUE)
                 if active
                 else ft.Colors.with_opacity(0.06, ft.Colors.WHITE)),
        border=ft.Border.all(
            1,
            ft.Colors.with_opacity(0.4, BLUE) if active else BORDER,
        ),
        on_click=on_click,
        ink=True,
    )
