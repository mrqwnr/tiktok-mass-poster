from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFrame, QLabel, QStackedWidget, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase
from ui.dashboard import DashboardPage
from ui.accounts_page import AccountsPage
from ui.settings_page import SettingsPage
from ui.styles import MAIN_STYLE
import os

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("TikTok Mass Poster")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        # Load DM Sans font if available
        font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "DMSans.ttf")
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)

        self.setStyleSheet(MAIN_STYLE)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 28, 0, 24)
        sidebar_layout.setSpacing(2)

        # Logo
        logo = QLabel("Mass Poster")
        logo.setObjectName("logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        logo.setContentsMargins(20, 0, 0, 0)
        sidebar_layout.addWidget(logo)

        sidebar_layout.addSpacing(24)

        # Nav
        self.nav_buttons = []
        nav_items = [
            ("Dashboard", 0),
            ("Accounts", 1),
            ("Settings", 2),
        ]
        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("nav_btn")
            btn.setCheckable(True)
            btn.setFixedHeight(38)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        ver = QLabel("v0.1.0")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet("color: #CCCCCC; font-size: 11px;")
        sidebar_layout.addWidget(ver)

        layout.addWidget(sidebar)

        # Pages
        self.stack = QStackedWidget()
        self.dashboard = DashboardPage(self.db)
        self.accounts_page = AccountsPage(self.db)
        self.settings_page = SettingsPage(self.db)

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.accounts_page)
        self.stack.addWidget(self.settings_page)

        layout.addWidget(self.stack)
        self._switch_page(0)

    def _switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        if index == 0:
            self.dashboard.refresh()
        elif index == 1:
            self.accounts_page.refresh()
