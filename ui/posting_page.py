from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QFileDialog, QListWidget, QListWidgetItem,
    QTextEdit, QCheckBox, QProgressBar, QSplitter, QMessageBox,
    QAbstractItemView, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont
from core.poster import TikTokPoster
from core.ai_helper import AIHelper
import asyncio
import os


class PostWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)

    def __init__(self, db, tasks):
        super().__init__()
        self.db = db
        self.tasks = tasks

    def run(self):
        poster = TikTokPoster(self.db)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(
            poster.post_batch(self.tasks, self.progress.emit)
        )
        loop.close()
        self.finished.emit(results)


class AIWorker(QThread):
    finished = pyqtSignal(str, str)  # caption, hashtags
    error = pyqtSignal(str)

    def __init__(self, db, niche, audience, hashtag_count):
        super().__init__()
        self.db = db
        self.niche = niche
        self.audience = audience
        self.hashtag_count = hashtag_count

    def run(self):
        try:
            ai = AIHelper(self.db)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            caption = loop.run_until_complete(ai.generate_caption(self.niche, self.audience))
            hashtags = loop.run_until_complete(ai.generate_hashtags(self.niche, self.audience, self.hashtag_count))
            loop.close()
            self.finished.emit(caption, hashtags)
        except Exception as e:
            self.error.emit(str(e))


class PostingPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.video_paths = []
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 36, 36, 36)
        root.setSpacing(20)

        # Заголовок
        hdr = QHBoxLayout()
        title = QLabel("Постинг")
        title.setObjectName("page_title")
        hdr.addWidget(title)
        hdr.addStretch()
        root.addLayout(hdr)

        # Сплиттер: левая панель + лог
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background: #EBEBEB; }")

        # ── Левая панель ──
        left = QWidget()
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 16, 0)
        left_lay.setSpacing(16)

        # Аккаунты
        acc_lbl = QLabel("Аккаунты")
        acc_lbl.setObjectName("section_title")
        left_lay.addWidget(acc_lbl)

        acc_hint = QLabel("Выберите аккаунты для постинга (Ctrl+A — все)")
        acc_hint.setStyleSheet("color: #BBBBBB; font-size: 12px; font-weight: 500;")
        left_lay.addWidget(acc_hint)

        self.acc_list = QListWidget()
        self.acc_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.acc_list.setFixedHeight(180)
        left_lay.addWidget(self.acc_list)

        # Видео
        vid_lbl = QLabel("Видео")
        vid_lbl.setObjectName("section_title")
        left_lay.addWidget(vid_lbl)

        vid_btn_row = QHBoxLayout()
        add_vid_btn = QPushButton("Добавить видео")
        add_vid_btn.setObjectName("secondary_btn")
        add_vid_btn.clicked.connect(self._add_videos)
        clear_vid_btn = QPushButton("Очистить")
        clear_vid_btn.setObjectName("secondary_btn")
        clear_vid_btn.clicked.connect(self._clear_videos)
        vid_btn_row.addWidget(add_vid_btn)
        vid_btn_row.addWidget(clear_vid_btn)
        vid_btn_row.addStretch()
        left_lay.addLayout(vid_btn_row)

        self.vid_list = QListWidget()
        self.vid_list.setFixedHeight(140)
        left_lay.addWidget(self.vid_list)

        # Описание и хэштеги
        cap_lbl = QLabel("Описание")
        cap_lbl.setObjectName("section_title")
        left_lay.addWidget(cap_lbl)

        self.caption_edit = QTextEdit()
        self.caption_edit.setPlaceholderText("Описание видео (оставьте пустым для AI-генерации)")
        self.caption_edit.setFixedHeight(80)
        left_lay.addWidget(self.caption_edit)

        hash_lbl = QLabel("Хэштеги")
        hash_lbl.setObjectName("section_title")
        left_lay.addWidget(hash_lbl)

        self.hashtags_edit = QTextEdit()
        self.hashtags_edit.setPlaceholderText("#хэштег1 #хэштег2 ...")
        self.hashtags_edit.setFixedHeight(60)
        left_lay.addWidget(self.hashtags_edit)

        # AI кнопка
        ai_row = QHBoxLayout()
        self.ai_btn = QPushButton("Сгенерировать через AI")
        self.ai_btn.setObjectName("secondary_btn")
        self.ai_btn.clicked.connect(self._generate_ai)
        ai_row.addWidget(self.ai_btn)
        ai_row.addStretch()
        left_lay.addLayout(ai_row)

        left_lay.addStretch()

        # Кнопка запуска
        self.start_btn = QPushButton("Запустить постинг")
        self.start_btn.setObjectName("primary_btn")
        self.start_btn.setFixedHeight(48)
        self.start_btn.setStyleSheet(
            self.start_btn.styleSheet() +
            "QPushButton#primary_btn { font-size: 16px; }"
        )
        self.start_btn.clicked.connect(self._start_posting)
        left_lay.addWidget(self.start_btn)

        splitter.addWidget(left)

        # ── Правая панель: лог ──
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(16, 0, 0, 0)
        right_lay.setSpacing(12)

        log_lbl = QLabel("Лог")
        log_lbl.setObjectName("section_title")
        right_lay.addWidget(log_lbl)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right_lay.addWidget(self.progress_bar)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet(
            "QTextEdit { background: #FAFAFA; border: 1.5px solid #EBEBEB; "
            "border-radius: 12px; padding: 12px; font-size: 13px; "
            "font-weight: 500; color: #333333; font-family: 'Consolas', monospace; }"
        )
        right_lay.addWidget(self.log_box)

        splitter.addWidget(right)
        splitter.setSizes([480, 400])

        root.addWidget(splitter)

    def refresh(self):
        self.acc_list.clear()
        accounts = self.db.get_all_accounts()
        for acc in accounts:
            item = QListWidgetItem(f"{acc['display_name'] or acc['login']}  (@{acc['tiktok_username'] or acc['login']})")
            item.setData(Qt.ItemDataRole.UserRole, acc["id"])
            status_color = {
                "active": "#22C55E", "inactive": "#AAAAAA",
                "failed": "#EF4444", "captcha": "#F59E0B"
            }.get(acc["status"], "#AAAAAA")
            item.setForeground(__import__("PyQt6.QtGui", fromlist=["QColor"]).QColor(status_color)
                               if acc["status"] != "active" else
                               __import__("PyQt6.QtGui", fromlist=["QColor"]).QColor("#0D0D0D"))
            self.acc_list.addItem(item)

    def _add_videos(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Выберите видео", "",
            "Видео (*.mp4 *.mov *.avi *.mkv *.webm)"
        )
        for p in paths:
            if p not in self.video_paths:
                self.video_paths.append(p)
                self.vid_list.addItem(os.path.basename(p))

    def _clear_videos(self):
        self.video_paths.clear()
        self.vid_list.clear()

    def _generate_ai(self):
        selected = self.acc_list.selectedItems()
        niche = ""
        audience = ""
        hashtag_count = 10

        if selected:
            acc_id = selected[0].data(Qt.ItemDataRole.UserRole)
            acc = dict(self.db.get_account(acc_id))
            niche = acc.get("niche", "")
            audience = acc.get("target_audience", "")
            hashtag_count = acc.get("hashtag_count", 10)

        self.ai_btn.setText("Генерирую...")
        self.ai_btn.setEnabled(False)

        self.ai_worker = AIWorker(self.db, niche, audience, hashtag_count)
        self.ai_worker.finished.connect(self._on_ai_done)
        self.ai_worker.error.connect(self._on_ai_error)
        self.ai_worker.start()

    def _on_ai_done(self, caption, hashtags):
        self.caption_edit.setPlainText(caption)
        self.hashtags_edit.setPlainText(hashtags)
        self.ai_btn.setText("Сгенерировать через AI")
        self.ai_btn.setEnabled(True)
        self._log("AI сгенерировал описание и хэштеги.")

    def _on_ai_error(self, err):
        self.ai_btn.setText("Сгенерировать через AI")
        self.ai_btn.setEnabled(True)
        self._log(f"Ошибка AI: {err}")

    def _start_posting(self):
        selected_accs = self.acc_list.selectedItems()
        if not selected_accs:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один аккаунт.")
            return
        if not self.video_paths:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы одно видео.")
            return

        caption = self.caption_edit.toPlainText().strip()
        hashtags = self.hashtags_edit.toPlainText().strip()

        # Создаём задачи: каждый аккаунт × каждое видео
        tasks = []
        for item in selected_accs:
            acc_id = item.data(Qt.ItemDataRole.UserRole)
            for vpath in self.video_paths:
                vid_id = self.db.add_video(acc_id, vpath, caption, hashtags)
                tasks.append({"account_id": acc_id, "video_id": vid_id})

        self._log(f"Запускаю постинг: {len(tasks)} задач...")
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # бесконечный

        self.worker = PostWorker(self.db, tasks)
        self.worker.progress.connect(self._log)
        self.worker.finished.connect(self._on_done)
        self.worker.start()

    def _on_done(self, results):
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        ok = sum(1 for r in results if r["success"])
        fail = len(results) - ok
        self._log(f"Готово! Успешно: {ok}, ошибок: {fail}")

    def _log(self, msg: str):
        self.log_box.append(msg)
        self.log_box.verticalScrollBar().setValue(
            self.log_box.verticalScrollBar().maximum()
        )
