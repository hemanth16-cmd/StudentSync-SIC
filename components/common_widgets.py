"""
Reusable UI Widgets for StudentSync (Python Flet 0.86+)
All Flet API calls verified against flet 0.86.5
"""

import flet as ft
from app.theme import AppColors, get_card_bg, get_text_primary, get_text_secondary, get_border_color


def _all_border(width: int, color: str) -> ft.Border:
    side = ft.BorderSide(width, color)
    return ft.Border(top=side, right=side, bottom=side, left=side)


def create_card(
    content: ft.Control,
    padding: int = 20,
    border_color: str = None,
    dark_mode: bool = True,
    expand: bool = False,
) -> ft.Container:
    """Styled card container."""
    b_color = border_color or get_border_color(dark_mode)
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=get_card_bg(dark_mode),
        border=_all_border(1, b_color),
        border_radius=16,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=12,
            color="#14000000" if not dark_mode else "#1AFFFFFF",
            offset=ft.Offset(0, 4),
        ),
        expand=expand,
    )


def create_stat_card(
    title: str,
    value: str,
    subtitle: str = "",
    icon: str = ft.Icons.ANALYTICS,
    accent_color: str = AppColors.BLUE,
    dark_mode: bool = True,
) -> ft.Container:
    """KPI summary stat card."""
    return create_card(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(icon, color=accent_color, size=20),
                            padding=10,
                            bgcolor=f"{accent_color}22",
                            border_radius=12,
                        ),
                        ft.Text(
                            title,
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=get_text_secondary(dark_mode),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=6),
                ft.Text(value, size=26, weight=ft.FontWeight.BOLD, color=get_text_primary(dark_mode)),
                ft.Text(subtitle, size=12, color=get_text_secondary(dark_mode)) if subtitle else ft.Container(height=0),
            ],
            spacing=2,
        ),
        padding=16,
        dark_mode=dark_mode,
        expand=True,
    )


def create_section_header(
    title: str,
    subtitle: str = "",
    action_button: ft.Control = None,
    dark_mode: bool = True,
) -> ft.Row:
    """Page / section title header row."""
    return ft.Row(
        [
            ft.Column(
                [
                    ft.Text(title, size=22, weight=ft.FontWeight.BOLD, color=get_text_primary(dark_mode)),
                    ft.Text(subtitle, size=13, color=get_text_secondary(dark_mode)) if subtitle else ft.Container(height=0),
                ],
                spacing=2,
            ),
            action_button if action_button else ft.Container(width=0),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )


def create_badge(
    text: str,
    bgcolor: str = AppColors.BLUE,
    text_color: str = ft.Colors.WHITE,
) -> ft.Container:
    """Compact status / tag badge."""
    return ft.Container(
        content=ft.Text(text, size=11, weight=ft.FontWeight.W_600, color=text_color),
        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
        bgcolor=bgcolor,
        border_radius=20,
    )


def create_progress_bar(value: float, color: str = AppColors.BLUE, height: int = 8) -> ft.ProgressBar:
    """Rounded progress bar (value 0.0 – 1.0)."""
    return ft.ProgressBar(
        value=min(max(value, 0.0), 1.0),
        color=color,
        bgcolor=f"{color}30",
        height=height,
        border_radius=height // 2,
    )


def create_empty_state(
    icon: str = ft.Icons.INBOX,
    message: str = "No items found",
    dark_mode: bool = True,
) -> ft.Container:
    """Centred empty-state placeholder."""
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(icon, size=52, color=get_text_secondary(dark_mode)),
                ft.Text(
                    message,
                    size=14,
                    color=get_text_secondary(dark_mode),
                    weight=ft.FontWeight.W_500,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        padding=48,
        alignment=ft.Alignment(0, 0),
    )
