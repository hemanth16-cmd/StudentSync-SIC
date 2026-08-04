import flet as ft
from datetime import datetime, timedelta
from app.database import Database

def diet_view(page: ft.Page):
    current_date = datetime.now()

    def get_date_str():
        return current_date.strftime("%Y-%m-%d")

    date_text = ft.Text(current_date.strftime("%Y-%m-%d"), size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    
    calories_burned_text = ft.Text("0 / 2000 kcal", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    calorie_progress = ft.ProgressBar(value=0, width=200, color=ft.Colors.GREEN_400, bgcolor=ft.Colors.GREY_800)
    
    protein_text = ft.Text("0g / 130g", size=12, color=ft.Colors.WHITE70)
    carbs_text = ft.Text("0g / 200g", size=12, color=ft.Colors.WHITE70)
    fats_text = ft.Text("0g / 60g", size=12, color=ft.Colors.WHITE70)
    
    water_text = ft.Text("0 / 2500 ml", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400)
    meals_column = ft.Column(spacing=10)

    def load_data():
        try:
            date_str = get_date_str()
            date_text.value = date_str
            
            entries = Database.get_diet_logs_by_date(date_str) or []
            water_ml = Database.get_water_intake(date_str) or 0
            settings = Database.get_settings() or {}
            
            target_calories = int(settings.get("calorie_target", 2000) or 2000)
            target_protein = int(settings.get("protein_target", 130) or 130)
            target_carbs = int(settings.get("carb_target", 200) or 200)
            target_fats = int(settings.get("fat_target", 60) or 60)
            target_water = int(settings.get("water_target", 2500) or 2500)

            total_cals = sum(int(e.get("calories", 0) or 0) for e in entries)
            total_protein = sum(int(e.get("protein", 0) or 0) for e in entries)
            total_carbs = sum(int(e.get("carbs", 0) or 0) for e in entries)
            total_fats = sum(int(e.get("fat", 0) or 0) for e in entries)

            calories_burned_text.value = f"{total_cals} / {target_calories} kcal"
            calorie_progress.value = min(total_cals / target_calories, 1.0) if target_calories > 0 else 0
            
            protein_text.value = f"{total_protein}g / {target_protein}g"
            carbs_text.value = f"{total_carbs}g / {target_carbs}g"
            fats_text.value = f"{total_fats}g / {target_fats}g"
            
            water_text.value = f"{water_ml} / {target_water} ml"

            meals_column.controls.clear()
            if not entries:
                meals_column.controls.append(
                    ft.Container(
                        content=ft.Text("No food logged for this date.", color=ft.Colors.GREY_500, italic=True),
                        alignment=ft.alignment.center,
                        padding=20
                    )
                )
            else:
                for entry in entries:
                    entry_id = entry.get("id")
                    food_name = entry.get("name", entry.get("food_name", "Unknown"))
                    meal_type = entry.get("meal", entry.get("meal_type", "Meal"))
                    cals = entry.get("calories", 0) or 0
                    p = entry.get("protein", 0) or 0
                    c = entry.get("carbs", 0) or 0
                    f = entry.get("fat", 0) or 0

                    meals_column.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Column([
                                    ft.Text(food_name, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    ft.Text(f"{meal_type} • {cals} kcal", size=12, color=ft.Colors.WHITE70),
                                ], expand=True),
                                ft.Row([
                                    ft.Text(f"P: {p}g | C: {c}g | F: {f}g", size=11, color=ft.Colors.GREY_400),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color=ft.Colors.RED_400,
                                        icon_size=18,
                                        on_click=lambda ev, eid=entry_id: delete_entry(eid)
                                    )
                                ])
                            ]),
                            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                            padding=12,
                            border_radius=8,
                            border=ft.BorderSide(1, ft.Colors.GREY_800)
                        )
                    )
            page.update()
        except Exception as ex:
            print(f"Error loading diet data: {ex}")

    def change_date(delta):
        nonlocal current_date
        current_date += timedelta(days=delta)
        load_data()

    def delete_entry(entry_id):
        if entry_id is not None:
            Database.delete_diet_entry(entry_id)
            load_data()

    def open_add_dialog(e):
        food_name_field = ft.TextField(label="Food Name", border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE)
        meal_type_dropdown = ft.Dropdown(
            label="Meal Type",
            options=[
                ft.dropdown.Option("Breakfast"),
                ft.dropdown.Option("Lunch"),
                ft.dropdown.Option("Dinner"),
                ft.dropdown.Option("Snacks"),
            ],
            value="Breakfast",
            border_color=ft.Colors.GREY_700,
            color=ft.Colors.WHITE
        )
        cals_field = ft.TextField(label="Calories (kcal)", keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE)
        protein_field = ft.TextField(label="Protein (g)", keyboard_type=ft.KeyboardType.NUMBER, value="0", border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE)
        carbs_field = ft.TextField(label="Carbs (g)", keyboard_type=ft.KeyboardType.NUMBER, value="0", border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE)
        fat_field = ft.TextField(label="Fat (g)", keyboard_type=ft.KeyboardType.NUMBER, value="0", border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE)

        def close_dlg(ev):
            dlg.open = False
            page.update()

        def save_entry(ev):
            try:
                cals_val = float(cals_field.value) if cals_field.value and cals_field.value.strip() else 0.0
                protein_val = float(protein_field.value) if protein_field.value and protein_field.value.strip() else 0.0
                carbs_val = float(carbs_field.value) if carbs_field.value and carbs_field.value.strip() else 0.0
                fat_val = float(fat_field.value) if fat_field.value and fat_field.value.strip() else 0.0

                Database.add_diet_entry(
                    name=food_name_field.value.strip() if food_name_field.value else "Item",
                    calories=int(cals_val),
                    meal=meal_type_dropdown.value or "Breakfast",
                    date_str=get_date_str(),
                    protein=protein_val,
                    carbs=carbs_val,
                    fat=fat_val
                )
                dlg.open = False
                page.update()
                load_data()
            except Exception as ex:
                print(f"Error saving food entry: {ex}")

        dlg = ft.AlertDialog(
            title=ft.Text("Log Food Item", color=ft.Colors.WHITE),
            content=ft.Column([
                food_name_field,
                meal_type_dropdown,
                cals_field,
                protein_field,
                carbs_field,
                fat_field
            ], tight=True, width=300, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=close_dlg),
                ft.ElevatedButton("Save", on_click=save_entry, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
            ],
            bgcolor=ft.Colors.GREY_900
        )
        
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def add_water(amount):
        date_str = get_date_str()
        Database.add_water_intake(int(amount), date_str)
        load_data()

    def reset_to_today(e):
        nonlocal current_date
        current_date = datetime.now()
        load_data()

    date_bar = ft.Row([
        ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, icon_color=ft.Colors.WHITE, on_click=lambda e: change_date(-1)),
        date_text,
        ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, icon_color=ft.Colors.WHITE, on_click=lambda e: change_date(1)),
        ft.TextButton("Today", on_click=reset_to_today),
    ], alignment=ft.MainAxisAlignment.START)

    overview_row = ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Text("Calories", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70),
                calories_burned_text,
                calorie_progress
            ], spacing=8),
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            padding=16,
            border_radius=10,
            expand=True,
            border=ft.BorderSide(1, ft.Colors.GREY_800)
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Macros (P / C / F)", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70),
                ft.Row([
                    ft.Column([ft.Text("Protein", size=10, color=ft.Colors.GREY_400), protein_text]),
                    ft.Column([ft.Text("Carbs", size=10, color=ft.Colors.GREY_400), carbs_text]),
                    ft.Column([ft.Text("Fats", size=10, color=ft.Colors.GREY_400), fats_text]),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=8),
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            padding=16,
            border_radius=10,
            expand=True,
            border=ft.BorderSide(1, ft.Colors.GREY_800)
        ),
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Water Intake", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70),
                    water_text
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.ElevatedButton("+ 250ml", on_click=lambda e: add_water(250), bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, scale=0.8),
                    ft.ElevatedButton("+ 500ml", on_click=lambda e: add_water(500), bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, scale=0.8),
                    ft.ElevatedButton("- 250ml", on_click=lambda e: add_water(-250), bgcolor=ft.Colors.GREY_800, color=ft.Colors.WHITE, scale=0.8),
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
            ], spacing=8),
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            padding=16,
            border_radius=10,
            expand=True,
            border=ft.BorderSide(1, ft.Colors.GREY_800)
        ),
    ], spacing=15)

    meals_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Today's Meals", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.ElevatedButton("Add Food", icon=ft.Icons.ADD, on_click=open_add_dialog, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(color=ft.Colors.GREY_800),
            meals_column
        ]),
        bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
        padding=16,
        border_radius=10,
        border=ft.BorderSide(1, ft.Colors.GREY_800)
    )

    load_data()

    return ft.Container(
        content=ft.ListView([
            date_bar,
            overview_row,
            meals_section
        ], spacing=15, padding=20, expand=True),
        bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE),
        expand=True
    )