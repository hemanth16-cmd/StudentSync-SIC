import flet as ft


def notes_view(page):

    # Stores notes while the app is running
    notes = []

    # ---------- UI ----------

    notes_list = ft.Column(
        spacing=12,
    )

    # ---------- NOTE EDITOR ----------

    title_field = ft.TextField(
        label="Note title",
        hint_text="e.g. Data Structures - Trees",
    )

    content_field = ft.TextField(
        label="Note content",
        hint_text="Write your notes here...",
        multiline=True,
        min_lines=5,
        max_lines=10,
    )

    dialog = ft.AlertDialog(
        title=ft.Text("Create Note"),
        content=ft.Column(
            controls=[
                title_field,
                content_field,
            ],
            tight=True,
        ),
    )

    # ---------- REFRESH NOTES ----------

    def refresh_notes():

        notes_list.controls.clear()

        if not notes:
            notes_list.controls.append(
                ft.Container(
                    padding=30,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "📝",
                                size=40,
                            ),
                            ft.Text(
                                "No notes yet",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Create your first note using the button above.",
                                color="#64748B",
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )

        for index, note in enumerate(notes):

            create_note_card(
                note,
                index,
            )

    # ---------- CREATE NOTE CARD ----------

    def create_note_card(note, index):

        def delete_note(e):

            notes.pop(index)

            refresh_notes()

            page.update()

        def edit_note(e):

            title_field.value = note["title"]
            content_field.value = note["content"]

            dialog.title = ft.Text("Edit Note")

            def save_edit(e):

                note["title"] = title_field.value
                note["content"] = content_field.value

                dialog.open = False

                refresh_notes()

                page.update()

            dialog.actions = [
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: close_dialog(),
                ),
                ft.ElevatedButton(
                    "Save",
                    on_click=save_edit,
                ),
            ]

            page.show_dialog(dialog)

        card = ft.Container(
            padding=20,
            border_radius=12,
            bgcolor="#FFFFFF",
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                note["title"],
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),

                            ft.Container(
                                expand=True,
                            ),

                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Edit",
                                on_click=edit_note,
                            ),

                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Delete",
                                on_click=delete_note,
                            ),
                        ],
                    ),

                    ft.Divider(),

                    ft.Text(
                        note["content"],
                    ),
                ],
            ),
        )

        notes_list.controls.append(card)

    # ---------- CLOSE DIALOG ----------

    def close_dialog():

        dialog.open = False

        title_field.value = ""
        content_field.value = ""

        page.update()

    # ---------- CREATE NOTE ----------

    def create_note(e):

        title = title_field.value.strip()
        content = content_field.value.strip()

        if not title or not content:

            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(
                        "Please enter both a title and content."
                    )
                )
            )

            return

        notes.append(
            {
                "title": title,
                "content": content,
            }
        )

        title_field.value = ""
        content_field.value = ""

        dialog.open = False

        refresh_notes()

        page.update()

    # ---------- NEW NOTE BUTTON ----------

    def open_new_note(e):

        title_field.value = ""
        content_field.value = ""

        dialog.title = ft.Text("Create Note")

        dialog.actions = [
            ft.TextButton(
                "Cancel",
                on_click=lambda e: close_dialog(),
            ),

            ft.ElevatedButton(
                "Create",
                on_click=create_note,
            ),
        ]

        page.show_dialog(dialog)

    # ---------- INITIAL LOAD ----------

    refresh_notes()

    # ---------- PAGE ----------

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                "📝 Notes",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                            ),

                            ft.Text(
                                "Create and organize your study notes.",
                                color="#64748B",
                            ),
                        ],
                        expand=True,
                    ),

                    ft.ElevatedButton(
                        "New Note",
                        icon=ft.Icons.ADD,
                        on_click=open_new_note,
                    ),
                ],
            ),

            ft.Divider(),

            notes_list,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )