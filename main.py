import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from db.database import Database

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TikTok Mass Poster")
    app.setStyle("Fusion")

    db = Database()
    db.init()

    window = MainWindow(db)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
