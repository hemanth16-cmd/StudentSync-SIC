import flet as ft


def timetable_view(page):

    # ---------- INPUT FIELDS ----------

    subject = ft.TextField(
        label="Subject",
        hint_text="e.g. Data Structures",
        expand=True,
    )

    day = ft.Dropdown(
        label="Day",
        options=[
            ft.dropdown.Option("Monday"),
            ft.dropdown.Option("Tuesday"),
            ft.dropdown.Option("Wednesday"),
            ft.dropdown.Option("Thursday"),
            ft.dropdown.Option("Friday"),
            ft.dropdown.Option("Saturday"),
        ],
        expand=True,
    )

    start_time = ft.TextField(
        label="Start Time",
        hint_text="09:00",
        expand=True,
    )

    end_time = ft.TextField(
        label="End Time",
        hint_text="10:00",
        expand=True,
    )

    room = ft.TextField(
        label="Room",
        hint_text="e.g. Room 204",
        expand=True,
    )

    # ---------- CLASS LIST ----------

    class_list = ft.Column(
        spacing=10,
    )

    # ---------- ADD CLASS ----------

    def add_class(e):

        # Make sure required fields are filled
        if not subject.value or not day.value:
            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text("Please enter a subject and select a day.")
                )
            )
            return

        # Create a card for the class
        class_card = ft.Container(
            padding=15,
            border_radius=10,
            bgcolor="#FFFFFF",
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                subject.value,
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"{day.value} | "
                                f"{start_time.value or 'N/A'} - "
                                f"{end_time.value or 'N/A'}",
                            ),
                            ft.Text(
                                f"Room: {room.value or 'N/A'}",
                                color="#64748B",
                            ),
                        ],
                        expand=True,
                    ),
                ],
            ),
        )

        class_list.controls.append(class_card)

        # Clear the form
        subject.value = ""
        day.value = None
        start_time.value = ""
        end_time.value = ""
        room.value = ""

        page.update()

    # ---------- ADD BUTTON ----------

    add_button = ft.ElevatedButton(
        "Add Class",
        icon=ft.Icons.ADD,
        on_click=add_class,
    )

    # ---------- PAGE ----------

    return ft.Column(
        controls=[
            ft.Text(
                "📅 Timetable",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),

            ft.Text(
                "Manage your weekly class schedule.",
                color="#64748B",
            ),

            ft.Divider(),

            ft.Text(
                "Add a Class",
                size=20,
                weight=ft.FontWeight.BOLD,
            ),

            subject,

            day,

            ft.Row(
                controls=[
                    start_time,
                    end_time,
                    room,
                ],
            ),

            add_button,

            ft.Divider(),

            ft.Text(
                "Your Classes",
                size=20,
                weight=ft.FontWeight.BOLD,
            ),

            class_list,
        ],
        scroll=ft.ScrollMode.AUTO,
    )