from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QFormLayout, QLineEdit, QSpinBox,
    QCheckBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt

GS = ("QGroupBox { font-size: 14px; font-weight: 700; color: #0D0D0D; "
      "border: 1.5px solid #EBEBEB; border-radius: 12px; margin-top: 12px; "
      "padding: 20px 18px 16px 18px; background: #FFFFFF; } "
      "QGroupBox::title { subcontrol-origin: margin; left: 16px; "
      "padding: 0 6px; background: #FFFFFF; }")

class SettingsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._build()

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(20)

        title = QLabel("Настройки")
        title.setObjectName("page_title")
        lay.addWidget(title)

        sub = QLabel("Глобальные настройки — применяются ко всем аккаунтам, если не переопределены.")
        sub.setStyleSheet("color: #AAAAAA; font-size: 13px; font-weight: 500;")
        lay.addWidget(sub)
        lay.addSpacing(4)

        # AI
        ai_g = QGroupBox("AI — DeepSeek")
        ai_g.setStyleSheet(GS)
        ai_f = QFormLayout(ai_g)
        ai_f.setSpacing(14)
        self.f_key = QLineEdit(self.db.get_setting("deepseek_api_key"))
        self.f_key.setPlaceholderText("sk-...")
        self.f_key.setEchoMode(QLineEdit.EchoMode.Password)
        ai_f.addRow("API ключ", self.f_key)
        lay.addWidget(ai_g)

        # Telegram
        tg_g = QGroupBox("Telegram")
        tg_g.setStyleSheet(GS)
        tg_f = QFormLayout(tg_g)
        tg_f.setSpacing(14)
        self.f_tg_token = QLineEdit(self.db.get_setting("tg_bot_token"))
        self.f_tg_token.setPlaceholderText("1234567890:AAF...")
        self.f_tg_chat = QLineEdit(self.db.get_setting("tg_chat_id"))
        self.f_tg_chat.setPlaceholderText("-100...")
        tg_f.addRow("Токен бота", self.f_tg_token)
        tg_f.addRow("Chat ID", self.f_tg_chat)
        lay.addWidget(tg_g)

        # Постинг
        po_g = QGroupBox("Постинг по умолчанию")
        po_g.setStyleSheet(GS)
        po_f = QFormLayout(po_g)
        po_f.setSpacing(14)
        self.f_imin = QSpinBox(); self.f_imin.setRange(10,1440); self.f_imin.setValue(int(self.db.get_setting("default_post_interval_min","60"))); self.f_imin.setSuffix(" мин")
        self.f_imax = QSpinBox(); self.f_imax.setRange(10,1440); self.f_imax.setValue(int(self.db.get_setting("default_post_interval_max","180"))); self.f_imax.setSuffix(" мин")
        self.f_mpd  = QSpinBox(); self.f_mpd.setRange(1,50);    self.f_mpd.setValue(int(self.db.get_setting("default_max_posts_per_day","5"))); self.f_mpd.setSuffix(" / день")
        self.f_hc   = QSpinBox(); self.f_hc.setRange(1,30);     self.f_hc.setValue(int(self.db.get_setting("default_hashtag_count","10")))
        po_f.addRow("Интервал мин", self.f_imin)
        po_f.addRow("Интервал макс", self.f_imax)
        po_f.addRow("Макс постов/день", self.f_mpd)
        po_f.addRow("Хэштегов", self.f_hc)
        lay.addWidget(po_g)

        # Браузер
        br_g = QGroupBox("Браузер")
        br_g.setStyleSheet(GS)
        br_f = QFormLayout(br_g)
        br_f.setSpacing(14)
        self.f_headless = QCheckBox("Скрытый режим (без окна браузера)")
        self.f_headless.setChecked(self.db.get_setting("headless_browser","0")=="1")
        self.f_dmin = QSpinBox(); self.f_dmin.setRange(1,60);  self.f_dmin.setValue(int(self.db.get_setting("random_delay_min","2"))); self.f_dmin.setSuffix(" сек")
        self.f_dmax = QSpinBox(); self.f_dmax.setRange(1,120); self.f_dmax.setValue(int(self.db.get_setting("random_delay_max","8"))); self.f_dmax.setSuffix(" сек")
        br_f.addRow("", self.f_headless)
        br_f.addRow("Задержка мин", self.f_dmin)
        br_f.addRow("Задержка макс", self.f_dmax)
        lay.addWidget(br_g)

        save_btn = QPushButton("Сохранить настройки")
        save_btn.setObjectName("primary_btn")
        save_btn.setFixedWidth(200)
        save_btn.clicked.connect(self._save)
        lay.addWidget(save_btn)
        lay.addStretch()

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0,0,0,0)
        outer.addWidget(scroll)

    def _save(self):
        self.db.set_setting("deepseek_api_key", self.f_key.text())
        self.db.set_setting("tg_bot_token", self.f_tg_token.text())
        self.db.set_setting("tg_chat_id", self.f_tg_chat.text())
        self.db.set_setting("default_post_interval_min", self.f_imin.value())
        self.db.set_setting("default_post_interval_max", self.f_imax.value())
        self.db.set_setting("default_max_posts_per_day", self.f_mpd.value())
        self.db.set_setting("default_hashtag_count", self.f_hc.value())
        self.db.set_setting("headless_browser", "1" if self.f_headless.isChecked() else "0")
        self.db.set_setting("random_delay_min", self.f_dmin.value())
        self.db.set_setting("random_delay_max", self.f_dmax.value())
        QMessageBox.information(self, "Сохранено", "Настройки сохранены.")
