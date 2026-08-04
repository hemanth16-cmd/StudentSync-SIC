import flet as ft
from app.database import Database

# Global runtime cache to keep selected program and semester across page switches
_current_user_program = "B.Tech"
_current_user_semester = "Semester 1"

def subject_view(page: ft.Page):
    global _current_user_program, _current_user_semester
    
    selected_program = ft.Ref[ft.Dropdown]()
    selected_semester = ft.Ref[ft.Dropdown]()
    
    subjects_column = ft.Column(spacing=10)

    programs = [
        "B.Tech",
        "BCA",
        "B.Sc Computer Science",
        "BBA",
        "MBA",
        "Law (B.A. LL.B / LL.B)",
        "B.Com",
        "Engineering - Other"
    ]
    
    semesters = [f"Semester {i}" for i in range(1, 11)]

    def load_subjects():
        try:
            current_prog = selected_program.current.value if selected_program.current and selected_program.current.value else _current_user_program
            current_sem = selected_semester.current.value if selected_semester.current and selected_semester.current.value else _current_user_semester

            all_subjects = Database.get_subjects() or []
            
            # Filter subjects dynamically by the selected program and semester
            subjects = [
                s for s in all_subjects 
                if s.get("program", current_prog) == current_prog and s.get("semester", current_sem) == current_sem
            ]
            
            subjects_column.controls.clear()
            if not subjects:
                subjects_column.controls.append(
                    ft.Container(
                        content=ft.Text(f"No subjects found for {current_prog} - {current_sem}. Click 'Add Subject' to begin.", color=ft.Colors.GREY_500, italic=True),
                        alignment=ft.alignment.center,
                        padding=20
                    )
                )
            else:
                for subj in subjects:
                    subj_id = subj.get("id")
                    name = subj.get("name", "Unknown Subject")
                    code = subj.get("code", "N/A")
                    credits = int(subj.get("credits", 3))
                    total_hours = subj.get("total_classes", credits * 15)
                    teacher = subj.get("teacher", "Not Assigned")
                    room = subj.get("room", "TBA")

                    subjects_column.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Column([
                                    ft.Row([
                                        ft.Text(name, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=16),
                                        ft.Container(
                                            content=ft.Text(code, size=11, color=ft.Colors.CYAN_400),
                                            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.CYAN_400),
                                            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                            border_radius=4
                                        )
                                    ], spacing=10),
                                    ft.Text(f"Faculty: {teacher}  •  Room: {room}", size=12, color=ft.Colors.WHITE70),
                                ], expand=True),
                                ft.Row([
                                    ft.Column([
                                        ft.Text(f"{credits} Credits", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400),
                                        ft.Text(f"{total_hours} Total Hours", size=11, color=ft.Colors.GREY_400),
                                    ], alignment=ft.MainAxisAlignment.CENTER),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color=ft.Colors.RED_400,
                                        icon_size=18,
                                        on_click=lambda ev, sid=subj_id: delete_subject(sid)
                                    )
                                ], spacing=15)
                            ]),
                            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                            padding=14,
                            border_radius=8,
                            border=ft.BorderSide(1, ft.Colors.GREY_800)
                        )
                    )
            page.update()
        except Exception as ex:
            print(f"Error loading subjects: {ex}")

    def on_filter_change(e):
        global _current_user_program, _current_user_semester
        if selected_program.current and selected_program.current.value:
            _current_user_program = selected_program.current.value
        if selected_semester.current and selected_semester.current.value:
            _current_user_semester = selected_semester.current.value
        load_subjects()

    def delete_subject(subj_id):
        if subj_id is not None:
            Database.delete_subject(subj_id)
            load_subjects()

    def open_add_subject_dialog(e):
        sem = selected_semester.current.value if selected_semester.current else _current_user_semester

        name_field = ft.TextField(label="Subject Name", border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE)
        code_field = ft.TextField(label="Subject Code (e.g., CS301)", border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE)
        credits_dropdown = ft.Dropdown(
            label="Credits",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
            value="4",
            border_color=ft.Colors.GREY_700,
            color=ft.Colors.WHITE
        )
        teacher_field = ft.TextField(label="Faculty Name", border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE)
        room_field = ft.TextField(label="Room (e.g., 304)", border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE)

        def close_dlg(ev):
            dlg.open = False
            page.update()

        def save_subject(ev):
            try:
                c_val = int(credits_dropdown.value or 3)
                n_val = name_field.value.strip() if name_field.value else "Untitled"
                code_val = code_field.value.strip() if code_field.value else "SUB000"
                tch_val = teacher_field.value.strip() if teacher_field.value else "Staff"
                rm_val = room_field.value.strip() if room_field.value else "TBA"
                
                active_prog = selected_program.current.value if selected_program.current else _current_user_program
                active_sem = selected_semester.current.value if selected_semester.current else _current_user_semester

                Database.add_subject(
                    name=n_val,
                    code=code_val,
                    teacher=tch_val,
                    credits=c_val,
                    room=rm_val,
                    program=active_prog,
                    semester=active_sem
                )

                dlg.open = False
                page.update()
                load_subjects()
                
                page.snack_bar = ft.SnackBar(ft.Text(f"Subject saved to {active_sem}!", color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN_700)
                page.snack_bar.open = True
                page.update()

            except Exception as ex:
                print(f"Error saving subject: {ex}")
                page.snack_bar = ft.SnackBar(ft.Text(f"Error saving: {ex}", color=ft.Colors.WHITE), bgcolor=ft.Colors.RED_700)
                page.snack_bar.open = True
                page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"Add Subject ({sem})", color=ft.Colors.WHITE),
            content=ft.Column([
                name_field,
                code_field,
                credits_dropdown,
                teacher_field,
                room_field,
                ft.Text("Note: Total hours will be automatically calculated (Credits × 15).", size=11, color=ft.Colors.GREY_400, italic=True)
            ], tight=True, width=380, spacing=10),
            actions=[
                ft.TextButton("Cancel", on_click=close_dlg),
                ft.ElevatedButton("Save Subject", on_click=save_subject, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
            ],
            bgcolor=ft.Colors.GREY_900
        )

        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    config_header = ft.Container(
        content=ft.Row([
            ft.Dropdown(
                ref=selected_program,
                label="Program",
                options=[ft.dropdown.Option(p) for p in programs],
                value=_current_user_program,
                width=220,
                border_color=ft.Colors.GREY_700,
                color=ft.Colors.WHITE,
                on_select=on_filter_change
            ),
            ft.Dropdown(
                ref=selected_semester,
                label="Semester",
                options=[ft.dropdown.Option(s) for s in semesters],
                value=_current_user_semester,
                width=180,
                border_color=ft.Colors.GREY_700,
                color=ft.Colors.WHITE,
                on_select=on_filter_change
            ),
        ], spacing=15, alignment=ft.MainAxisAlignment.START),
        padding=15,
        bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
        border_radius=10,
        border=ft.BorderSide(1, ft.Colors.GREY_800)
    )

    list_header = ft.Row([
        ft.Text("Subjects & Curriculum", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ft.ElevatedButton("Add Subject", icon=ft.Icons.ADD, on_click=open_add_subject_dialog, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    load_subjects()

    return ft.Container(
        content=ft.Column([
            config_header,
            list_header,
            ft.Divider(color=ft.Colors.GREY_800),
            ft.Container(
                content=ft.ListView(controls=subjects_column.controls, expand=True),
                expand=True
            )
        ], spacing=15, expand=True),
        padding=20,
        bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE),
        expand=True
    )