"""
View Router & Navigation Registry for StudentSync Flet App
"""

from typing import Dict, Callable

import flet as ft

from app.state import AppState


class Router:
    _routes: Dict[str, Callable[[ft.Page], ft.Control]] = {}

    @classmethod
    def register(
        cls,
        route_name: str,
        view_builder: Callable[[ft.Page], ft.Control],
    ):
        """Register a page/view with the router."""
        cls._routes[route_name] = view_builder

    @classmethod
    def get_view(
        cls,
        route_name: str,
        page: ft.Page,
    ) -> ft.Control:
        """Return the view registered for the requested route."""

        builder = cls._routes.get(route_name)

        if builder:
            return builder(page)

        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.CONSTRUCTION,
                        size=48,
                        color=ft.Colors.AMBER,
                    ),
                    ft.Text(
                        f"Page '{route_name}' under construction",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.Alignment.CENTER,
            expand=True,
        )


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

from pages.auth_page import auth_view

Router.register("auth", auth_view)