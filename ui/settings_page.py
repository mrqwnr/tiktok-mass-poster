from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QFormLayout, QLineEdit, QSpinBox,
    QCheckBox, QComboBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

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
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(24)

        title = QLabel("Глобальные настройки")
        title.setObjectName("title")
        layout.addWidget(title)

        sub = QLabel("Настройки применяются ко всем аккаунтам, если не переопределены индивидуально")
        sub.setObjectName("subtitle")
        layout.addWidget(sub)

        # --- AI Settings ---
        ai_group = QGroupBox("🤖 DeepSeek AI")
        ai_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; border: 1px solid #eee; border-radius: 10px; margin-top: 8px; padding: 16px; } QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; }")
        ai_form = QFormLayout(ai_group)
        ai_form.setSpacing(12)

        self.f_deepseek_key = QLineEdit(self.db.get_setting("deepseek_api_key"))
        self.f_deepseek_key.setPlaceholderText("sk-...")
        self.f_deepseek_key.setEchoMode(QLineEdit.EchoMode.Password)
        ai_form.addRow("API Key (глобальный):", self.f_deepseek_key)
        layout.addWidget(ai_group)

        # --- Telegram Settings ---
        tg_group = QGroupBox("📱 Telegram (глобальный)")
        tg_group.setStyleSheet(ai_group.styleSheet())
        tg_form = QFormLayout(tg_group)
        tg_form.setSpacing(12)

        self.f_tg_token = QLineEdit(self.db.get_setting("tg_bot_token"))
        self.f_tg_token.setPlaceholderText("1234567890:AAF...")
        self.f_tg_chat = QLineEdit(self.db.get_setting("tg_chat_id"))
        self.f_tg_chat.setPlaceholderText("-100...")
        tg_form.addRow("Токен бота:", self.f_tg_token)
        tg_form.addRow("Chat ID:", self.f_tg_chat)
        layout.addWidget(tg_group)

        # --- Posting Defaults ---
        post_group = QGroupBox("🎬 Постинг (по умолчанию)")
        post_group.setStyleSheet(ai_group.styleSheet())
        post_form = QFormLayout(post_group)
        post_form.setSpacing(12)

        self.f_interval_min = QSpinBox()
        self.f_interval_min.setRange(10, 1440)
        self.f_interval_min.setValue(int(self.db.get_setting("default_post_interval_min", "60")))
        self.f_interval_min.setSuffix(" мин")

        self.f_interval_max = QSpinBox()
        self.f_interval_max.setRange(10, 1440)
        self.f_interval_max.setValue(int(self.db.get_setting("default_post_interval_max", "180")))
        self.f_interval_max.setSuffix(" мин")

        self.f_max_posts = QSpinBox()
        self.f_max_posts.setRange(1, 50)
        self.f_max_posts.setValue(int(self.db.get_setting("default_max_posts_per_day", "5")))
        self.f_max_posts.setSuffix(" в день")

        self.f_hashtag_count = QSpinBox()
        self.f_hashtag_count.setRange(1, 30)
        self.f_hashtag_count.setValue(int(self.db.get_setting("default_hashtag_count", "10")))

        post_form.addRow("Интервал мин:", self.f_interval_min)
        post_form.addRow("Интервал макс:", self.f_interval_max)
        post_form.addRow("Макс постов в день:", self.f_max_posts)
        post_form.addRow("Кол-во хэштегов:", self.f_hashtag_count)
        layout.addWidget(post_group)

        # --- Browser Settings ---
        browser_group = QGroupBox("🌐 Браузер")
        browser_group.setStyleSheet(ai_group.styleSheet())
        browser_form = QFormLayout(browser_group)
        browser_form.setSpacing(12)

        self.f_headless = QCheckBox("Скрытый режим (headless)")
        self.f_headless.setChecked(self.db.get_setting("headless_browser", "1") == "1")

        self.f_delay_min = QSpinBox()
        self.f_delay_min.setRange(1, 60)
        self.f_delay_min.setValue(int(self.db.get_setting("random_delay_min", "2")))
        self.f_delay_min.setSuffix(" сек")

        self.f_delay_max = QSpinBox()
        self.f_delay_max.setRange(1, 120)
        self.f_delay_max.setValue(int(self.db.get_setting("random_delay_max", "8")))
        self.f_delay_max.setSuffix(" сек")

        browser_form.addRow("", self.f_headless)
        browser_form.addRow("Задержка мин:", self.f_delay_min)
        browser_form.addRow("Задержка макс:", self.f_delay_max)
        layout.addWidget(browser_group)

        # Save button
        save_btn = QPushButton("💾 Сохранить настройки")
        save_btn.setObjectName("primary_btn")
        save_btn.setFixedWidth(220)
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
        QMessageBox.information(self, "Сохранено", "Настройки сохранены!")
