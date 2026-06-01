from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class StatCard(QFrame):
    def __init__(self, label, value, icon=""):
        super().__init__()
        self.setObjectName("card")
        self.setFixedHeight(110)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI", 22))
        top.addWidget(icon_lbl)
        top.addStretch()
        layout.addLayout(top)

        val_lbl = QLabel(str(value))
        val_lbl.setObjectName("stat_value")
        layout.addWidget(val_lbl)
        self.val_lbl = val_lbl

        lbl = QLabel(label)
        lbl.setObjectName("stat_label")
        layout.addWidget(lbl)

    def update_value(self, value):
        self.val_lbl.setText(str(value))


class TopAccountCard(QFrame):
    def __init__(self, rank, login, views, likes, videos):
        super().__init__()
        self.setObjectName("card")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        rank_lbl = QLabel(f"#{rank}")
        rank_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        rank_lbl.setStyleSheet("color: #fe2c55;")
        rank_lbl.setFixedWidth(40)
        layout.addWidget(rank_lbl)

        info = QVBoxLayout()
        name_lbl = QLabel(login)
        name_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        info.addWidget(name_lbl)

        stats_lbl = QLabel(f"👁 {views or 0}  ❤️ {likes or 0}  🎬 {videos or 0}")
        stats_lbl.setStyleSheet("color: #888; font-size: 12px;")
        info.addWidget(stats_lbl)
        layout.addLayout(info)
        layout.addStretch()


class DashboardPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        self.main_layout = QVBoxLayout(content)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        # Title
        title = QLabel("Главная")
        title.setObjectName("title")
        self.main_layout.addWidget(title)

        # Stats row
        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)

        self.stat_accounts = StatCard("Аккаунтов", "0", "👤")
        self.stat_videos = StatCard("Видео всего", "0", "🎬")
        self.stat_posted = StatCard("Опубликовано", "0", "✅")
        self.stat_views = StatCard("Просмотров", "0", "👁")
        self.stat_likes = StatCard("Лайков", "0", "❤️")
        self.stat_failed = StatCard("Ошибок", "0", "❌")

        stats_grid.addWidget(self.stat_accounts, 0, 0)
        stats_grid.addWidget(self.stat_videos, 0, 1)
        stats_grid.addWidget(self.stat_posted, 0, 2)
        stats_grid.addWidget(self.stat_views, 1, 0)
        stats_grid.addWidget(self.stat_likes, 1, 1)
        stats_grid.addWidget(self.stat_failed, 1, 2)

        self.main_layout.addLayout(stats_grid)

        # Top accounts
        top_title = QLabel("🏆 Топ 3 аккаунта")
        top_title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        self.main_layout.addWidget(top_title)

        self.top_accounts_layout = QVBoxLayout()
        self.top_accounts_layout.setSpacing(10)
        self.main_layout.addLayout(self.top_accounts_layout)

        self.main_layout.addStretch()

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh(self):
        stats = self.db.get_stats_summary()
        self.stat_accounts.update_value(stats.get("total_accounts", 0))
        self.stat_videos.update_value(stats.get("total_videos", 0))
        self.stat_posted.update_value(stats.get("posted_videos", 0))
        self.stat_views.update_value(stats.get("total_views", 0) or 0)
        self.stat_likes.update_value(stats.get("total_likes", 0) or 0)
        self.stat_failed.update_value(stats.get("failed_videos", 0))

        # Clear top accounts
        while self.top_accounts_layout.count():
            item = self.top_accounts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        top = self.db.get_top_accounts(3)
        for i, acc in enumerate(top):
            card = TopAccountCard(
                i + 1,
                acc["login"],
                acc["total_views"],
                acc["total_likes"],
                acc["video_count"]
            )
            self.top_accounts_layout.addWidget(card)

        if not top:
            empty = QLabel("Нет данных. Добавьте аккаунты и начните постинг.")
            empty.setStyleSheet("color: #aaa; font-size: 13px;")
            self.top_accounts_layout.addWidget(empty)
