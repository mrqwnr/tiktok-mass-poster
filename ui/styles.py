MAIN_STYLE = """
QMainWindow, QWidget {
    background-color: #f8f9fa;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: #1a1a2e;
}

QFrame#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e8e8e8;
}

QPushButton#nav_btn {
    background: transparent;
    border: none;
    padding: 12px 20px;
    text-align: left;
    font-size: 14px;
    color: #555;
    border-radius: 8px;
    margin: 2px 8px;
}
QPushButton#nav_btn:hover {
    background-color: #f0f0f0;
    color: #1a1a2e;
}
QPushButton#nav_btn:checked {
    background-color: #f0f0f0;
    color: #fe2c55;
    font-weight: bold;
}

QPushButton#primary_btn {
    background-color: #fe2c55;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton#primary_btn:hover {
    background-color: #e0254a;
}
QPushButton#primary_btn:disabled {
    background-color: #ccc;
}

QPushButton#secondary_btn {
    background-color: #ffffff;
    color: #1a1a2e;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
}
QPushButton#secondary_btn:hover {
    background-color: #f5f5f5;
}

QFrame#card {
    background-color: #ffffff;
    border-radius: 12px;
    border: 1px solid #eeeeee;
}

QLabel#title {
    font-size: 22px;
    font-weight: bold;
    color: #1a1a2e;
}
QLabel#subtitle {
    font-size: 13px;
    color: #888;
}
QLabel#stat_value {
    font-size: 28px;
    font-weight: bold;
    color: #1a1a2e;
}
QLabel#stat_label {
    font-size: 12px;
    color: #aaa;
}

QLineEdit, QTextEdit, QComboBox, QSpinBox {
    background-color: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: #1a1a2e;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #fe2c55;
    background-color: #fff;
}

QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    width: 6px;
    background: transparent;
}
QScrollBar::handle:vertical {
    background: #ddd;
    border-radius: 3px;
}

QTabWidget::pane {
    border: none;
}
QTabBar::tab {
    padding: 8px 16px;
    border: none;
    color: #888;
    font-size: 13px;
}
QTabBar::tab:selected {
    color: #fe2c55;
    border-bottom: 2px solid #fe2c55;
    font-weight: bold;
}
"""
