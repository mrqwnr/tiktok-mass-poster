from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt

class StatCard(QFrame):
    def __init__(self, label, value):
        super().__init__()
        self.setObjectName("card")
        self.setFixedHeight(110)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(6)
        self.val = QLabel(str(value))
        self.val.setObjectName("stat_value")
        lay.addWidget(self.val)
        lbl = QLabel(label)
        lbl.setObjectName("stat_label")
        lay.addWidget(lbl)

    def update_value(self, v): self.val.setText(str(v))


class TopRow(QFrame):
    def __init__(self, rank, login, views, likes, videos):
        super().__init__()
        self.setObjectName("card")
        self.setFixedHeight(64)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(22, 0, 22, 0)
        lay.setSpacing(16)

        rk = QLabel(str(rank))
        rk.setFixedWidth(28)
        rk.setStyleSheet("font-size: 18px; font-weight: 800; color: #DDDDDD;")
        lay.addWidget(rk)

        nm = QLabel(login)
        nm.setStyleSheet("font-size: 15px; font-weight: 700; color: #0D0D0D;")
        lay.addWidget(nm)
        lay.addStretch()

        for val, lbl in [(views or 0, "просмотры"), (likes or 0, "лайки"), (videos or 0, "видео")]:
            col = QVBoxLayout()
            col.setSpacing(1)
            v = QLabel(str(val))
            v.setStyleSheet("font-size: 14px; font-weight: 700; color: #0D0D0D;")
            v.setAlignment(Qt.AlignmentFlag.AlignRight)
            l = QLabel(lbl)
            l.setStyleSheet("font-size: 11px; font-weight: 500; color: #BBBBBB;")
            l.setAlignment(Qt.AlignmentFlag.AlignRight)
            col.addWidget(v); col.addWidget(l)
            lay.addLayout(col)
            lay.addSpacing(8)


class DashboardPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._build()

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        self.lay = QVBoxLayout(content)
        self.lay.setContentsMargins(36, 36, 36, 36)
        self.lay.setSpacing(28)

        title = QLabel("Главная")
        title.setObjectName("page_title")
        self.lay.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(14)
        self.s_acc   = StatCard("Аккаунтов", "0")
        self.s_vid   = StatCard("Всего видео", "0")
        self.s_post  = StatCard("Опубликовано", "0")
        self.s_views = StatCard("Просмотров", "0")
        self.s_likes = StatCard("Лайков", "0")
        self.s_fail  = StatCard("Ошибок", "0")
        for i, c in enumerate([self.s_acc, self.s_vid, self.s_post,
                                self.s_views, self.s_likes, self.s_fail]):
            grid.addWidget(c, i // 3, i % 3)
        self.lay.addLayout(grid)

        top_lbl = QLabel("Топ аккаунты")
        top_lbl.setObjectName("section_title")
        self.lay.addWidget(top_lbl)

        self.top_lay = QVBoxLayout()
        self.top_lay.setSpacing(10)
        self.lay.addLayout(self.top_lay)
        self.lay.addStretch()

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh(self):
        s = self.db.get_stats_summary()
        self.s_acc.update_value(s.get("total_accounts", 0))
        self.s_vid.update_value(s.get("total_videos", 0))
        self.s_post.update_value(s.get("posted_videos", 0))
        self.s_views.update_value(s.get("total_views", 0))
        self.s_likes.update_value(s.get("total_likes", 0))
        self.s_fail.update_value(s.get("failed_videos", 0))

        while self.top_lay.count():
            item = self.top_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        top = self.db.get_top_accounts(5)
        for i, a in enumerate(top):
            self.top_lay.addWidget(TopRow(i+1, a["login"], a["total_views"], a["total_likes"], a["video_count"]))
        if not top:
            e = QLabel("Нет данных. Добавьте аккаунты и начните постинг.")
            e.setStyleSheet("color: #CCCCCC; font-size: 14px; font-weight: 500;")
            self.top_lay.addWidget(e)
