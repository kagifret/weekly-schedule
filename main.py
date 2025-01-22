import sys
from PyQt6.QtWidgets import QApplication
from gui.calendar_view import CalendarView

def main():
    app = QApplication(sys.argv)
    window = CalendarView()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()