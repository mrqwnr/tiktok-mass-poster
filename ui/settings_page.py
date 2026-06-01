from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QFormLayout, QLineEdit, QSpinBox,
    QCheckBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt

class SettingsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(20)

        title = QLabel("Settings")
        title.setObjectName("page_title")
        layout.addWidget(title)

        sub = QLabel("Global defaults — applied to all accounts unless overridden individually.")
        sub.setStyleSheet("color: #AAAAAA; font-size: 13px;")
        layout.addWidget(sub)

        layout.addSpacing(4)

        GS = "QGroupBox { font-size: 13px; font-weight: 600; color: #111111; border: 1px solid #EBEBEB; border-radius: 10px; margin-top: 10px; padding: 18px 18px 14px 18px; background: #FFFFFF; } QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; background: #FFFFFF; }"

        # AI
        ai_group = QGroupBox("AI — DeepSeek")
        ai_group.setStyleSheet(GS)
        ai_form = QFormLayout(ai_group)
        ai_form.setSpacing(14)
        self.f_deepseek_key = QLineEdit(self.db.get_setting("deepseek_api_key"))
        self.f_deepseek_key.setPlaceholderText("sk-...")
        self.f_deepseek_key.setEchoMode(QLineEdit.EchoMode.Password)
        ai_form.addRow("API Key", self.f_deepseek_key)
        layout.addWidget(ai_group)

        # Telegram
        tg_group = QGroupBox("Telegram")
        tg_group.setStyleSheet(GS)
        tg_form = QFormLayout(tg_group)
        tg_form.setSpacing(14)
        self.f_tg_token = QLineEdit(self.db.get_setting("tg_bot_token"))
        self.f_tg_token.setPlaceholderText("1234567890:AAF...")
        self.f_tg_chat = QLineEdit(self.db.get_setting("tg_chat_id"))
        self.f_tg_chat.setPlaceholderText("-100...")
        tg_form.addRow("Bot token", self.f_tg_token)
        tg_form.addRow("Chat ID", self.f_tg_chat)
        layout.addWidget(tg_group)

        # Posting
        post_group = QGroupBox("Posting defaults")
        post_group.setStyleSheet(GS)
        post_form = QFormLayout(post_group)
        post_form.setSpacing(14)

        self.f_interval_min = QSpinBox()
        self.f_interval_min.setRange(10, 1440)
        self.f_interval_min.setValue(int(self.db.get_setting("default_post_interval_min", "60")))
        self.f_interval_min.setSuffix(" min")

        self.f_interval_max = QSpinBox()
        self.f_interval_max.setRange(10, 1440)
        self.f_interval_max.setValue(int(self.db.get_setting("default_post_interval_max", "180")))
        self.f_interval_max.setSuffix(" min")

        self.f_max_posts = QSpinBox()
        self.f_max_posts.setRange(1, 50)
        self.f_max_posts.setValue(int(self.db.get_setting("default_max_posts_per_day", "5")))
        self.f_max_posts.setSuffix(" / day")

        self.f_hashtag_count = QSpinBox()
        self.f_hashtag_count.setRange(1, 30)
        self.f_hashtag_count.setValue(int(self.db.get_setting("default_hashtag_count", "10")))

        post_form.addRow("Interval min", self.f_interval_min)
        post_form.addRow("Interval max", self.f_interval_max)
        post_form.addRow("Max posts per day", self.f_max_posts)
        post_form.addRow("Hashtag count", self.f_hashtag_count)
        layout.addWidget(post_group)

        # Browser
        browser_group = QGroupBox("Browser")
        browser_group.setStyleSheet(GS)
        browser_form = QFormLayout(browser_group)
        browser_form.setSpacing(14)

        self.f_headless = QCheckBox("Headless mode (hidden browser)")
        self.f_headless.setChecked(self.db.get_setting("headless_browser", "1") == "1")

        self.f_delay_min = QSpinBox()
        self.f_delay_min.setRange(1, 60)
        self.f_delay_min.setValue(int(self.db.get_setting("random_delay_min", "2")))
        self.f_delay_min.setSuffix(" sec")

        self.f_delay_max = QSpinBox()
        self.f_delay_max.setRange(1, 120)
        self.f_delay_max.setValue(int(self.db.get_setting("random_delay_max", "8")))
        self.f_delay_max.setSuffix(" sec")

        browser_form.addRow("", self.f_headless)
        browser_form.addRow("Random delay min", self.f_delay_min)
        browser_form.addRow("Random delay max", self.f_delay_max)
        layout.addWidget(browser_group)

        # Save
        save_btn = QPushButton("Save settings")
        save_btn.setObjectName("primary_btn")
        save_btn.setFixedWidth(160)
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)
        layout.addStretch()

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _save(self):
        self.db.set_setting("deepseek_api_key", self.f_deepseek_key.text())
        self.db.set_setting("tg_bot_token", self.f_tg_token.text())
        self.db.set_setting("tg_chat_id", self.f_tg_chat.text())
        self.db.set_setting("default_post_interval_min", self.f_interval_min.value())
        self.db.set_setting("default_post_interval_max", self.f_interval_max.value())
        self.db.set_setting("default_max_posts_per_day", self.f_max_posts.value())
        self.db.set_setting("default_hashtag_count", self.f_hashtag_count.value())
        self.db.set_setting("headless_browser", "1" if self.f_headless.isChecked() else "0")
        self.db.set_setting("random_delay_min", self.f_delay_min.value())
        self.db.set_setting("random_delay_max", self.f_delay_max.value())
        QMessageBox.information(self, "Saved", "Settings saved.")
