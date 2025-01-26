from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QPushButton
from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class PlanWindow(QDialog):
    def __init__(self, plan_name, schedule_data, time_slots, parent=None):
        super().__init__(parent)
        self.plan_name = plan_name
        self.schedule_data = schedule_data
        self.time_slots = time_slots
        self.setWindowTitle(f"View Plan: {plan_name}")
        self.setGeometry(200, 200, 1000, 800)

        layout = QVBoxLayout(self)

        #plan name label
        title_label = QLabel(f"Plan: {plan_name}")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        #calendar table
        self.calendar_table = QTableWidget(len(self.time_slots), 5)  # Rows = time slots, Columns = days
        self.calendar_table.setHorizontalHeaderLabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        self.calendar_table.setVerticalHeaderLabels(self.time_slots)
        self.calendar_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.calendar_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.calendar_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.calendar_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.calendar_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.calendar_table)

        #load the schedule
        self.load_schedule_data()

        # Close Button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

    def load_schedule_data(self):
        for course in self.schedule_data.get("courses", []):
            day_to_col = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
            col = day_to_col.get(course["day"], -1)

            if col == -1:
                print(f"Invalid day '{course['day']}' in plan data. Skipping course.")
                continue

            try:
                start_index = self.time_slots.index(course["start_time"])
                end_index = self.time_slots.index(course["end_time"])
                span_rows = end_index - start_index

                self.calendar_table.setSpan(start_index, col, span_rows, 1)
                course_item = QTableWidgetItem(f"{course['name']}\nCredits: {course['credits']}")
                course_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                course_item.setBackground(Qt.GlobalColor.cyan)
                course_item.setForeground(Qt.GlobalColor.black)
                self.calendar_table.setItem(start_index, col, course_item)
            except ValueError as ve:
                print(f"Error placing course '{course['name']}': {ve}")
