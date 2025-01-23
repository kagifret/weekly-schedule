from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton,
    QLineEdit, QComboBox, QGridLayout, QTextEdit
)
from PyQt6.QtCore import Qt
import json

class CalendarView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weekly Scheduler")
        self.setGeometry(100, 100, 1200, 500)

        #default init settings
        self.time_slots = []
        start_minutes = 9 * 60  #9AM
        end_minutes = 15 * 60 + 30  #3:30PM
        for minutes in range(start_minutes, end_minutes, 30):
            hour = minutes // 60
            minute = minutes % 60
            self.time_slots.append(f"{hour:02}:{minute:02}")

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

        #save and load schedule
        self.save_button = QPushButton("Save Schedule")
        self.save_button.clicked.connect(self.save_schedule)

        self.load_button = QPushButton("Load Schedule")
        self.load_button.clicked.connect(self.load_schedule)

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
        layout.addWidget(self.load_button)

        layout.addStretch()
        #init total credits count
        self.total_credits = 0

    def update_total_credits(self):
        self.total_credits_label.setText(f"Total Credits: {self.total_credits}")

    def setup_calendar(self, layout):
        # Clear existing calendar
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

        #header rows
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        for col, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label, 0, col + 1)

        #time collumns
        for row, time_label in enumerate(self.time_slots):
            label = QLabel(time_label)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label, row + 1, 0)

        #placeholders for the grid
        self.calendar_cells = {}
        for row in range(1, len(self.time_slots) + 1):
            for col in range(1, len(days) + 1):
                cell = QTextEdit()
                cell.setReadOnly(True)
                cell.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                cell.customContextMenuRequested.connect(lambda pos, r=row, c=col: self.remove_course_block(r, c))
                cell.setStyleSheet("background-color: #f0f0f0;")
                layout.addWidget(cell, row, col)
                self.calendar_cells[(row, col)] = cell  

    def add_course_to_calendar(self):
        #user input used
        course_name = self.course_name_input.text()
        credits = self.credits_input.text()
        day = self.day_input.currentText()
        time_slot = self.time_input.text()

        if not course_name or not time_slot or not credits.isdigit():
            return #error checking

        #time slot parsing
        try:
            start_time, end_time = time_slot.split("-")
            start_index = self.time_slots.index(start_time)
            end_index = self.time_slots.index(end_time)
        except ValueError:
            return #error handling

        #finding the column of the selected day
        day_to_col = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5}
        col = day_to_col.get(day, 1)

        #cell update
        for row in range(start_index + 1, end_index + 1):  #+1 because rows are 1-indexed
            cell = self.calendar_cells.get((row, col))
            if cell:
                cell.setText(f"{course_name}\nCredits: {credits}")
                cell.setStyleSheet("background-color: #b3e5fc;")

        self.total_credits += int(credits)
        self.update_total_credits()

    #function to remove the course block on the grid
    def remove_course_block(self, row, col):
        cell = self.calendar_cells.get((row, col))
        if cell and cell.toPlainText():
            course_name = cell.toPlainText().split("\n")[0]  #gets the course name
            credits = int(cell.toPlainText().split("\n")[1].replace("Credits: ", ""))
            cell.clear()
            cell.setStyleSheet("background-color: #f0f0f0;")
            print(f"Removed course: {course_name}")

            #adjusting total credits
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
        #saves to a file
        schedule_data = {
            "time_slots": self.time_slots,
            "courses": []
        }

        #first gets the courses
        for (row, col), cell in self.calendar_cells.items():
            if cell.toPlainText():
                schedule_data["courses"].append({
                    "name": cell.toPlainText(),
                    "day": self.get_day_from_col(col),
                    "start_time": self.time_slots[row - 1],  #adjusted for 0 index
                    "end_time": self.time_slots[row] if row < len(self.time_slots) else None
                })

        #output to json
        with open("schedule.json", "w") as file:
            json.dump(schedule_data, file)
        print("Schedule saved")

    def load_schedule(self):
        try:
            with open("schedule.json", "r") as file:
                schedule_data = json.load(file)

            #time slot update
            self.time_slots = schedule_data["time_slots"]
            self.update_time_slots()  #regenerate the grid

            #clears the calendar
            for cell in self.calendar_cells.values():
                cell.clear()
                cell.setStyleSheet("background-color: #f0f0f0;")

            #courses added back
            for course in schedule_data["courses"]:
                self.add_course_to_calendar_from_data(course)

            print("Schedule loaded")
        except FileNotFoundError:
            print("No saved schedule found")
        except Exception as e:
            print(f"Error loading schedule: {e}")

    #helper methods

    def get_day_from_col(self, col):
        #column index to day mappings
        col_to_day = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
        return col_to_day.get(col, "Unknown")

    def add_course_to_calendar_from_data(self, course):
        #adds course from the saved data
        day = course["day"]
        start_time = course["start_time"]
        name = course["name"]

        #find row and column
        try:
            row = self.time_slots.index(start_time) + 1  #adjusedt for 1-based indexing
            col = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5}[day]
            cell = self.calendar_cells.get((row, col))
            if cell:
                cell.setText(name)
                cell.setStyleSheet("background-color: #b3e5fc;")
        except ValueError:
            print(f"Error: Invalid time slot for course '{name}'")
