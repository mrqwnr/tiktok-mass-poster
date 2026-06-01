from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFrame, QLabel, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase
from ui.dashboard import DashboardPage
from ui.accounts_page import AccountsPage
from ui.settings_page import SettingsPage
from ui.posting_page import PostingPage
from ui.styles import MAIN_STYLE
import os

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("TikTok Mass Poster")
        self.setMinimumSize(1100, 700)
        self.resize(1300, 820)

        font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "DMSans.ttf")
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)

        self.setStyleSheet(MAIN_STYLE)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Сайдбар
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(0, 32, 0, 28)
        sb.setSpacing(2)

        logo = QLabel("Mass Poster")
        logo.setObjectName("logo")
        logo.setContentsMargins(22, 0, 0, 0)
        sb.addWidget(logo)
        sb.addSpacing(28)

        self.nav_buttons = []
        nav_items = [
            ("Главная",    0),
            ("Аккаунты",   1),
            ("Постинг",    2),
            ("Настройки",  3),
        ]
        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("nav_btn")
            btn.setCheckable(True)
            btn.setFixedHeight(42)
            btn.clicked.connect(lambda _, i=idx: self._switch(i))
            sb.addWidget(btn)
            self.nav_buttons.append(btn)

        sb.addStretch()
        ver = QLabel("v0.1.0")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet("color: #CCCCCC; font-size: 11px; font-weight: 500;")
        sb.addWidget(ver)

        root.addWidget(sidebar)

        # Страницы
        self.stack = QStackedWidget()
        self.dashboard   = DashboardPage(self.db)
        self.accounts_pg = AccountsPage(self.db)
        self.posting_pg  = PostingPage(self.db)
        self.settings_pg = SettingsPage(self.db)

        for pg in [self.dashboard, self.accounts_pg, self.posting_pg, self.settings_pg]:
            self.stack.addWidget(pg)

        root.addWidget(self.stack)
        self._switch(0)

    def _switch(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        if index == 0: self.dashboard.refresh()
        if index == 1: self.accounts_pg.refresh()
        if index == 2: self.posting_pg.refresh()
