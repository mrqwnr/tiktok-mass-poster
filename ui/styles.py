# DM Sans font setup
DM_SANS_SETUP = """
QApplication {
    font-family: 'DM Sans';
}
"""

MAIN_STYLE = """
* {
    font-family: 'DM Sans', 'Segoe UI', sans-serif;
}

QMainWindow, QWidget {
    background-color: #F7F7F8;
    color: #111111;
    font-size: 14px;
}

/* Sidebar */
QFrame#sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #EBEBEB;
}

QLabel#logo {
    font-size: 17px;
    font-weight: 700;
    color: #111111;
    letter-spacing: -0.3px;
}

QPushButton#nav_btn {
    background: transparent;
    border: none;
    padding: 10px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
    color: #888888;
    border-radius: 8px;
    margin: 1px 10px;
}
QPushButton#nav_btn:hover {
    background-color: #F3F3F4;
    color: #111111;
}
QPushButton#nav_btn:checked {
    background-color: #F0F0F1;
    color: #111111;
    font-weight: 600;
}

/* Buttons */
QPushButton#primary_btn {
    background-color: #111111;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#primary_btn:hover {
    background-color: #2a2a2a;
}
QPushButton#primary_btn:disabled {
    background-color: #CCCCCC;
    color: #888888;
}

QPushButton#secondary_btn {
    background-color: #FFFFFF;
    color: #111111;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 9px 18px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton#secondary_btn:hover {
    background-color: #F7F7F8;
}

QPushButton#danger_btn {
    background-color: #FFFFFF;
    color: #E53935;
    border: 1px solid #FFCDD2;
    border-radius: 8px;
    padding: 9px 18px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton#danger_btn:hover {
    background-color: #FFF5F5;
}

/* Cards */
QFrame#card {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #EBEBEB;
}

QFrame#account_card {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #EBEBEB;
}
QFrame#account_card:hover {
    border: 1px solid #CCCCCC;
}

/* Typography */
QLabel#page_title {
    font-size: 22px;
    font-weight: 700;
    color: #111111;
    letter-spacing: -0.4px;
}
QLabel#section_title {
    font-size: 15px;
    font-weight: 600;
    color: #111111;
}
QLabel#stat_value {
    font-size: 26px;
    font-weight: 700;
    color: #111111;
    letter-spacing: -0.5px;
}
QLabel#stat_label {
    font-size: 12px;
    font-weight: 400;
    color: #999999;
}
QLabel#card_name {
    font-size: 14px;
    font-weight: 600;
    color: #111111;
}
QLabel#card_username {
    font-size: 12px;
    font-weight: 400;
    color: #AAAAAA;
}
QLabel#card_stats {
    font-size: 12px;
    color: #AAAAAA;
}
QLabel#status_bar {
    font-size: 12px;
    color: #AAAAAA;
}

/* Inputs */
QLineEdit, QTextEdit, QSpinBox, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: #111111;
    selection-background-color: #E8E8E8;
}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
    border: 1px solid #AAAAAA;
    outline: none;
}
QLineEdit::placeholder {
    color: #CCCCCC;
}

/* Scroll */
QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    width: 5px;
    background: transparent;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #E0E0E0;
    border-radius: 2px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* Tabs */
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    padding: 9px 18px;
    border: none;
    color: #AAAAAA;
    font-size: 13px;
    font-weight: 500;
    background: transparent;
}
QTabBar::tab:selected {
    color: #111111;
    font-weight: 600;
    border-bottom: 2px solid #111111;
}
QTabBar::tab:hover {
    color: #333333;
}

/* GroupBox */
QGroupBox {
    font-size: 13px;
    font-weight: 600;
    color: #111111;
    border: 1px solid #EBEBEB;
    border-radius: 10px;
    margin-top: 10px;
    padding: 16px 16px 12px 16px;
    background: #FFFFFF;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    background: #FFFFFF;
}

/* Checkbox */
QCheckBox {
    font-size: 13px;
    color: #333333;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1.5px solid #CCCCCC;
    background: #FFFFFF;
}
QCheckBox::indicator:checked {
    background: #111111;
    border: 1.5px solid #111111;
}

/* Dialog */
QDialog {
    background-color: #F7F7F8;
}

/* MessageBox */
QMessageBox {
    background-color: #FFFFFF;
    font-size: 13px;
}
"""
