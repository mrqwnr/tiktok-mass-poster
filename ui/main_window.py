from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFrame, QLabel, QStackedWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from ui.dashboard import DashboardPage
from ui.accounts_page import AccountsPage
from ui.settings_page import SettingsPage
from ui.styles import MAIN_STYLE

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("TikTok Mass Poster")
        self.setMinimumSize(1200, 750)
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
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(4)

        # Logo
        logo = QLabel("🎵 TikPoster")
        logo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("color: #fe2c55; padding: 10px 0 20px 0;")
        sidebar_layout.addWidget(logo)

        # Nav buttons
        self.nav_buttons = []
        nav_items = [
            ("🏠  Главная", 0),
            ("👤  Аккаунты", 1),
            ("⚙️  Настройки", 2),
        ]
        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("nav_btn")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # Version
        ver = QLabel("v0.1.0")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet("color: #ccc; font-size: 11px;")
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

        # Default page
        self._switch_page(0)

    def _switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        if index == 0:
            self.dashboard.refresh()
        elif index == 1:
            self.accounts_page.refresh()
