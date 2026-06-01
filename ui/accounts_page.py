from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QFileDialog, QMessageBox,
    QDialog, QTabWidget, QLineEdit, QSpinBox, QTextEdit, QCheckBox,
    QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from core.account_manager import AccountManager
import asyncio


class AccountCard(QFrame):
    clicked = pyqtSignal(int)

    def __init__(self, account):
        super().__init__()
        self.account_id = account["id"]
        self.setObjectName("account_card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(120)
        self._build(account)

    def _build(self, acc):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 14)
        layout.setSpacing(0)

        top = QHBoxLayout()
        top.setSpacing(12)

        letter = (acc["display_name"] or acc["login"] or "?")[0].upper()
        avatar = QLabel(letter)
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(
            "background: #F0F0F1; border-radius: 20px; "
            "font-size: 16px; font-weight: 800; color: #555555;"
        )
        top.addWidget(avatar)

        name_col = QVBoxLayout()
        name_col.setSpacing(2)
        name = QLabel(acc["display_name"] or acc["login"])
        name.setObjectName("card_name")
        name_col.addWidget(name)
        uname = QLabel(f"@{acc['tiktok_username'] or acc['login']}")
        uname.setObjectName("card_username")
        name_col.addWidget(uname)
        top.addLayout(name_col)
        top.addStretch()

        status_colors = {
            "active": "#22C55E", "inactive": "#CCCCCC",
            "failed": "#EF4444", "captcha": "#F59E0B", "verify": "#3B82F6"
        }
        dot = QLabel()
        dot.setFixedSize(9, 9)
        dot.setStyleSheet(f"background: {status_colors.get(acc['status'], '#CCCCCC')}; border-radius: 5px;")
        top.addWidget(dot)
        layout.addLayout(top)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background: #F0F0F1; border: none; max-height: 1px; margin: 10px 0 8px 0;")
        layout.addWidget(line)

        status_ru = {
            "active": "активен", "inactive": "неактивен",
            "failed": "ошибка", "captcha": "капча", "verify": "верификация"
        }
        videos = acc.get("video_count", 0) or 0
        stats = QLabel(f"{videos} видео  ·  {status_ru.get(acc['status'], acc['status'])}")
        stats.setObjectName("card_stats")
        layout.addWidget(stats)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.account_id)


class LoginWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)

    def __init__(self, db):
        super().__init__()
        self.db = db

    def run(self):
        manager = AccountManager(self.db)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(manager.login_all(self.progress.emit))
        loop.close()
        self.finished.emit(results)


class AccountDetailDialog(QDialog):
    def __init__(self, db, account_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.account_id = account_id
        self.acc = dict(db.get_account(account_id))
        self.setWindowTitle(self.acc["login"])
        self.setMinimumSize(560, 540)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        def form_tab(title):
            w = QWidget()
            f = QFormLayout(w)
            f.setSpacing(14)
            f.setContentsMargins(24, 20, 24, 20)
            f.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
            tabs.addTab(w, title)
            return f

        # Профиль
        pf = form_tab("Профиль")
        self.f_login = QLineEdit(self.acc["login"])
        self.f_password = QLineEdit(self.acc["password"])
        self.f_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.f_display_name = QLineEdit(self.acc["display_name"])
        self.f_tiktok_username = QLineEdit(self.acc["tiktok_username"])
        self.f_bio = QTextEdit(self.acc["bio"])
        self.f_bio.setFixedHeight(72)
        self.f_proxy = QLineEdit(self.acc["proxy"])
        self.f_proxy.setPlaceholderText("http://user:pass@host:port")
        pf.addRow("Логин", self.f_login)
        pf.addRow("Пароль", self.f_password)
        pf.addRow("Имя", self.f_display_name)
        pf.addRow("TikTok username", self.f_tiktok_username)
        pf.addRow("Биография", self.f_bio)
        pf.addRow("Прокси", self.f_proxy)

        # Постинг
        po = form_tab("Постинг")
        self.f_niche = QLineEdit(self.acc["niche"])
        self.f_niche.setPlaceholderText("фитнес, крипта, мемы...")
        self.f_target = QLineEdit(self.acc["target_audience"])
        self.f_target.setPlaceholderText("18-25 лет, предприниматели...")
        self.f_hashtag_count = QSpinBox()
        self.f_hashtag_count.setRange(1, 30)
        self.f_hashtag_count.setValue(self.acc["hashtag_count"])
        self.f_interval_min = QSpinBox()
        self.f_interval_min.setRange(10, 1440)
        self.f_interval_min.setValue(self.acc["post_interval_min"])
        self.f_interval_min.setSuffix(" мин")
        self.f_interval_max = QSpinBox()
        self.f_interval_max.setRange(10, 1440)
        self.f_interval_max.setValue(self.acc["post_interval_max"])
        self.f_interval_max.setSuffix(" мин")
        self.f_max_posts = QSpinBox()
        self.f_max_posts.setRange(1, 50)
        self.f_max_posts.setValue(self.acc["max_posts_per_day"])
        self.f_max_posts.setSuffix(" / день")
        po.addRow("Ниша", self.f_niche)
        po.addRow("Аудитория", self.f_target)
        po.addRow("Хэштегов", self.f_hashtag_count)
        po.addRow("Интервал мин", self.f_interval_min)
        po.addRow("Интервал макс", self.f_interval_max)
        po.addRow("Макс постов/день", self.f_max_posts)

        # Telegram
        tg = form_tab("Telegram")
        self.f_tg_token = QLineEdit(self.acc["tg_bot_token"])
        self.f_tg_token.setPlaceholderText("1234567890:AAF...")
        self.f_tg_chat = QLineEdit(self.acc["tg_chat_id"])
        self.f_tg_chat.setPlaceholderText("-100...")
        self.f_tg_success = QCheckBox("Уведомлять об успешном посте")
        self.f_tg_success.setChecked(bool(self.acc["tg_report_success"]))
        self.f_tg_fail = QCheckBox("Уведомлять об ошибке")
        self.f_tg_fail.setChecked(bool(self.acc["tg_report_fail"]))
        tg.addRow("Токен бота", self.f_tg_token)
        tg.addRow("Chat ID", self.f_tg_chat)
        tg.addRow("", self.f_tg_success)
        tg.addRow("", self.f_tg_fail)

        # AI
        ai = form_tab("AI")
        self.f_api_key = QLineEdit(self.acc["deepseek_api_key"])
        self.f_api_key.setPlaceholderText("Оставьте пустым — будет использован глобальный ключ")
        self.f_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        ai.addRow("DeepSeek API Key", self.f_api_key)

        layout.addWidget(tabs)

        # Кнопки
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(20, 12, 20, 16)
        btn_row.setSpacing(10)

        del_btn = QPushButton("Удалить аккаунт")
        del_btn.setObjectName("danger_btn")
        del_btn.clicked.connect(self._delete)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def _save(self):
        self.db.update_account(
            self.account_id,
            login=self.f_login.text(),
            password=self.f_password.text(),
            display_name=self.f_display_name.text(),
            tiktok_username=self.f_tiktok_username.text(),
            bio=self.f_bio.toPlainText(),
            proxy=self.f_proxy.text(),
            niche=self.f_niche.text(),
            target_audience=self.f_target.text(),
            hashtag_count=self.f_hashtag_count.value(),
            post_interval_min=self.f_interval_min.value(),
            post_interval_max=self.f_interval_max.value(),
            max_posts_per_day=self.f_max_posts.value(),
            tg_bot_token=self.f_tg_token.text(),
            tg_chat_id=self.f_tg_chat.text(),
            tg_report_success=int(self.f_tg_success.isChecked()),
            tg_report_fail=int(self.f_tg_fail.isChecked()),
            deepseek_api_key=self.f_api_key.text(),
        )
        self.accept()

    def _delete(self):
        reply = QMessageBox.question(
            self, "Удалить аккаунт",
            f"Удалить аккаунт {self.acc['login']}? Это действие необратимо.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_account(self.account_id)
            self.done(2)


class AccountsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(20)

        header = QHBoxLayout()
        header.setSpacing(10)
        title = QLabel("Аккаунты")
        title.setObjectName("page_title")
        header.addWidget(title)
        header.addStretch()

        import_btn = QPushButton("Импорт TXT")
        import_btn.setObjectName("secondary_btn")
        import_btn.clicked.connect(self._import_txt)
        header.addWidget(import_btn)

        login_btn = QPushButton("Войти во все")
        login_btn.setObjectName("primary_btn")
        login_btn.clicked.connect(self._login_all)
        header.addWidget(login_btn)

        layout.addLayout(header)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("status_bar")
        layout.addWidget(self.status_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.cards_widget = QWidget()
        self.cards_grid = QGridLayout(self.cards_widget)
        self.cards_grid.setSpacing(14)
        self.cards_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self.cards_widget)
        layout.addWidget(scroll)

    def refresh(self):
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        accounts = self.db.get_all_accounts()
        self.status_lbl.setText(f"{len(accounts)} аккаунтов")

        for i, acc in enumerate(accounts):
            acc_dict = dict(acc)
            acc_dict["video_count"] = len(self.db.get_videos_for_account(acc["id"]))
            card = AccountCard(acc_dict)
            card.clicked.connect(self._open_account)
            self.cards_grid.addWidget(card, i // 3, i % 3)

        if not accounts:
            empty = QLabel("Нет аккаунтов. Импортируйте из TXT файла.")
            empty.setStyleSheet("color: #CCCCCC; font-size: 15px; font-weight: 600;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cards_grid.addWidget(empty, 0, 0, 1, 3)

    def _import_txt(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Текстовые файлы (*.txt)")
        if not path: return
        manager = AccountManager(self.db)
        try:
            accounts = manager.import_from_txt(path)
            count = manager.save_imported_accounts(accounts)
            self.status_lbl.setText(f"Импортировано: {count} аккаунтов")
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _login_all(self):
        self.status_lbl.setText("Выполняю вход...")
        self.worker = LoginWorker(self.db)
        self.worker.progress.connect(lambda msg: self.status_lbl.setText(msg))
        self.worker.finished.connect(self._on_login_done)
        self.worker.start()

    def _on_login_done(self, results):
        ok = sum(1 for r in results if r["success"])
        fail = len(results) - ok
        self.status_lbl.setText(f"Готово: {ok} вошли, {fail} ошибок")
        self.refresh()

    def _open_account(self, account_id):
        dialog = AccountDetailDialog(self.db, account_id, self)
        result = dialog.exec()
        if result in (1, 2): self.refresh()
