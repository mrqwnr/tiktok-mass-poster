from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QFileDialog, QMessageBox,
    QDialog, QTabWidget, QLineEdit, QSpinBox, QTextEdit, QCheckBox,
    QFormLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from core.account_manager import AccountManager
import asyncio


class AccountCard(QFrame):
    clicked = pyqtSignal(int)
    delete_requested = pyqtSignal(int)

    def __init__(self, account):
        super().__init__()
        self.account_id = account["id"]
        self.setObjectName("account_card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(120)
        self._build(account)

    def _build(self, acc):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 12)
        layout.setSpacing(0)

        # Top row: avatar placeholder + name + status dot
        top = QHBoxLayout()
        top.setSpacing(12)

        # Avatar circle
        avatar = QLabel(acc["display_name"][0].upper() if acc["display_name"] else acc["login"][0].upper())
        avatar.setFixedSize(38, 38)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(
            "background: #F0F0F1; border-radius: 19px; "
            "font-size: 15px; font-weight: 700; color: #555555;"
        )
        top.addWidget(avatar)

        name_col = QVBoxLayout()
        name_col.setSpacing(2)

        name = QLabel(acc["display_name"] or acc["login"])
        name.setObjectName("card_name")
        name_col.addWidget(name)

        username = QLabel(f"@{acc['tiktok_username'] or acc['login']}")
        username.setObjectName("card_username")
        name_col.addWidget(username)

        top.addLayout(name_col)
        top.addStretch()

        # Status indicator
        status_colors = {
            "active": "#22C55E",
            "inactive": "#CCCCCC",
            "failed": "#EF4444",
            "captcha": "#F59E0B",
            "verify": "#3B82F6"
        }
        color = status_colors.get(acc["status"], "#CCCCCC")
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {color}; border-radius: 4px;")
        top.addWidget(dot)

        layout.addLayout(top)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background: #F0F0F1; border: none; max-height: 1px; margin: 10px 0 8px 0;")
        layout.addWidget(line)

        # Bottom stats
        videos = acc.get("video_count", 0) or 0
        stats = QLabel(f"{videos} videos  ·  {acc['status']}")
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
        self.setMinimumSize(560, 520)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        # --- Profile tab ---
        profile_tab = QWidget()
        form = QFormLayout(profile_tab)
        form.setSpacing(14)
        form.setContentsMargins(24, 20, 24, 20)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.f_login = QLineEdit(self.acc["login"])
        self.f_password = QLineEdit(self.acc["password"])
        self.f_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.f_display_name = QLineEdit(self.acc["display_name"])
        self.f_tiktok_username = QLineEdit(self.acc["tiktok_username"])
        self.f_bio = QTextEdit(self.acc["bio"])
        self.f_bio.setFixedHeight(72)
        self.f_proxy = QLineEdit(self.acc["proxy"])
        self.f_proxy.setPlaceholderText("http://user:pass@host:port")

        form.addRow("Login", self.f_login)
        form.addRow("Password", self.f_password)
        form.addRow("Display name", self.f_display_name)
        form.addRow("TikTok username", self.f_tiktok_username)
        form.addRow("Bio", self.f_bio)
        form.addRow("Proxy", self.f_proxy)
        tabs.addTab(profile_tab, "Profile")

        # --- Posting tab ---
        post_tab = QWidget()
        post_form = QFormLayout(post_tab)
        post_form.setSpacing(14)
        post_form.setContentsMargins(24, 20, 24, 20)

        self.f_niche = QLineEdit(self.acc["niche"])
        self.f_niche.setPlaceholderText("e.g. fitness, crypto, memes")
        self.f_target = QLineEdit(self.acc["target_audience"])
        self.f_target.setPlaceholderText("e.g. 18-25 y.o., entrepreneurs")
        self.f_hashtag_count = QSpinBox()
        self.f_hashtag_count.setRange(1, 30)
        self.f_hashtag_count.setValue(self.acc["hashtag_count"])
        self.f_interval_min = QSpinBox()
        self.f_interval_min.setRange(10, 1440)
        self.f_interval_min.setValue(self.acc["post_interval_min"])
        self.f_interval_min.setSuffix(" min")
        self.f_interval_max = QSpinBox()
        self.f_interval_max.setRange(10, 1440)
        self.f_interval_max.setValue(self.acc["post_interval_max"])
        self.f_interval_max.setSuffix(" min")
        self.f_max_posts = QSpinBox()
        self.f_max_posts.setRange(1, 50)
        self.f_max_posts.setValue(self.acc["max_posts_per_day"])
        self.f_max_posts.setSuffix(" / day")

        post_form.addRow("Niche", self.f_niche)
        post_form.addRow("Target audience", self.f_target)
        post_form.addRow("Hashtag count", self.f_hashtag_count)
        post_form.addRow("Interval min", self.f_interval_min)
        post_form.addRow("Interval max", self.f_interval_max)
        post_form.addRow("Max posts per day", self.f_max_posts)
        tabs.addTab(post_tab, "Posting")

        # --- Telegram tab ---
        tg_tab = QWidget()
        tg_form = QFormLayout(tg_tab)
        tg_form.setSpacing(14)
        tg_form.setContentsMargins(24, 20, 24, 20)

        self.f_tg_token = QLineEdit(self.acc["tg_bot_token"])
        self.f_tg_token.setPlaceholderText("1234567890:AAF...")
        self.f_tg_chat = QLineEdit(self.acc["tg_chat_id"])
        self.f_tg_chat.setPlaceholderText("-100...")
        self.f_tg_success = QCheckBox("Report on successful post")
        self.f_tg_success.setChecked(bool(self.acc["tg_report_success"]))
        self.f_tg_fail = QCheckBox("Report on failed post")
        self.f_tg_fail.setChecked(bool(self.acc["tg_report_fail"]))
        self.f_tg_interval = QSpinBox()
        self.f_tg_interval.setRange(5, 1440)
        self.f_tg_interval.setValue(self.acc["tg_report_interval"])
        self.f_tg_interval.setSuffix(" min")

        tg_form.addRow("Bot token", self.f_tg_token)
        tg_form.addRow("Chat ID", self.f_tg_chat)
        tg_form.addRow("", self.f_tg_success)
        tg_form.addRow("", self.f_tg_fail)
        tg_form.addRow("Stats interval", self.f_tg_interval)
        tabs.addTab(tg_tab, "Telegram")

        # --- AI tab ---
        ai_tab = QWidget()
        ai_form = QFormLayout(ai_tab)
        ai_form.setSpacing(14)
        ai_form.setContentsMargins(24, 20, 24, 20)

        self.f_api_key = QLineEdit(self.acc["deepseek_api_key"])
        self.f_api_key.setPlaceholderText("Leave empty to use global key")
        self.f_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        ai_form.addRow("DeepSeek API Key", self.f_api_key)
        tabs.addTab(ai_tab, "AI")

        layout.addWidget(tabs)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(20, 12, 20, 16)
        btn_row.setSpacing(10)

        delete_btn = QPushButton("Delete account")
        delete_btn.setObjectName("danger_btn")
        delete_btn.clicked.connect(self._delete)
        btn_row.addWidget(delete_btn)

        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
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
            tg_report_interval=self.f_tg_interval.value(),
            deepseek_api_key=self.f_api_key.text(),
        )
        self.accept()

    def _delete(self):
        reply = QMessageBox.question(
            self, "Delete account",
            f"Delete account {self.acc['login']}? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_account(self.account_id)
            self.done(2)  # custom code for delete


class AccountsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        header.setSpacing(10)

        title = QLabel("Accounts")
        title.setObjectName("page_title")
        header.addWidget(title)
        header.addStretch()

        self.delete_selected_btn = QPushButton("Delete selected")
        self.delete_selected_btn.setObjectName("danger_btn")
        self.delete_selected_btn.setVisible(False)
        self.delete_selected_btn.clicked.connect(self._delete_selected)
        header.addWidget(self.delete_selected_btn)

        import_btn = QPushButton("Import TXT")
        import_btn.setObjectName("secondary_btn")
        import_btn.clicked.connect(self._import_txt)
        header.addWidget(import_btn)

        login_btn = QPushButton("Login all")
        login_btn.setObjectName("primary_btn")
        login_btn.clicked.connect(self._login_all)
        header.addWidget(login_btn)

        layout.addLayout(header)

        # Status
        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("status_bar")
        layout.addWidget(self.status_lbl)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.cards_widget = QWidget()
        self.cards_grid = QGridLayout(self.cards_widget)
        self.cards_grid.setSpacing(14)
        self.cards_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll.setWidget(self.cards_widget)
        layout.addWidget(scroll)

        self._selected = set()

    def refresh(self):
        self._selected.clear()
        self.delete_selected_btn.setVisible(False)

        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        accounts = self.db.get_all_accounts()
        self.status_lbl.setText(f"{len(accounts)} accounts")

        for i, acc in enumerate(accounts):
            acc_dict = dict(acc)
            videos = self.db.get_videos_for_account(acc["id"])
            acc_dict["video_count"] = len(videos)

            card = AccountCard(acc_dict)
            card.clicked.connect(self._open_account)
            self.cards_grid.addWidget(card, i // 3, i % 3)

        if not accounts:
            empty = QLabel("No accounts yet. Import from a TXT file.")
            empty.setStyleSheet("color: #CCCCCC; font-size: 14px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cards_grid.addWidget(empty, 0, 0, 1, 3)

    def _import_txt(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select file", "", "Text Files (*.txt)")
        if not path:
            return
        manager = AccountManager(self.db)
        try:
            accounts = manager.import_from_txt(path)
            count = manager.save_imported_accounts(accounts)
            self.status_lbl.setText(f"Imported {count} accounts")
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _login_all(self):
        self.status_lbl.setText("Logging in...")
        self.worker = LoginWorker(self.db)
        self.worker.progress.connect(lambda msg: self.status_lbl.setText(msg))
        self.worker.finished.connect(self._on_login_done)
        self.worker.start()

    def _on_login_done(self, results):
        ok = sum(1 for r in results if r["success"])
        fail = len(results) - ok
        self.status_lbl.setText(f"Done: {ok} logged in, {fail} failed")
        self.refresh()

    def _open_account(self, account_id):
        dialog = AccountDetailDialog(self.db, account_id, self)
        result = dialog.exec()
        if result in (1, 2):  # saved or deleted
            self.refresh()

    def _delete_selected(self):
        if not self._selected:
            return
        reply = QMessageBox.question(
            self, "Delete accounts",
            f"Delete {len(self._selected)} selected accounts?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for acc_id in self._selected:
                self.db.delete_account(acc_id)
            self.refresh()
