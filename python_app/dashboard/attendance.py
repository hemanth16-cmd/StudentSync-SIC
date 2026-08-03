import flet as ft


def attendance_view(page):

    # ---------- SUBJECT DATA ----------

    subjects = [
        {
            "name": "Data Structures",
            "held": 20,
            "attended": 17,
        },
        {
            "name": "Mathematics",
            "held": 18,
            "attended": 14,
        },
        {
            "name": "Web Development",
            "held": 22,
            "attended": 20,
        },
    ]

    # ---------- CALCULATE PERCENTAGE ----------

    def calculate_percentage(held, attended):

        if held == 0:
            return 0

        return round((attended / held) * 100)

    # ---------- UI REFERENCES ----------

    overall_percentage_text = ft.Text(
        size=40,
        weight=ft.FontWeight.BOLD,
    )

    overall_progress = ft.ProgressBar()

    overall_classes_text = ft.Text(
        color="#64748B",
    )

    subject_list = ft.Column(
        spacing=12,
    )

    # ---------- UPDATE OVERALL ----------

    def update_overall():

        total_held = sum(
            subject["held"]
            for subject in subjects
        )

        total_attended = sum(
            subject["attended"]
            for subject in subjects
        )

        percentage = calculate_percentage(
            total_held,
            total_attended,
        )

        overall_percentage_text.value = f"{percentage}%"

        overall_progress.value = percentage / 100

        overall_classes_text.value = (
            f"{total_attended} attended "
            f"out of {total_held} classes"
        )

    # ---------- UPDATE SUBJECT CARD ----------

    def update_subject_card(
        subject,
        percentage_text,
        progress_bar,
        status_text,
    ):

        percentage = calculate_percentage(
            subject["held"],
            subject["attended"],
        )

        percentage_text.value = f"{percentage}%"

        progress_bar.value = percentage / 100

        if percentage < 75:
            status_text.value = "⚠️ Low attendance"
        else:
            status_text.value = "✓ Good attendance"

        update_overall()

        page.update()

    # ---------- CREATE SUBJECT CARD ----------

    def create_subject_card(subject):

        percentage = calculate_percentage(
            subject["held"],
            subject["attended"],
        )

        percentage_text = ft.Text(
            f"{percentage}%",
            size=20,
            weight=ft.FontWeight.BOLD,
        )

        progress_bar = ft.ProgressBar(
            value=percentage / 100,
        )

        status_text = ft.Text(
            "⚠️ Low attendance"
            if percentage < 75
            else "✓ Good attendance",
            color="#64748B",
        )

        classes_text = ft.Text(
            f"{subject['attended']} attended "
            f"out of {subject['held']} classes",
            color="#64748B",
        )

        def mark_present(e):

            subject["held"] += 1
            subject["attended"] += 1

            classes_text.value = (
                f"{subject['attended']} attended "
                f"out of {subject['held']} classes"
            )

            update_subject_card(
                subject,
                percentage_text,
                progress_bar,
                status_text,
            )

        def mark_absent(e):

            subject["held"] += 1

            classes_text.value = (
                f"{subject['attended']} attended "
                f"out of {subject['held']} classes"
            )

            update_subject_card(
                subject,
                percentage_text,
                progress_bar,
                status_text,
            )

        return ft.Container(
            padding=20,
            border_radius=12,
            bgcolor="#FFFFFF",
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                subject["name"],
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(expand=True),
                            percentage_text,
                        ],
                    ),

                    progress_bar,

                    classes_text,

                    status_text,

                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "✓ Present",
                                on_click=mark_present,
                            ),

                            ft.OutlinedButton(
                                "✕ Absent",
                                on_click=mark_absent,
                            ),
                        ],
                    ),
                ],
            ),
        )

    # ---------- LOAD SUBJECTS ----------

    for subject in subjects:

        subject_list.controls.append(
            create_subject_card(subject)
        )

    # ---------- INITIAL OVERALL ----------

    update_overall()

    # ---------- PAGE ----------

    return ft.Column(
        controls=[
            ft.Text(
                "📊 Attendance",
                size=28,
                weight=ft.FontWeight.BOLD,
            ),

            ft.Text(
                "Track your attendance across all subjects.",
                color="#64748B",
            ),

            ft.Divider(),

            # Overall attendance
            ft.Container(
                padding=25,
                border_radius=12,
                bgcolor="#FFFFFF",
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Overall Attendance",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),

                        overall_percentage_text,

                        overall_progress,

                        overall_classes_text,
                    ],
                ),
            ),

            ft.Container(height=10),

            ft.Text(
                "Subjects",
                size=20,
                weight=ft.FontWeight.BOLD,
            ),

            subject_list,
        ],
        scroll=ft.ScrollMode.AUTO,
    )