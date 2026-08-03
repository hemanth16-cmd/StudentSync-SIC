import flet as ft
from app.database import Database
from app.theme import get_text_primary, get_text_secondary
from components.common_widgets import create_card, create_section_header

def workout_view(page: ft.Page, dark_mode: bool = True) -> ft.Control:
    workouts_list = ft.ListView(expand=True, spacing=10, padding=0)

    name_input = ft.TextField(label="Workout Name (e.g., Push Day)", autofocus=True)
    type_dropdown = ft.Dropdown(
        label="Workout Type",
        value="strength",
        options=[
            ft.dropdown.Option("strength", "Strength"),
            ft.dropdown.Option("cardio", "Cardio"),
            ft.dropdown.Option("yoga", "Yoga/Flexibility"),
            ft.dropdown.Option("sports", "Sports"),
        ]
    )
    duration_input = ft.TextField(label="Duration (minutes)", value="30", keyboard_type=ft.KeyboardType.NUMBER)
    calories_input = ft.TextField(label="Calories Burned", value="200", keyboard_type=ft.KeyboardType.NUMBER)
    date_input = ft.TextField(label="Date (YYYY-MM-DD)", value=Database.today_str())

    dialog_container = ft.Container(visible=False)

    def load_workouts():
        workouts_list.controls.clear()
        try:
            updated_workouts = Database.get_workouts()
        except Exception as ex:
            print(f"Error loading workouts: {ex}")
            updated_workouts = []
        
        if not updated_workouts:
            workouts_list.controls.append(
                ft.Container(
                    content=ft.Text("No workouts logged yet. Hit 'Log Workout' to start!", italic=True, color="grey"),
                    padding=20
                )
            )
        else:
            for w in updated_workouts:
                workouts_list.controls.append(
                    create_card(
                        content=ft.Container(
                            content=ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(f"{w['name']} ({w.get('date', 'Today')})", weight=ft.FontWeight.BOLD, size=16, color=get_text_primary(dark_mode)),
                                            ft.Text(f"Type: {w['workout_type'].capitalize()} • {w['duration']} mins • {w['calories']} kcal", size=12, color=get_text_secondary(dark_mode)),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        expand=True,
                                        spacing=4,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color="red",
                                        on_click=lambda e, log_id=w["id"]: delete_workout(log_id)
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            padding=15,
                        ),
                        dark_mode=dark_mode
                    )
                )
        page.update()

    def delete_workout(log_id):
        try:
            Database.delete_workout(log_id)
        except Exception as ex:
            print(f"Error deleting workout: {ex}")
        load_workouts()

    def close_dialog(e):
        dialog_container.visible = False
        page.update()

    def save_workout(e):
        try:
            dur = float(duration_input.value)
            cal = int(calories_input.value)
        except ValueError:
            dur = 30
            cal = 200

        if name_input.value:
            try:
                Database.add_workout(
                    name=name_input.value,
                    workout_type=type_dropdown.value,
                    duration=int(dur),
                    calories=int(cal),
                    date_str=date_input.value if date_input.value else Database.today_str()
                )
            except Exception as ex:
                print(f"Error saving workout: {ex}")
            
            name_input.value = ""
            
        dialog_container.visible = False
        load_workouts()

    def open_dialog(e):
        dialog_container.visible = True
        page.update()

    # Using standard Row and Column centering instead of ft.alignment sub-modules
    dialog_card = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Log a New Workout", size=18, weight=ft.FontWeight.BOLD),
                            name_input,
                            type_dropdown,
                            duration_input,
                            calories_input,
                            date_input,
                            ft.Row(
                                [
                                    ft.TextButton("Cancel", on_click=close_dialog),
                                    ft.ElevatedButton("Save", on_click=save_workout),
                                ],
                                alignment=ft.MainAxisAlignment.END,
                                spacing=10,
                            ),
                        ],
                        tight=True,
                        spacing=15,
                    ),
                    padding=20,
                    bgcolor=ft.Colors.SURFACE,
                    border_radius=12,
                    width=400,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.with_opacity(0.6, ft.Colors.BLACK),
        expand=True,
    )
    
    dialog_container.content = dialog_card

    load_workouts()

    return ft.Stack(
        [
            ft.Column(
                [
                    ft.Row(
                        [
                            create_section_header(
                                "Workout Tracker",
                                "Log and track your physical training sessions",
                                dark_mode=dark_mode,
                            ),
                            ft.ElevatedButton("Log Workout", icon=ft.Icons.ADD, on_click=open_dialog),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=10, color="transparent"),
                    ft.Container(content=workouts_list, expand=True),
                ],
                spacing=10,
                expand=True,
                scroll=ft.ScrollMode.HIDDEN,
            ),
            dialog_container,
        ],
        expand=True,
    )