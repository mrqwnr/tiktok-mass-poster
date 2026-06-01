from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QFileDialog, QMessageBox,
    QDialog, QTabWidget, QLineEdit, QSpinBox, QTextEdit, QCheckBox, QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from core.account_manager import AccountManager
import asyncio

class AccountCard(QFrame):
    clicked = pyqtSignal(int)

    def __init__(self, account):
        super().__init__()
        self.account_id = account["id"]
        self.setObjectName("card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(130)
        self._build(account)

    def _build(self, acc):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 10)
        layout.setSpacing(4)

        top = QHBoxLayout()

        # Avatar placeholder
        avatar = QLabel("👤")
        avatar.setFont(QFont("Segoe UI", 24))
        avatar.setFixedSize(44, 44)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("background:#f0f0f0; border-radius:22px;")
        top.addWidget(avatar)

        info = QVBoxLayout()
        info.setSpacing(2)
        name = QLabel(acc["display_name"] or acc["login"])
        name.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        info.addWidget(name)

        username = QLabel(f"@{acc['tiktok_username'] or acc['login']}")
        username.setStyleSheet("color: #aaa; font-size: 11px;")
        info.addWidget(username)
        top.addLayout(info)
        top.addStretch()

        # Status dot
        status_color = {"active": "#22c55e", "inactive": "#aaa", "failed": "#ef4444", "captcha": "#f59e0b"}.get(acc["status"], "#aaa")
        status = QLabel("●")
        status.setStyleSheet(f"color: {status_color}; font-size: 16px;")
        top.addWidget(status)

        layout.addLayout(top)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #f0f0f0;")
        layout.addWidget(line)

        # Stats
        stats = QLabel(f"Видео: {acc.get('video_count', 0) or 0}  |  Статус: {acc['status']}")
        stats.setStyleSheet("color: #999; font-size: 11px;")
        layout.addWidget(stats)

    def mousePressEvent(self, event):
        self.clicked.emit(self.account_id)


class LoginWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)

    def __init__(self, db, account_ids=None):
        super().__init__()
        self.db = db
        self.account_ids = account_ids

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
        self.setWindowTitle(f"Аккаунт: {self.acc['login']}")
        self.setMinimumSize(600, 500)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # Tab 1: Profile
        profile_tab = QWidget()
        form = QFormLayout(profile_tab)
        form.setSpacing(12)
        form.setContentsMargins(20, 20, 20, 20)

        self.f_login = QLineEdit(self.acc["login"])
        self.f_password = QLineEdit(self.acc["password"])
        self.f_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.f_display_name = QLineEdit(self.acc["display_name"])
        self.f_tiktok_username = QLineEdit(self.acc["tiktok_username"])
        self.f_bio = QTextEdit(self.acc["bio"])
        self.f_bio.setFixedHeight(80)
        self.f_proxy = QLineEdit(self.acc["proxy"])
        self.f_proxy.setPlaceholderText("http://user:pass@host:port")

        form.addRow("Логин:", self.f_login)
        form.addRow("Пароль:", self.f_password)
        form.addRow("Отображаемое имя:", self.f_display_name)
        form.addRow("TikTok username:", self.f_tiktok_username)
        form.addRow("Описание профиля:", self.f_bio)
        form.addRow("Прокси:", self.f_proxy)
        tabs.addTab(profile_tab, "Профиль")

        # Tab 2: Posting settings
        post_tab = QWidget()
        post_form = QFormLayout(post_tab)
        post_form.setSpacing(12)
        post_form.setContentsMargins(20, 20, 20, 20)

        self.f_niche = QLineEdit(self.acc["niche"])
        self.f_niche.setPlaceholderText("Например: фитнес, криптовалюта, мемы")
        self.f_target = QLineEdit(self.acc["target_audience"])
        self.f_target.setPlaceholderText("Например: молодёжь 18-25, предприниматели")
        self.f_hashtag_count = QSpinBox()
        self.f_hashtag_count.setRange(1, 30)
        self.f_hashtag_count.setValue(self.acc["hashtag_count"])
        self.f_interval_min = QSpinBox()
        self.f_interval_min.setRange(10, 1440)
        self.f_interval_min.setValue(self.acc["post_interval_min"])
        self.f_interval_max = QSpinBox()
        self.f_interval_max.setRange(10, 1440)
        self.f_interval_max.setValue(self.acc["post_interval_max"])
        self.f_max_posts = QSpinBox()
        self.f_max_posts.setRange(1, 50)
        self.f_max_posts.setValue(self.acc["max_posts_per_day"])

        post_form.addRow("Ниша:", self.f_niche)
        post_form.addRow("Целевая аудитория:", self.f_target)
        post_form.addRow("Кол-во хэштегов:", self.f_hashtag_count)
        post_form.addRow("Интервал мин (мин):", self.f_interval_min)
        post_form.addRow("Интервал макс (мин):", self.f_interval_max)
        post_form.addRow("Макс постов в день:", self.f_max_posts)
        tabs.addTab(post_tab, "Постинг")

        # Tab 3: Telegram
        tg_tab = QWidget()
        tg_form = QFormLayout(tg_tab)
        tg_form.setSpacing(12)
        tg_form.setContentsMargins(20, 20, 20, 20)

        self.f_tg_token = QLineEdit(self.acc["tg_bot_token"])
        self.f_tg_chat = QLineEdit(self.acc["tg_chat_id"])
        self.f_tg_success = QCheckBox("Успешная публикация")
        self.f_tg_success.setChecked(bool(self.acc["tg_report_success"]))
        self.f_tg_fail = QCheckBox("Ошибка публикации")
        self.f_tg_fail.setChecked(bool(self.acc["tg_report_fail"]))
        self.f_tg_interval = QSpinBox()
        self.f_tg_interval.setRange(5, 1440)
        self.f_tg_interval.setValue(self.acc["tg_report_interval"])

        tg_form.addRow("Токен бота:", self.f_tg_token)
        tg_form.addRow("Chat ID:", self.f_tg_chat)
        tg_form.addRow("Отчёт:", self.f_tg_success)
        tg_form.addRow("", self.f_tg_fail)
        tg_form.addRow("Интервал отчёта (мин):", self.f_tg_interval)
        tabs.addTab(tg_tab, "Telegram")

        # Tab 4: AI
        ai_tab = QWidget()
        ai_form = QFormLayout(ai_tab)
        ai_form.setSpacing(12)
        ai_form.setContentsMargins(20, 20, 20, 20)

        self.f_api_key = QLineEdit(self.acc["deepseek_api_key"])
        self.f_api_key.setPlaceholderText("sk-... (оставьте пустым для глобального)")
        self.f_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        ai_form.addRow("DeepSeek API Key:", self.f_api_key)
        tabs.addTab(ai_tab, "AI")

        layout.addWidget(tabs)

        # Buttons
        btn_row = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
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
            tg_report_interval=self.f_tg_interval.value(),
            deepseek_api_key=self.f_api_key.text(),
        )
        self.accept()


class AccountsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("Аккаунты")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()

        import_btn = QPushButton("📂 Импорт из TXT")
        import_btn.setObjectName("secondary_btn")
        import_btn.clicked.connect(self._import_txt)
        header.addWidget(import_btn)

        login_btn = QPushButton("🔑 Войти во все")
        login_btn.setObjectName("primary_btn")
        login_btn.clicked.connect(self._login_all)
        header.addWidget(login_btn)

        layout.addLayout(header)

        # Status bar
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.status_lbl)

        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.cards_widget = QWidget()
        self.cards_grid = QGridLayout(self.cards_widget)
        self.cards_grid.setSpacing(16)
        self.cards_grid.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.cards_widget)
        layout.addWidget(scroll)

    def refresh(self):
        # Clear grid
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        accounts = self.db.get_all_accounts()
        self.status_lbl.setText(f"Всего аккаунтов: {len(accounts)}")

        for i, acc in enumerate(accounts):
            acc_dict = dict(acc)
            # Get video count
            videos = self.db.get_videos_for_account(acc["id"])
            acc_dict["video_count"] = len(videos)

            card = AccountCard(acc_dict)
            card.clicked.connect(self._open_account)
            row = i // 3
            col = i % 3
            self.cards_grid.addWidget(card, row, col)

        if not accounts:
            empty = QLabel("Нет аккаунтов. Импортируйте из TXT файла.")
            empty.setStyleSheet("color: #aaa; font-size: 14px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cards_grid.addWidget(empty, 0, 0, 1, 3)

    def _import_txt(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Text Files (*.txt)")
        if not path:
            return
        manager = AccountManager(self.db)
        try:
            accounts = manager.import_from_txt(path)
            count = manager.save_imported_accounts(accounts)
            QMessageBox.information(self, "Импорт", f"Добавлено {count} аккаунтов")
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _login_all(self):
        self.status_lbl.setText("Выполняется вход...")
        self.worker = LoginWorker(self.db)
        self.worker.progress.connect(lambda msg: self.status_lbl.setText(msg))
        self.worker.finished.connect(self._on_login_done)
        self.worker.start()

    def _on_login_done(self, results):
        ok = sum(1 for r in results if r["success"])
        fail = len(results) - ok
        self.status_lbl.setText(f"Вход завершён: ✅ {ok} успешно, ❌ {fail} ошибок")
        self.refresh()

    def _open_account(self, account_id):
        dialog = AccountDetailDialog(self.db, account_id, self)
        if dialog.exec():
            self.refresh()
