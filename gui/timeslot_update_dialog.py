from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QPushButton, QMessageBox


class TimeSlotUpdateDialog(QDialog):
    def __init__(self, current_time_slots, full_time_range, parent=None):
        super().__init__(parent)
        self.current_time_slots = current_time_slots
        self.full_time_range = full_time_range
        self.setWindowTitle("Update Time Slots")
        self.setModal(True)
        self.resize(300, 150)

        layout = QVBoxLayout()

        # Start and End Time
        time_layout = QHBoxLayout()
        self.start_time_input = QComboBox()
        self.start_time_input.setEditable(True)
        self.start_time_input.addItems(self.full_time_range)
        self.start_time_input.setPlaceholderText("Start time")

        self.end_time_input = QComboBox()
        self.end_time_input.setEditable(True)
        self.end_time_input.addItems(self.full_time_range)
        self.end_time_input.setPlaceholderText("End time")

        time_layout.addWidget(QLabel("Start time:"))
        time_layout.addWidget(self.start_time_input)
        time_layout.addWidget(QLabel("-"))
        time_layout.addWidget(self.end_time_input)

        layout.addWidget(QLabel("Update Time Slots:"))
        layout.addLayout(time_layout)

        # Action buttons
        button_layout = QHBoxLayout()
        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(self.update_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_time_slot_range(self):
        return self.start_time_input.currentText().strip(), self.end_time_input.currentText().strip()

    def validate_and_accept(self):
        start_time, end_time = self.get_time_slot_range()

        if start_time not in self.full_time_range or end_time not in self.full_time_range:
            QMessageBox.warning(self, "Invalid time slots", "Start time or end time is not valid")
            return

        if self.full_time_range.index(start_time) >= self.full_time_range.index(end_time):
            QMessageBox.warning(self, "Invalid time range", "Start time must be earlier than end time")
            return

        self.accept()