from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton,
    QLineEdit, QComboBox, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QColorDialog,  QInputDialog, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt
import json, os
from gui.plan_window import PlanWindow

class CalendarView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.time_slots = []
        start_minutes = 9 * 60  #9AM
        end_minutes = 15 * 60 + 30  #3:30PM
        for minutes in range(start_minutes, end_minutes, 30):
            hour = minutes // 60
            minute = minutes % 60
            self.time_slots.append(f"{hour:02}:{minute:02}")

        self.plans = {}
        self.current_plan = None

        self.setWindowTitle("Weekly Scheduler")
        self.setGeometry(100, 100, 1200, 500)
        
        #layout setup
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar)
        self.setup_sidebar(sidebar_layout)
        main_layout.addWidget(self.sidebar, 1)

        #calendar view
        self.calendar = QWidget()
        calendar_layout = QGridLayout(self.calendar)
        self.setup_calendar(calendar_layout)
        main_layout.addWidget(self.calendar, 3)

        self.setCentralWidget(central_widget)

        self.initialize_plans()

    def setup_sidebar(self, layout):
        self.course_name_input = QLineEdit()
        self.course_name_input.setPlaceholderText("Course name")

        self.course_code_input = QLineEdit()
        self.course_code_input.setPlaceholderText("Course code")

        self.credits_input = QLineEdit()
        self.credits_input.setPlaceholderText("credits")

        self.day_input = QComboBox()
        self.day_input.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])

        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Time Slot (10:00-12:00)")

        #adding a course
        self.add_course_button = QPushButton("Add Course")
        self.add_course_button.clicked.connect(self.add_course_to_calendar)

        #custom time hours customization
        self.start_hour_input = QLineEdit()
        self.start_hour_input.setPlaceholderText("Start Hour (ex: 08:00)")

        self.end_hour_input = QLineEdit()
        self.end_hour_input.setPlaceholderText("End Hour (ex: 18:00)")

        self.update_slots_button = QPushButton("Update Time slots")
        self.update_slots_button.clicked.connect(self.update_time_slots)

        #plans config
        self.plans = {}
        self.current_plan = None

        #dropdown for the plan selection
        self.plan_selector = QComboBox()
        # self.plan_selector.addItems(self.plans.keys())
        self.plan_selector.currentIndexChanged.connect(self.switch_plan) #triggers when a selection item changes
        layout.addWidget(QLabel("Select or create plan:"))
        layout.addWidget(self.plan_selector)

        #creating and selecting the new plan
        self.new_plan_button = QPushButton("Create new plan")
        self.new_plan_button.clicked.connect(self.create_new_plan)
        layout.addWidget(self.new_plan_button)

        self.open_plan_button = QPushButton("Open selected plan")
        self.open_plan_button.clicked.connect(self.open_plan_window)
        layout.addWidget(self.open_plan_button)


        #save and load schedule
        self.save_button = QPushButton("Save Schedule")
        self.save_button.clicked.connect(self.save_schedule)

        #self.load_button = QPushButton("Load Schedule")
        #self.load_button.clicked.connect(self.load_schedule)

        #total credits count
        self.total_credits_label = QLabel("Total Credits: 0")
        layout.addWidget(self.total_credits_label)



        #added to layout
        layout.addWidget(QLabel("Add Course:"))
        layout.addWidget(self.course_name_input)
        layout.addWidget(self.course_code_input)
        layout.addWidget(self.credits_input)
        layout.addWidget(self.day_input)
        layout.addWidget(self.time_input)
        layout.addWidget(self.add_course_button)
        layout.addWidget(QLabel("Custom Time slots:"))
        layout.addWidget(self.start_hour_input)
        layout.addWidget(self.end_hour_input)
        layout.addWidget(self.update_slots_button)
        layout.addWidget(self.add_course_button)
        layout.addWidget(self.save_button)
        #layout.addWidget(self.load_button)

        #line break
        layout.addWidget(QLabel(""))

        #delete button
        self.delete_button = QPushButton("Delete Selected Block")
        self.delete_button.clicked.connect(self.delete_selected_block)
        layout.addWidget(self.delete_button)

        #change block color button
        self.color_button = QPushButton("Change Block Color")
        self.color_button.clicked.connect(self.change_selected_block_color)
        layout.addWidget(self.color_button)


        layout.addStretch()
        #init total credits count
        self.total_credits = 0
        self.course_codes = set()

    def update_total_credits(self):
        self.total_credits_label.setText(f"Total Credits: {self.total_credits}")
    
    def setup_calendar(self, layout):
    #removes any existing widgets in the layout
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

        #table widget
        self.calendar_table = QTableWidget(len(self.time_slots), 5)  #rows: time slots, columns: days
        self.calendar_table.setHorizontalHeaderLabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        self.calendar_table.setVerticalHeaderLabels(self.time_slots)
        self.calendar_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.calendar_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.calendar_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)


        #responsive resizing enabled
        self.calendar_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.calendar_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        #default table style
        self.calendar_table.setStyleSheet("gridline-color: white;")
        self.calendar_table.horizontalHeader().setDefaultSectionSize(100)
        self.calendar_table.verticalHeader().setDefaultSectionSize(50)

        # Add the table to the layout
        layout.addWidget(self.calendar_table)

    def add_course_to_calendar(self):
        course_name = self.course_name_input.text()
        course_code = self.course_code_input.text()
        credits = self.credits_input.text()
        day = self.day_input.currentText()
        time_slot = self.time_input.text()

        if not course_name or not course_code or not time_slot or not credits.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please fill all fields correctly")
            return

        try:
            start_time, end_time = time_slot.split("-")
            start_index = self.time_slots.index(start_time)
            end_index = self.time_slots.index(end_time)
        except ValueError:
            QMessageBox.warning(self, "Invalid Time Slot", "Please enter a valid time slot (10:00-12:00)")
            return

        day_to_col = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
        col = day_to_col.get(day, -1)
        if col == -1:
            QMessageBox.warning(self, "Invalid day", f"'{day}' is not a valid day")
            return

        for row in range(start_index, end_index):
            if self.calendar_table.item(row, col):
                QMessageBox.warning(self, "Schedule conflict", "This time slot is already occupied")
                return

        #adds the course
        span_rows = end_index - start_index
        self.calendar_table.setSpan(start_index, col, span_rows, 1)
        course_item = QTableWidgetItem(f"{course_name}\nCredits: {credits}")
        course_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        course_item.setBackground(Qt.GlobalColor.cyan)
        self.calendar_table.setItem(start_index, col, course_item)

        course_data = {
            "name": course_name,
            "credits": int(credits),
            "start_time": start_time,
            "end_time": end_time,
            "day": day
        }
        self.plans[self.current_plan]["courses"].append(course_data)
        print(f"Added course '{course_name}' to plan '{self.current_plan}'")

    #function to remove the course block on the table
    def delete_selected_block(self):
        selected_items = self.calendar_table.selectedItems()
        if not selected_items:
            print("No block selected")
            return

        item = selected_items[0]
        row = item.row()
        col = item.column()

        #get course details
        course_data = item.text().split("\n")
        course_name = course_data[0]
        credits = int(course_data[1].replace("Credits: ", ""))
        course_code = course_name

        #removes the block
        self.calendar_table.removeCellWidget(row, col)
        self.calendar_table.clearSpans()
        self.calendar_table.takeItem(row, col)

        print(f"Removed course: {course_name}")

        #adjust total credits sum
        if course_code in self.course_codes:
            self.course_codes.remove(course_code)
            self.total_credits -= credits
            self.update_total_credits()

    def update_time_slots(self):
        #gets the time range from the user input
        start_hour = self.start_hour_input.text()
        end_hour = self.end_hour_input.text()

        try:
            #input validation
            start_parts = list(map(int, start_hour.split(":")))
            end_parts = list(map(int, end_hour.split(":")))

            start_minutes = start_parts[0] * 60 + start_parts[1]
            end_minutes = end_parts[0] * 60 + end_parts[1]

            if start_minutes >= end_minutes or start_minutes < 0 or end_minutes > 24 * 60:
                raise ValueError("Invalid time range")

            #generates time slots with 30 min intervals
            self.time_slots = []
            for minutes in range(start_minutes, end_minutes, 30):
                hour = minutes // 60
                minute = minutes % 60
                self.time_slots.append(f"{hour:02}:{minute:02}")

            #regenerates the grid
            self.setup_calendar(self.calendar.layout())
        except ValueError:
            print("Invalid time range format. Use HH:MM")
    
    #saving/loading section

    def save_schedule(self):
        #saves the active plan first
        self.save_active_plan()

        #json file
        try:
            with open("all_plans.json", "w") as file:
                json.dump(self.plans, file, indent=4)
            print("All plans saved successfully")
        except Exception as e:
            print(f"Error saving plans: {e}")

    def load_schedule(self):
        try:
            with open("all_plans.json", "r") as file:
                loaded_plans = json.load(file)

            #validates the loaded plans
            if not loaded_plans or not isinstance(loaded_plans, dict):
                QMessageBox.warning(self, "Invalid File", "The file does not contain valid plans")
                return

            self.plans = loaded_plans

            #validate if plans exist
            if not self.plans:
                QMessageBox.warning(self, "No Plans Found", "No plans were found in the saved file")
                self.prompt_new_plan()
                return

            first_plan = list(self.plans.keys())[0]
            self.current_plan = first_plan

            #updates the dropdown menu
            self.plan_selector.blockSignals(True)  # Block signals during dropdown population
            self.plan_selector.clear()
            self.plan_selector.addItems(self.plans.keys())
            self.plan_selector.setCurrentText(self.current_plan)
            self.plan_selector.blockSignals(False)

            # Load the active plan into the calendar
            self.load_plan_into_calendar(self.plans[self.current_plan])
        except FileNotFoundError:
            print("No saved plans found")
            self.prompt_new_plan()
        except Exception as e:
            print(f"Error loading plans: {e}")

    def get_day_from_col(self, col):
        #column index to day mappings
        col_to_day = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday"}
        return col_to_day.get(col, "Unknown")

    def load_plan_to_calendar(self, plan_data):
        if not plan_data:
                print("Plan data is empty")
                return

        self.setup_calendar(self.calendar.layout())

        try:
            for course in plan_data.get("courses", []):
                start_index = self.time_slots.index(course["start_time"])
                end_index = self.time_slots.index(course["end_time"])
                day_to_col = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
                col = day_to_col.get(course["day"], -1)

                if col == -1:
                    print(f"Invalid day {course['day']} in course {course['name']}. Skipping.")
                    continue

                span_rows = end_index - start_index
                self.calendar_table.setSpan(start_index, col, span_rows, 1)
                course_item = QTableWidgetItem(f"{course['name']}\nCredits: {course['credits']}")
                course_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                course_item.setBackground(Qt.GlobalColor.cyan)
                self.calendar_table.setItem(start_index, col, course_item)

            print(f"Plan '{self.current_plan}' loaded into calendar")
        except Exception as e:
            print(f"Error loading plan into calendar: {e}")

    def change_selected_block_color(self):
        selected_items = self.calendar_table.selectedItems()
        if not selected_items:
            print("No block selected")
            return

        item = selected_items[0]

        #color dialog
        color = QColorDialog.getColor()

        if color.isValid():
            #update color
            item.setBackground(color)
            print("Block color updated.")

    def create_new_plan(self):
        plan_name, ok = QInputDialog.getText(self, "Create new plan", "Enter a name for the new plan:")
        if ok and plan_name:
            if plan_name in self.plans:
                QMessageBox.warning(self, "Duplicate found", "A plan with this name already exists")
                return
            
            self.save_active_plan()

            self.plans[plan_name] = {"courses": []}
            self.current_plan = plan_name
            self.plan_selector.addItem(plan_name)
            self.plan_selector.setCurrentText(plan_name)

            self.setup_calendar(self.calendar.layout())

    def open_plan_window(self):
        selected_plan = self.plan_selector.currentText()

        if selected_plan not in self.plans:
            QMessageBox.warning(self, "No Plan Selected", "Please select a valid plan to open")
            return

        #opens the plan in a new window
        plan_window = PlanWindow(
            plan_name=selected_plan,
            schedule_data=self.plans[selected_plan],
            time_slots=self.time_slots,
            parent=self
        )
        plan_window.show()

    def switch_plan(self):
        selected_plan = self.plan_selector.currentText()

        # checks for the existing plans
        if selected_plan not in self.plans:
            QMessageBox.warning(self, "Invalid Plan", f"The plan '{selected_plan}' does not exist")
            return

        #save before switching
        self.save_active_plan()

        #clears the calendar table
        self.calendar_table.clearContents()
        self.calendar_table.clearSpans()

        self.current_plan = selected_plan
        self.load_plan_into_calendar(self.plans[self.current_plan])

        print(f"Switched to plan: {self.current_plan}")

    def update_plan_selector(self):
        self.plan_selector.clear()
        self.plan_selector.addItems(self.plans.keys())
        self.plan_selector.setCurrentText(self.current_plan)

    def save_active_plan(self):
        if not self.current_plan:
            QMessageBox.warning(self, "No plan selected", "Please select or create a plan before saving")
            return

        if self.current_plan not in self.plans:
            self.plans[self.current_plan] = {"courses": []}

        self.plans[self.current_plan]["courses"] = []
        for row in range(self.calendar_table.rowCount()):
            for col in range(self.calendar_table.columnCount()):
                item = self.calendar_table.item(row, col)
                if item:
                    span = self.calendar_table.rowSpan(row, col)
                    start_time = self.time_slots[row]
                    end_time = self.time_slots[row + span] if (row + span) < len(self.time_slots) else self.time_slots[-1]

                    self.plans[self.current_plan]["courses"].append({
                        "name": item.text().split("\n")[0],
                        "credits": int(item.text().split("\n")[1].replace("Credits: ", "")),
                        "day": self.get_day_from_col(col),
                        "start_time": start_time,
                        "end_time": end_time
                    })

        try:
            with open("all_plans.json", "w") as file:
                json.dump(self.plans, file, indent=4)
            print(f"Plan '{self.current_plan}' saved successfully.")
        except Exception as e:
            print(f"Error saving plans: {e}")


    def load_plan_into_calendar(self, plan_data):
        if not plan_data or "courses" not in plan_data:
            print("Plan data is empty or invalid")
            self.setup_calendar(self.calendar.layout())
            return

        for course in plan_data["courses"]:
            try:
                start_index = self.time_slots.index(course["start_time"])
                end_index = self.time_slots.index(course["end_time"])
                day_to_col = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
                col = day_to_col.get(course["day"], -1)

                if col == -1:
                    print(f"Invalid day '{course['day']}' in course '{course['name']}'. Skipping.")
                    continue

                span_rows = end_index - start_index
                course_item = QTableWidgetItem(f"{course['name']}\nCredits: {course['credits']}")
                course_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                course_item.setBackground(Qt.GlobalColor.cyan)
                self.calendar_table.setSpan(start_index, col, span_rows, 1)
                self.calendar_table.setItem(start_index, col, course_item)
            except ValueError:
                print(f"Invalid time slot for course '{course['name']}'. Skipping.")

    
    def initialize_plans(self):
        #checks if the json file already exists
        if os.path.exists("all_plans.json"):
            self.load_schedule()
        else:
            self.prompt_new_plan()

        if not self.current_plan or self.current_plan not in self.plans:
            print("No valid plan found. Prompting user to create a new plan.")
            self.prompt_new_plan()
        
        if self.current_plan and self.current_plan in self.plans:
            self.load_plan_into_calendar(self.plans[self.current_plan])

    def prompt_new_plan(self):
        if not hasattr(self, "time_slots"):
            QMessageBox.critical(self, "Initialization error", "Plan selector is not initialized")

        #new plan creation
        new_plan_name, ok = QInputDialog.getText(self, "Create new plan", "No plans found. Create a new plan:")

        if ok and new_plan_name.strip():
            self.plans = {new_plan_name: {"time_slots": self.time_slots, "courses": []}}
            self.current_plan = new_plan_name

            self.plan_selector.clear()
            self.plan_selector.addItem(new_plan_name)
            self.plan_selector.setCurrentText(new_plan_name)

            self.calendar_table.clearContents()
            self.calendar_table.clearSpans()

            print(f"Plan '{new_plan_name}' created and set as active")
        else:
            QMessageBox.critical(self, "No Plan Created", "A plan must be created to proceed")
            exit()