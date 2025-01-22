from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton,
    QLineEdit, QComboBox, QGridLayout, QTextEdit
)
from PyQt6.QtCore import Qt

class CalendarView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weekly Scheduler")
        self.setGeometry(100, 100, 1200, 800)

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

        #button
        self.add_course_button = QPushButton("Add Course")
        self.add_course_button.clicked.connect(self.add_course_to_calendar)

        #added to layout
        layout.addWidget(QLabel("Add Course:"))
        layout.addWidget(self.course_name_input)
        layout.addWidget(self.course_code_input)
        layout.addWidget(self.credits_input)
        layout.addWidget(self.day_input)
        layout.addWidget(self.time_input)
        layout.addWidget(self.add_course_button)

        layout.addStretch()

    def setup_calendar(self, layout):
        #header rows
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        for col, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label, 0, col + 1)

        #columns for time
        for row, time in enumerate(range(8, 18)):
            label = QLabel(f"{time}:00 - {time + 1}:00")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label, row + 1, 0)

        # grid cells
        self.calendar_cells = {}
        for row in range(1, 11):
            for col in range(1, 6):
                cell = QTextEdit()
                cell.setReadOnly(True)
                cell.setStyleSheet("background-color: #f0f0f0;")
                layout.addWidget(cell, row, col)
                self.calendar_cells[(row, col)] = cell

    def add_course_to_calendar(self):
        #user input used
        course_name = self.course_name_input.text()
        day = self.day_input.currentText()
        time_slot = self.time_input.text()

        if not course_name or not time_slot:
            return #WIP

        #time slot parsing
        start_hour = int(time_slot.split(":")[0])
        row = start_hour - 8 + 1  # Map 8 AM to row 1

        #finding the column of the selected day
        day_to_col = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5}
        col = day_to_col.get(day, 1)

        #cell update
        cell = self.calendar_cells.get((row, col))
        if cell:
            cell.setText(course_name)
            cell.setStyleSheet("background-color: #b3e5fc;")
