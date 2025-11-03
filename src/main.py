from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
import sys

def main():
    print("Starting application...")
    app = QApplication(sys.argv)
    print("Created QApplication")
    window = MainWindow()
    print("Created MainWindow")
    window.show()
    print("Called show()")
    sys.exit(app.exec())

if __name__ == "__main__":
    print("Running main()")
    main()