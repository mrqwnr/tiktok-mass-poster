MAIN_STYLE = """
* {
    font-family: 'DM Sans', 'Segoe UI', sans-serif;
    box-sizing: border-box;
}

QMainWindow, QWidget {
    background-color: #F5F5F7;
    color: #0D0D0D;
    font-size: 14px;
}

/* ── Сайдбар ── */
QFrame#sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E8E8E8;
}

QLabel#logo {
    font-size: 20px;
    font-weight: 800;
    color: #0D0D0D;
    letter-spacing: -0.5px;
}

QPushButton#nav_btn {
    background: transparent;
    border: none;
    padding: 11px 18px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
    color: #AAAAAA;
    border-radius: 10px;
    margin: 2px 10px;
}
QPushButton#nav_btn:hover {
    background-color: #F5F5F7;
    color: #0D0D0D;
}
QPushButton#nav_btn:checked {
    background-color: #0D0D0D;
    color: #FFFFFF;
}

/* ── Кнопки ── */
QPushButton#primary_btn {
    background-color: #0D0D0D;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 11px 22px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: -0.2px;
}
QPushButton#primary_btn:hover { background-color: #2a2a2a; }
QPushButton#primary_btn:disabled { background-color: #CCCCCC; color: #888; }

QPushButton#secondary_btn {
    background-color: #FFFFFF;
    color: #0D0D0D;
    border: 1.5px solid #E0E0E0;
    border-radius: 10px;
    padding: 11px 22px;
    font-size: 14px;
    font-weight: 600;
}
QPushButton#secondary_btn:hover { background-color: #F5F5F7; }

QPushButton#danger_btn {
    background-color: #FFF0F0;
    color: #D32F2F;
    border: 1.5px solid #FFCDD2;
    border-radius: 10px;
    padding: 11px 22px;
    font-size: 14px;
    font-weight: 600;
}
QPushButton#danger_btn:hover { background-color: #FFE0E0; }

QPushButton#success_btn {
    background-color: #E8F5E9;
    color: #2E7D32;
    border: 1.5px solid #C8E6C9;
    border-radius: 10px;
    padding: 11px 22px;
    font-size: 14px;
    font-weight: 600;
}
QPushButton#success_btn:hover { background-color: #DCEDC8; }

/* ── Карточки ── */
QFrame#card {
    background-color: #FFFFFF;
    border-radius: 14px;
    border: 1.5px solid #EBEBEB;
}
QFrame#account_card {
    background-color: #FFFFFF;
    border-radius: 14px;
    border: 1.5px solid #EBEBEB;
}
QFrame#account_card:hover { border: 1.5px solid #BBBBBB; }

/* ── Типографика ── */
QLabel#page_title {
    font-size: 28px;
    font-weight: 800;
    color: #0D0D0D;
    letter-spacing: -0.8px;
}
QLabel#section_title {
    font-size: 16px;
    font-weight: 700;
    color: #0D0D0D;
    letter-spacing: -0.3px;
}
QLabel#stat_value {
    font-size: 32px;
    font-weight: 800;
    color: #0D0D0D;
    letter-spacing: -1px;
}
QLabel#stat_label {
    font-size: 12px;
    font-weight: 500;
    color: #AAAAAA;
    letter-spacing: 0.2px;
}
QLabel#card_name {
    font-size: 15px;
    font-weight: 700;
    color: #0D0D0D;
}
QLabel#card_username {
    font-size: 12px;
    font-weight: 400;
    color: #BBBBBB;
}
QLabel#card_stats {
    font-size: 12px;
    font-weight: 500;
    color: #BBBBBB;
}
QLabel#status_bar {
    font-size: 13px;
    font-weight: 500;
    color: #AAAAAA;
}

/* ── Инпуты ── */
QLineEdit, QTextEdit, QSpinBox, QComboBox {
    background-color: #FFFFFF;
    border: 1.5px solid #E5E5E5;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 14px;
    font-weight: 500;
    color: #0D0D0D;
}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
    border: 1.5px solid #0D0D0D;
}
QSpinBox::up-button, QSpinBox::down-button { width: 20px; }

/* ── Скролл ── */
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical {
    width: 5px; background: transparent;
}
QScrollBar::handle:vertical {
    background: #DDDDDD; border-radius: 3px; min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Табы ── */
QTabWidget::pane { border: none; background: transparent; }
QTabBar::tab {
    padding: 10px 20px; border: none;
    color: #AAAAAA; font-size: 14px; font-weight: 600;
    background: transparent;
}
QTabBar::tab:selected {
    color: #0D0D0D;
    border-bottom: 2.5px solid #0D0D0D;
}
QTabBar::tab:hover { color: #444444; }

/* ── GroupBox ── */
QGroupBox {
    font-size: 14px; font-weight: 700; color: #0D0D0D;
    border: 1.5px solid #EBEBEB; border-radius: 12px;
    margin-top: 12px; padding: 20px 18px 16px 18px;
    background: #FFFFFF;
}
QGroupBox::title {
    subcontrol-origin: margin; left: 16px;
    padding: 0 6px; background: #FFFFFF;
}

/* ── Чекбокс ── */
QCheckBox { font-size: 14px; font-weight: 500; color: #333; spacing: 10px; }
QCheckBox::indicator {
    width: 18px; height: 18px; border-radius: 5px;
    border: 1.5px solid #CCCCCC; background: #FFFFFF;
}
QCheckBox::indicator:checked {
    background: #0D0D0D; border: 1.5px solid #0D0D0D;
}

/* ── Диалог ── */
QDialog { background-color: #F5F5F7; }
QMessageBox { background-color: #FFFFFF; font-size: 14px; }

/* ── Прогресс ── */
QProgressBar {
    border: none; border-radius: 6px;
    background: #F0F0F0; height: 8px; text-align: center;
    font-size: 11px; color: transparent;
}
QProgressBar::chunk {
    background: #0D0D0D; border-radius: 6px;
}

/* ── Список ── */
QListWidget {
    background: #FFFFFF; border: 1.5px solid #EBEBEB;
    border-radius: 12px; padding: 6px; font-size: 13px;
    font-weight: 500;
}
QListWidget::item {
    padding: 8px 12px; border-radius: 8px; color: #0D0D0D;
}
QListWidget::item:selected {
    background: #F0F0F0; color: #0D0D0D;
}
QListWidget::item:hover { background: #F8F8F8; }
"""
