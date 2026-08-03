import flet as ft


def study_planner_view(page):

    # ---------- INPUT FIELDS ----------

    subject_field = ft.TextField(
        label="Subject",
        hint_text="e.g. Data Structures",
    )

    exam_date_field = ft.TextField(
        label="Exam / Deadline",
        hint_text="e.g. 15 August",
    )

    hours_field = ft.TextField(
        label="Available study hours per day",
        hint_text="e.g. 2",
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    topics_field = ft.TextField(
        label="Topics",
        hint_text="e.g. Trees, Graphs, Sorting, Hashing",
        multiline=True,
        min_lines=3,
        max_lines=5,
    )

    # ---------- RESULT ----------

    plan_output = ft.Column(
        spacing=10,
    )

    # ---------- GENERATE PLAN ----------

    def generate_plan(e):

        subject = subject_field.value.strip()
        exam_date = exam_date_field.value.strip()
        topics_text = topics_field.value.strip()
        hours_text = hours_field.value.strip()

        # ---------- VALIDATION ----------

        if not subject or not topics_text:

            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(
                        "Please enter a subject and topics."
                    )
                )
            )

            return

        try:
            hours_per_day = float(hours_text)

            if hours_per_day <= 0:
                raise ValueError

        except ValueError:

            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(
                        "Please enter a valid number of study hours."
                    )
                )
            )

            return

        # ---------- CONVERT TOPICS TO LIST ----------

        topics = [
            topic.strip()
            for topic in topics_text.split(",")
            if topic.strip()
        ]

        if not topics:
            return

        # ---------- CALCULATE STUDY TIME ----------

        total_minutes = int(hours_per_day * 60)

        minutes_per_topic = total_minutes // len(topics)

        # ---------- CLEAR OLD PLAN ----------

        plan_output.controls.clear()

        # ---------- HEADER ----------

        plan_output.controls.append(
            ft.Container(
                padding=20,
                border_radius=12,
                bgcolor="#FFFFFF",
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "📚 Your Study Plan",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                        ),

                        ft.Text(
                            subject,
                            size=18,
                        ),

                        ft.Text(
                            f"Exam / Deadline: "
                            f"{exam_date or 'Not specified'}",
                            color="#64748B",
                        ),

                        ft.Text(
                            f"Available study time: "
                            f"{hours_per_day:g} hours/day",
                            color="#64748B",
                        ),
                    ],
                ),
            )
        )

        # ---------- GENERATE TOPIC SESSIONS ----------

        for index, topic in enumerate(topics):

            if index == 0:
                session_type = "📖 Learn"

            elif index % 2 == 1:
                session_type = "🧠 Practice"

            else:
                session_type = "🔄 Revise"

            duration = f"{minutes_per_topic} minutes"

            plan_output.controls.append(
                ft.Container(
                    padding=20,
                    border_radius=12,
                    bgcolor="#FFFFFF",
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        topic,
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                    ),

                                    ft.Text(
                                        session_type,
                                        color="#64748B",
                                    ),
                                ],
                                expand=True,
                            ),

                            ft.Text(
                                duration,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                )
            )

        # ---------- FINAL REVISION ----------

        plan_output.controls.append(
            ft.Container(
                padding=20,
                border_radius=12,
                bgcolor="#FFFFFF",
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "🔄 Final Revision",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),

                        ft.Text(
                            "Review all topics and solve practice questions.",
                            color="#64748B",
                        ),

                        ft.Text(
                            "30 minutes",
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),
            )
        )

        page.update()

    # ---------- BUTTON ----------

    generate_button = ft.ElevatedButton(
        "Generate Study Plan",
        icon=ft.Icons.AUTO_AWESOME,
        on_click=generate_plan,
    )

    # ---------- PAGE ----------

    return ft.Column(
        controls=[
            ft.Text(
                "🤖 AI Study Planner",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),

            ft.Text(
                "Create a personalized study plan.",
                color="#64748B",
            ),

            ft.Divider(),

            ft.Container(
                padding=20,
                border_radius=12,
                bgcolor="#FFFFFF",
                content=ft.Column(
                    controls=[
                        subject_field,
                        exam_date_field,
                        hours_field,
                        topics_field,
                        generate_button,
                    ],
                ),
            ),

            ft.Container(height=10),

            plan_output,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )