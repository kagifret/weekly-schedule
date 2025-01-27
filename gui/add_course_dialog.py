from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QHBoxLayout, QPushButton, QMessageBox, QColorDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class AddCourseDialog(QDialog):
    def __init__(self, time_slots, parent=None):
        super().__init__(parent)
        self.time_slots = time_slots
        self.setWindowTitle("Add New Course")
        self.setModal(True)
        self.resize(300, 250)

        layout = QVBoxLayout()

        #input fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Course Name")
        layout.addWidget(QLabel("Course Name:"))
        layout.addWidget(self.name_input)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Course Code")
        layout.addWidget(QLabel("Course Code:"))
        layout.addWidget(self.code_input)

        self.credits_input = QLineEdit()
        self.credits_input.setPlaceholderText("Credits")
        layout.addWidget(QLabel("Credits:"))
        layout.addWidget(self.credits_input)

        self.day_input = QComboBox()
        self.day_input.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        layout.addWidget(QLabel("Day:"))
        layout.addWidget(self.day_input)

        time_layout = QHBoxLayout()
        self.start_time_input = QComboBox()
        self.start_time_input.setEditable(True)
        self.start_time_input.addItems(self.time_slots)
        self.start_time_input.setPlaceholderText("Start Time")

        self.end_time_input = QComboBox()
        self.end_time_input.setEditable(True)
        self.end_time_input.addItems(self.time_slots)
        self.end_time_input.setPlaceholderText("End Time")

        time_layout.addWidget(QLabel("Start Time:"))
        time_layout.addWidget(self.start_time_input)
        time_layout.addWidget(QLabel("-"))
        time_layout.addWidget(self.end_time_input)

        layout.addWidget(QLabel("Time slot duration:"))
        layout.addLayout(time_layout)

        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.select_color)
        self.selected_color = "#00aa00"
        layout.addWidget(QLabel("Block Color:"))
        layout.addWidget(self.color_button)

        #buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.accept_course)
        button_layout.addWidget(self.add_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def accept_course(self):
        course_name = self.name_input.text().strip()
        course_code = self.code_input.text().strip()
        credits = self.credits_input.text().strip()
        start_time = self.start_time_input.currentText().strip()
        end_time = self.end_time_input.currentText().strip()

        if not course_name or not course_code or not credits or not start_time or not end_time:
            QMessageBox.warning(self, "Invalid input", "All fields must be filled out")
            return

        if not credits.isdigit():
            QMessageBox.warning(self, "Invalid credits", "Credits must be a number")
            return

        if start_time not in self.time_slots or end_time not in self.time_slots:
            QMessageBox.warning(self, "Invalid time slot", "Start time or end time is not valid")
            return

        if self.time_slots.index(start_time) >= self.time_slots.index(end_time):
            QMessageBox.warning(self, "Invalid time slot", "Start time must be earlier than end time")
            return

        self.accept()

    def get_course_details(self):
        return {
            "name": self.name_input.text().strip(),
            "code": self.code_input.text().strip(),
            "credits": int(self.credits_input.text().strip()),
            "day": self.day_input.currentText(),
            "start_time": self.start_time_input.currentText().strip(),
            "end_time": self.end_time_input.currentText().strip(),
            "color": self.selected_color
        }
    
    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
            self.color_button.setStyleSheet(f"background-color: {self.selected_color};")
            print(f"Selected color: {self.selected_color}")
