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


# ── Canvas Charts ────────────────────────────────────────────────────────────
# Flet 0.86 has no built-in PieChart/BarChart widgets.
# We draw them manually with flet.canvas (Arc, Rect, Text).

import math
import flet.canvas as cv


def build_pie_chart(
    data: list[tuple[str, float, str]],
    size: int = 160,
) -> ft.Control:
    """
    Draw a donut-style pie chart on a Canvas.

    Args:
        data: list of (label, value, hex_color).
        size: pixel width/height of the chart.

    Returns:
        A Container wrapping the Canvas.
    """
    total = sum(d[1] for d in data)
    if total == 0:
        return ft.Container(
            width=size, height=size,
            alignment=ft.Alignment(0, 0),
            content=ft.Text("No data", size=12, color=TEXT_3, italic=True),
        )

    shapes: list[cv.Shape] = []
    start = -math.pi / 2  # 12 o'clock

    for _label, val, color in data:
        if val <= 0:
            continue
        sweep = (val / total) * 2 * math.pi
        shapes.append(
            cv.Arc(
                x=10, y=10,
                width=size - 20, height=size - 20,
                start_angle=start,
                sweep_angle=sweep,
                use_center=True,
                paint=ft.Paint(color=color, style=ft.PaintingStyle.FILL),
            ),
        )
        start += sweep

    # Inner circle to make it a donut
    inner = size * 0.38
    offset = (size - inner) / 2
    shapes.append(
        cv.Circle(
            x=size / 2, y=size / 2,
            radius=inner / 2,
            paint=ft.Paint(color="#161B26", style=ft.PaintingStyle.FILL),
        ),
    )

    return cv.Canvas(shapes=shapes, width=size, height=size)


def pie_legend(
    data: list[tuple[str, float, str]],
    currency: str = "₹",
) -> ft.Column:
    """Build a vertical legend list for a pie chart."""
    total = sum(d[1] for d in data) or 1
    rows: list[ft.Control] = []
    for label, val, color in data:
        pct = round(val / total * 100)
        rows.append(
            ft.Row([
                ft.Container(width=10, height=10,
                             border_radius=ft.BorderRadius.all(3),
                             bgcolor=color),
                ft.Text(label, size=11, color=TEXT_2, expand=True),
                ft.Text(f"{currency}{val:,.0f} ({pct}%)",
                        size=11, color=TEXT_1,
                        weight=ft.FontWeight.W_600),
            ], spacing=8),
        )
    return ft.Column(rows, spacing=8)


def build_bar_chart(
    data: list[tuple[str, float]],
    bar_color: str = BLUE,
    highlight_color: str | None = None,
    width: int = 420,
    height: int = 180,
    currency: str = "₹",
) -> ft.Control:
    """
    Draw a vertical bar chart on a Canvas.

    Args:
        data: list of (label, value).
        bar_color: default bar fill colour.
        highlight_color: colour for the tallest bar.
        width / height: canvas dimensions.
        currency: symbol for tooltip.

    Returns:
        A Container wrapping the Canvas.
    """
    if not data:
        return ft.Container(
            width=width, height=height,
            alignment=ft.Alignment(0, 0),
            content=ft.Text("No data", size=12, color=TEXT_3, italic=True),
        )

    max_val = max(d[1] for d in data) or 1
    n = len(data)
    gap = 12
    bar_w = max(8, (width - gap * (n + 1)) / n)
    chart_h = height - 30  # reserve 30px for labels

    shapes: list[cv.Shape] = []
    hi = highlight_color or bar_color

    for i, (label, val) in enumerate(data):
        bh = max(4, (val / max_val) * chart_h)
        x = gap + i * (bar_w + gap)
        y = chart_h - bh

        color = hi if val == max_val and val > 0 else bar_color

        # Bar
        shapes.append(
            cv.Rect(
                x=x, y=y, width=bar_w, height=bh,
                border_radius=ft.BorderRadius(4, 4, 0, 0),
                paint=ft.Paint(color=color, style=ft.PaintingStyle.FILL),
            ),
        )

        # Value on top
        shapes.append(
            cv.Text(
                x=x + bar_w / 2 - 10, y=max(0, y - 16),
                value=f"{currency}{val:,.0f}",
                style=ft.TextStyle(size=9, color=TEXT_2),
            ),
        )

        # Label below
        shapes.append(
            cv.Text(
                x=x + bar_w / 2 - 12, y=chart_h + 6,
                value=label,
                style=ft.TextStyle(size=10, color=TEXT_3),
            ),
        )

    return cv.Canvas(shapes=shapes, width=width, height=height)
