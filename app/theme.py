"""
App Theme and Design Tokens for StudentSync (Python Flet 0.86+)
Inspired by Notion, Apple Fitness, Spotify
"""

import flet as ft


# ── Color Palette Constants ──
class AppColors:
    # Light Mode
    BG_APP_LIGHT     = "#F6F8FB"
    BG_CARD_LIGHT    = "#FFFFFF"
    BG_HOVER_LIGHT   = "#EEF2F7"
    TEXT_PRIMARY_LIGHT   = "#0F172A"
    TEXT_SECONDARY_LIGHT = "#475569"
    TEXT_MUTED_LIGHT     = "#94A3B8"
    BORDER_LIGHT         = "#E2E8F0"

    # Dark Mode
    BG_APP_DARK     = "#0F172A"
    BG_CARD_DARK    = "#1E293B"
    BG_HOVER_DARK   = "#334155"
    TEXT_PRIMARY_DARK   = "#F8FAFC"
    TEXT_SECONDARY_DARK = "#94A3B8"
    TEXT_MUTED_DARK     = "#64748B"
    BORDER_DARK         = "#334155"

    # Accent / Category Colors
    BLUE        = "#2563EB"   # Academic (Studies, Notes, Assignments)
    BLUE_LIGHT  = "#3B82F6"
    GREEN       = "#059669"   # Health (Attendance, Habits, Diet, Workout)
    GREEN_LIGHT = "#10B981"
    ORANGE      = "#D97706"   # Goals (To-Do, Planner)
    ORANGE_LIGHT = "#F59E0B"
    PURPLE      = "#7C3AED"   # Achievement (Analytics, Streaks)
    PURPLE_LIGHT = "#8B5CF6"
    INDIGO      = "#4338CA"   # Sleep / Calm
    RED         = "#DC2626"   # Danger / High Priority


def get_theme(dark_mode: bool = True) -> ft.Theme:
    """Returns a configured Flet Theme for light or dark mode."""
    color_scheme = ft.ColorScheme(
        primary=AppColors.BLUE,
        secondary=AppColors.PURPLE,
        surface=AppColors.BG_CARD_DARK if dark_mode else AppColors.BG_CARD_LIGHT,
        on_primary="white",
        on_secondary="white",
        on_surface=AppColors.TEXT_PRIMARY_DARK if dark_mode else AppColors.TEXT_PRIMARY_LIGHT,
        outline=AppColors.BORDER_DARK if dark_mode else AppColors.BORDER_LIGHT,
    )
    return ft.Theme(
        color_scheme=color_scheme,
        use_material3=True,
        font_family="Inter",
    )


def get_bg_color(dark_mode: bool) -> str:
    return AppColors.BG_APP_DARK if dark_mode else AppColors.BG_APP_LIGHT

def get_card_bg(dark_mode: bool) -> str:
    return AppColors.BG_CARD_DARK if dark_mode else AppColors.BG_CARD_LIGHT

def get_text_primary(dark_mode: bool) -> str:
    return AppColors.TEXT_PRIMARY_DARK if dark_mode else AppColors.TEXT_PRIMARY_LIGHT

def get_text_secondary(dark_mode: bool) -> str:
    return AppColors.TEXT_SECONDARY_DARK if dark_mode else AppColors.TEXT_SECONDARY_LIGHT

def get_border_color(dark_mode: bool) -> str:
    return AppColors.BORDER_DARK if dark_mode else AppColors.BORDER_LIGHT
