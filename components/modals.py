"""
Onboarding Modal & Toast Notifications for StudentSync (Python Flet 0.86+)
"""

import flet as ft
from app.theme import AppColors, get_card_bg, get_text_primary, get_text_secondary
from app.database import Database


def show_onboarding_dialog(page: ft.Page, on_complete_callback=None):
    """First-visit onboarding dialog."""

    name_field = ft.TextField(
        label="Your name",
        hint_text="e.g. Alex",
        border_radius=10,
        autofocus=True,
    )
    college_field = ft.TextField(
        label="College / University",
        hint_text="e.g. Stanford University",
        border_radius=10,
    )

    def finish(e):
        name    = (name_field.value or "").strip() or "Student"
        college = (college_field.value or "").strip()
        Database.update_settings({"name": name, "college": college})
        Database.get("visited", True)
        if hasattr(page, "close"):
            try:
                page.close(dlg)
            except Exception:
                dlg.open = False
        else:
            dlg.open = False
        page.update()
        show_toast(page, f"Welcome to StudentSync, {name}! 🚀", "success")
        if on_complete_callback:
            on_complete_callback()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("🎓 Welcome to StudentSync", size=20, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Your all-in-one student productivity platform.\nLet's set up your profile in 10 seconds.",
                        size=13,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=8),
                    name_field,
                    college_field,
                ],
                tight=True,
                spacing=14,
            ),
            width=380,
            padding=ft.Padding(top=4, bottom=4),
        ),
        actions=[
            ft.ElevatedButton(
                "Let's Go! 🚀",
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=AppColors.BLUE,
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding(left=24, right=24, top=14, bottom=14),
                ),
                on_click=finish,
                width=380,
            )
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    if hasattr(page, "open"):
        try:
            page.open(dlg)
        except Exception:
            page.dialog = dlg
            dlg.open = True
    else:
        page.dialog = dlg
        dlg.open = True
    page.update()


def show_toast(page: ft.Page, message: str, kind: str = "success"):
    """Floating SnackBar notification."""
    color_map = {
        "success": AppColors.GREEN,
        "error":   AppColors.RED,
        "warning": AppColors.ORANGE,
        "info":    AppColors.BLUE,
    }
    try:
        snack = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            bgcolor=color_map.get(kind, AppColors.BLUE),
            behavior=ft.SnackBarBehavior.FLOATING,
            duration=3000,
        )
        if hasattr(page, "open"):
            try:
                page.open(snack)
                return
            except Exception:
                pass
        page.snack_bar = snack
        page.snack_bar.open = True
        page.update()
    except Exception as exc:
        print(f"[Toast] Exception ignored: {exc}")
