from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton,
    QLineEdit, QComboBox, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QColorDialog
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
        #user input used
        course_name = self.course_name_input.text()
        course_code = self.course_code_input.text()
        credits = self.credits_input.text()
        day = self.day_input.currentText()
        time_slot = self.time_input.text()

        #if not course_name or not time_slot or not credits.isdigit():
        if not course_name or not course_code or not time_slot or not credits.isdigit():
            return #error checking

        #time slot parsing
        try:
            start_time, end_time = time_slot.split("-")
            start_index = self.time_slots.index(start_time)
            end_index = self.time_slots.index(end_time)
        except ValueError:
            return #error handling

        #finding the column of the selected day
        day_to_col = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
        col = day_to_col.get(day, 0)

        #check for conflicts
        for row in range(start_index, end_index):
            if self.calendar_table.item(row, col) is not None:
                print(f"Cell conflict for {course_name} at {day}, {start_time}-{end_time}.")
                return

        #adds the course
        span_rows = end_index - start_index
        self.calendar_table.setSpan(start_index, col, span_rows, 1)
        course_item = QTableWidgetItem(f"{course_name}\nCredits: {credits}")
        course_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        course_item.setBackground(Qt.GlobalColor.cyan) #background color
        course_item.setForeground(Qt.GlobalColor.black) #text color
        self.calendar_table.setItem(start_index, col, course_item)

        #updates the sum of credits if the course is new
        if course_code not in self.course_codes:
            self.course_codes.add(course_code)
            self.total_credits += int(credits)
            self.update_total_credits()

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
        #saves to a file
        schedule_data = {
            "time_slots": self.time_slots,
            "courses": []
        }

        #gets the courses
        for row in range(self.calendar_table.rowCount()):
            for col in range(self.calendar_table.columnCount()):
                item = self.calendar_table.item(row, col)
                if item and self.calendar_table.columnSpan(row, col) == 1:
                    course_data = item.text().split("\n")
                    course_name = course_data[0]
                    credits = int(course_data[1].replace("Credits: ", ""))
                    start_time = self.time_slots[row]
                    end_time = self.time_slots[row + self.calendar_table.rowSpan(row, col)]

                    schedule_data["courses"].append({
                        "name": course_name,
                        "credits": credits,
                        "start_time": start_time,
                        "end_time": end_time,
                        "day": self.get_day_from_col(col)
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
            self.calendar_table.clearContents()
            self.calendar_table.clearSpans()

            #courses added back
            for course in schedule_data["courses"]:
                self.load_course_to_calendar(course)

            print("Schedule loaded")
        except FileNotFoundError:
            print("No saved schedule found")
        except Exception as e:
            print(f"Error loading schedule: {e}")

    #helper methods

    def get_day_from_col(self, col):
        #column index to day mappings
        col_to_day = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday"}
        return col_to_day.get(col, "Unknown")

    def load_course_to_calendar(self, course):
        day_to_col = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
        col = day_to_col[course["day"]]

        try:
            start_index = self.time_slots.index(course["start_time"])
            end_index = self.time_slots.index(course["end_time"])
            span_rows = end_index - start_index

            # Add the course to the calendar
            self.calendar_table.setSpan(start_index, col, span_rows, 1)
            course_item = QTableWidgetItem(f"{course['name']}\nCredits: {course['credits']}")
            course_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            course_item.setBackground(Qt.GlobalColor.cyan)
            course_item.setForeground(Qt.GlobalColor.black)
            self.calendar_table.setItem(start_index, col, course_item)

            # Update total credits
            if course["name"] not in self.course_codes:
                self.course_codes.add(course["name"])
                self.total_credits += course["credits"]
                self.update_total_credits()
        except ValueError:
            print(f"Error: Invalid time slot:'{course['name']}'")

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