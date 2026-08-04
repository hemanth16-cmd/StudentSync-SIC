
"""
StudentSync — Premium Student Productivity Platform
Main Application Entry Point (Python Flet 0.86+)
"""

import os
import socket

import flet as ft

from authentication.auth_service import AuthService

from expenses.expense_tracker import ExpenseTrackerView

from app.theme import (
    get_theme,
    get_bg_color,
    AppColors,
    get_text_primary,
    get_text_secondary,
    get_border_color,
)
from app.database import Database
from app.state import AppState
from app.routes import Router


# ─────────────────────────────────────────────────────────────────────────────
# Components
# ─────────────────────────────────────────────────────────────────────────────

from components.sidebar import create_sidebar
from components.topbar import create_topbar
from components.modals import show_onboarding_dialog, show_toast
from components.common_widgets import (
    create_card,
    create_stat_card,
    create_section_header,
)


# ─────────────────────────────────────────────────────────────────────────────
# Page views
# ─────────────────────────────────────────────────────────────────────────────

from pages.todos_page import todos_view
from pages.planner_page import planner_view
from pages.subjects_page import subject_view
from pages.assignments_page import assignments_view
from pages.notes_page import notes_view
from pages.attendance_page import attendance_view
from pages.habits_page import habits_view
from pages.diet_page import diet_view
from pages.workout_page import workout_view
from pages.sleep_page import sleep_view
from pages.analytics_page import analytics_view
from pages.settings_page import settings_view


# ─────────────────────────────────────────────────────────────────────────────
# Route registrations
# ─────────────────────────────────────────────────────────────────────────────

Router.register("todos", todos_view)
Router.register("planner", planner_view)
Router.register("subjects", subject_view)
Router.register("assignments", assignments_view)
Router.register("notes", notes_view)
Router.register("attendance", attendance_view)
Router.register("habits", habits_view)
Router.register("diet", diet_view)
Router.register("workout", workout_view)
Router.register("sleep", sleep_view)
Router.register("analytics", analytics_view)
Router.register("settings", settings_view)


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────────────────────────────

def _dashboard_view(
    page: ft.Page,
    dark_mode: bool = True,
) -> ft.Control:
    """
    Dashboard overview.

    Dashboard data currently comes from the local Database layer.
    Authentication identity comes from AuthService.
    """

    settings = Database.get_settings()

    # Authenticated user is the primary source of identity.
    user = AuthService.current_user()

    if user:
        user_name = user.name
    else:
        user_name = settings.get("name", "Student")

    todos = Database.get_todos()
    subjects = Database.get_subjects()

    pending = sum(
        1
        for todo in todos
        if not todo.get("completed")
    )

    streak = Database.get_streak()

    hero = create_card(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    f"Welcome back, {user_name}! 👋",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=get_text_primary(dark_mode),
                                ),
                                ft.Text(
                                    "Here is your daily academic & lifestyle summary.",
                                    size=13,
                                    color=get_text_secondary(dark_mode),
                                ),
                            ],
                            spacing=4,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Text(
                                "🎓 StudentSync",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            padding=ft.Padding(
                                left=14,
                                right=14,
                                top=7,
                                bottom=7,
                            ),
                            bgcolor=AppColors.BLUE,
                            border_radius=20,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            ]
        ),
        padding=24,
        dark_mode=dark_mode,
    )

    stats = ft.Row(
        [
            create_stat_card(
                "Pending Tasks",
                str(pending),
                "Tasks remaining",
                ft.Icons.PENDING_ACTIONS,
                AppColors.ORANGE,
                dark_mode,
            ),
            create_stat_card(
                "Active Subjects",
                str(len(subjects)),
                "Enrolled courses",
                ft.Icons.BOOK,
                AppColors.BLUE,
                dark_mode,
            ),
            create_stat_card(
                "Login Streak",
                f"{streak} days",
                "Keep it going! 🔥",
                ft.Icons.LOCAL_FIRE_DEPARTMENT,
                AppColors.PURPLE,
                dark_mode,
            ),
        ],
        spacing=16,
    )

    return ft.Column(
        [
            create_section_header(
                "Dashboard",
                "Student Life Command Centre",
                dark_mode=dark_mode,
            ),
            hero,
            stats,
        ],
        spacing=16,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Expenses
# ─────────────────────────────────────────────────────────────────────────────

def _expenses_view(
    page: ft.Page,
    dark_mode: bool = True,
):
    return ExpenseTrackerView(page).build()


Router.register("dashboard", _dashboard_view)
Router.register("expenses", _expenses_view)


# ─────────────────────────────────────────────────────────────────────────────
# Authentication-aware application shell
# ─────────────────────────────────────────────────────────────────────────────

def main(page: ft.Page):

    page.title = "StudentSync — Premium Student Productivity"
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = AppColors.BG_APP_DARK

    # Window defaults
    try:
        page.window.width = 1280
        page.window.height = 820
        page.window.min_width = 900
        page.window.min_height = 600
    except Exception:
        pass

    # ────────────────────────────────────────────────────────────────────────
    # Content area
    # ────────────────────────────────────────────────────────────────────────

    content_area = ft.Container(expand=True)

    # ────────────────────────────────────────────────────────────────────────
    # Authentication-aware navigation
    # ────────────────────────────────────────────────────────────────────────

    def show_auth():
        """
        Display the authentication screen.

        No sidebar or authenticated application UI is shown here.
        """

        AppState.current_page = "auth"

        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = AppColors.BG_APP_DARK

        auth_view = Router.get_view("auth", page)

        page.controls.clear()
        page.add(
            ft.Container(
                content=auth_view,
                expand=True,
                bgcolor=AppColors.BG_APP_DARK,
            )
        )

        page.update()

    def _render_content():
        """
        Render the currently selected authenticated page.
        """

        dm = AppState.dark_mode

        view = Router.get_view(
            AppState.current_page,
            page,
        )

        content_area.content = ft.Container(
            content=view,
            padding=24,
            expand=True,
            bgcolor=get_bg_color(dm),
        )

        content_area.bgcolor = get_bg_color(dm)

    def _render_authenticated_app():
        """
        Render the main StudentSync application shell.

        This should only be called for authenticated users.
        """

        # Safety check.
        if not AuthService.is_logged_in():
            show_auth()
            return

        dm = AppState.dark_mode

        page.theme_mode = (
            ft.ThemeMode.DARK
            if dm
            else ft.ThemeMode.LIGHT
        )

        page.bgcolor = get_bg_color(dm)

        sidebar = create_sidebar(
            page,
            dark_mode=dm,
        )

        topbar = create_topbar(
            page,
            dark_mode=dm,
        )

        _render_content()

        main_col = ft.Column(
            [
                topbar,
                ft.Container(
                    content=content_area,
                    expand=True,
                    bgcolor=get_bg_color(dm),
                ),
            ],
            spacing=0,
            expand=True,
        )

        layout = ft.Row(
            [
                sidebar,
                main_col,
            ],
            spacing=0,
            expand=True,
        )

        page.controls.clear()
        page.add(layout)
        page.update()

    def render_application():
        """
        Decide which part of StudentSync should be displayed.

        Authentication is deliberately checked through AuthService only.
        """

        if AuthService.is_logged_in():

            # If the user is authenticated but somehow landed on auth,
            # return them to the dashboard.
            if AppState.current_page == "auth":
                AppState.current_page = "dashboard"

            _render_authenticated_app()

        else:
            show_auth()

    # ────────────────────────────────────────────────────────────────────────
    # State listeners
    # ────────────────────────────────────────────────────────────────────────

    AppState.page_change_listeners.clear()
    AppState.theme_change_listeners.clear()

    def on_page_change(_):
        """
        Handle navigation changes.

        Authentication remains protected by AuthService.
        """

        if not AuthService.is_logged_in():

            if AppState.current_page != "auth":
                AppState.current_page = "auth"

            show_auth()
            return

        _render_authenticated_app()

    def on_theme_change(_):
        """
        Re-render the authenticated application after theme changes.
        """

        if AuthService.is_logged_in():
            _render_authenticated_app()
        else:
            show_auth()

    AppState.page_change_listeners.append(
        on_page_change
    )

    AppState.theme_change_listeners.append(
        on_theme_change
    )

    # ────────────────────────────────────────────────────────────────────────
    # Initial application render
    # ────────────────────────────────────────────────────────────────────────

    render_application()

    # ────────────────────────────────────────────────────────────────────────
    # First-visit onboarding
    # ────────────────────────────────────────────────────────────────────────

    # Only show onboarding after authentication.
    if (
        AuthService.is_logged_in()
        and not Database.get("visited", False)
    ):
        show_onboarding_dialog(
            page,
            on_complete_callback=render_application,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Port discovery
# ─────────────────────────────────────────────────────────────────────────────

def find_available_port(
    default_port: int = 8551,
    max_attempts: int = 50,
) -> int:
    """
    Find an available TCP port for Flet.

    Uses FLET_PORT if provided, otherwise starts at default_port.
    """

    env_port = os.getenv("FLET_PORT")

    start_port = (
        int(env_port)
        if env_port and env_port.isdigit()
        else default_port
    )

    for port in range(
        start_port,
        start_port + max_attempts,
    ):
        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        ) as sock:

            try:
                sock.bind(
                    ("0.0.0.0", port)
                )
                return port

            except OSError:
                continue

    return start_port


# ─────────────────────────────────────────────────────────────────────────────
# Application entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    import os

    # Use Render's assigned PORT in deployment,
    # otherwise use 8551 for local development
    port = int(os.environ.get("PORT", 8551))

    print(
        f"\n[StudentSync] Flet Frontend is running on port {port}"
    )

    print(
        f"[StudentSync] Access URL: http://localhost:{port}\n"
    )

    ft.run(
        main,
        port=port,
        view=ft.AppView.WEB_BROWSER,
    )
