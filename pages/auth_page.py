
"""
Authentication UI for StudentSync.

The UI communicates with authentication only through AuthService.
It does not directly access Session or Firebase.
"""

import flet as ft

from authentication.auth_service import AuthService

from app.state import AppState

from app.theme import (
    AppColors,
    get_text_primary,
    get_text_secondary,
)


def auth_view(page: ft.Page) -> ft.Control:
    #uild the login/signup authentication screen

    dark_mode = AppState.dark_mode

    # ---------------------------------------------------------
    # Fields
    # ---------------------------------------------------------

    name_field = ft.TextField(
        label="Name",
        hint_text="Your name",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        visible=False,
        width=360,
    )

    email_field = ft.TextField(
        label="Email",
        hint_text="you@example.com",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        keyboard_type=ft.KeyboardType.EMAIL,
        width=360,
    )

    password_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        width=360,
    )

    # ---------------------------------------------------------
    # Feedback
    # ---------------------------------------------------------

    error_text = ft.Text(
        "",
        color=ft.Colors.RED_400,
        size=12,
        text_align=ft.TextAlign.CENTER,
    )

    # ---------------------------------------------------------
    # Headings
    # ---------------------------------------------------------

    mode_title = ft.Text(
        "Welcome back",
        size=28,
        weight=ft.FontWeight.BOLD,
        color=get_text_primary(dark_mode),
    )

    mode_subtitle = ft.Text(
        "Sign in to continue to StudentSync",
        size=13,
        color=get_text_secondary(dark_mode),
    )

    # ---------------------------------------------------------
    # Buttons
    # ---------------------------------------------------------

    submit_button = ft.ElevatedButton(
        content=ft.Text("Sign In"),
        width=360,
        height=46,
    )

    switch_button = ft.TextButton(
        content=ft.Text("Create an account"),
    )

    # Track whether we're in signup mode.
    mode = {"signup": False}

    # ---------------------------------------------------------
    # Helper functions
    # ---------------------------------------------------------

    def set_error(message: str):
        error_text.value = message
        page.update()

    def set_submit_text(text: str):
        submit_button.content = ft.Text(text)

    def set_switch_text(text: str):
        switch_button.content = ft.Text(text)

    # ---------------------------------------------------------
    # Login <-> Signup
    # ---------------------------------------------------------

    def switch_mode(e=None):
        mode["signup"] = not mode["signup"]

        if mode["signup"]:
            mode_title.value = "Create your account"
            mode_subtitle.value = "Start organizing your student life"

            name_field.visible = True

            set_submit_text("Create Account")
            set_switch_text("Already have an account? Sign in")

        else:
            mode_title.value = "Welcome back"
            mode_subtitle.value = "Sign in to continue to StudentSync"

            name_field.visible = False

            set_submit_text("Sign In")
            set_switch_text("Create an account")

        error_text.value = ""
        page.update()

    # ---------------------------------------------------------
    # Authentication
    # ---------------------------------------------------------

    def submit(e):
        error_text.value = ""

        submit_button.disabled = True
        set_submit_text("Please wait...")
        page.update()

        try:
            email = email_field.value.strip() if email_field.value else ""
            password = password_field.value or ""

            # -------------------------
            # Signup
            # -------------------------

            if mode["signup"]:
                name = (
                    name_field.value.strip()
                    if name_field.value
                    else ""
                )

                user = AuthService.signup(
                    name=name,
                    email=email,
                    password=password,
                )

                print(
                    f"[AUTH UI] Account created for {user.email}"
                )

            # -------------------------
            # Login
            # -------------------------

            else:
                user = AuthService.login(
                    email=email,
                    password=password,
                )

                print(
                    f"[AUTH UI] Logged in as {user.email}"
                )

            # AuthService owns authentication/session state.
            #
            # The UI does NOT:
            # - import Session
            # - access Firebase
            # - manipulate Firebase tokens
            #
            # After successful authentication, navigate
            # to the dashboard.

            AppState.set_page("dashboard")

        except Exception as ex:
            print(f"[AUTH UI] Authentication error: {ex}")

            set_error(str(ex))

            submit_button.disabled = False

            set_submit_text(
                "Create Account"
                if mode["signup"]
                else "Sign In"
            )

            page.update()

    # ---------------------------------------------------------
    # Event handlers
    # ---------------------------------------------------------

    submit_button.on_click = submit
    switch_button.on_click = switch_mode

    # ---------------------------------------------------------
    # Authentication card
    # ---------------------------------------------------------

    card = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.SCHOOL_ROUNDED,
                        color=ft.Colors.WHITE,
                        size=28,
                    ),
                    padding=14,
                    bgcolor=AppColors.BLUE,
                    border_radius=16,
                ),

                ft.Container(height=8),

                mode_title,
                mode_subtitle,

                ft.Container(height=12),

                name_field,
                email_field,
                password_field,

                error_text,

                ft.Container(height=8),

                submit_button,
                switch_button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),

        width=460,
        padding=40,
        border_radius=20,

        bgcolor=ft.Colors.with_opacity(
            0.06,
            ft.Colors.WHITE if dark_mode else ft.Colors.BLACK,
        ),
    )

    # ---------------------------------------------------------
    # Full authentication page
    # ---------------------------------------------------------

    return ft.Container(
        content=card,
        expand=True,
        alignment=ft.Alignment.CENTER,
    )
