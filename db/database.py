import sqlite3
from pathlib import Path

DB_PATH = Path("data/tiktok_poster.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()
        self._seed_settings()

    def _create_tables(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS accounts (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            login               TEXT NOT NULL UNIQUE,
            password            TEXT NOT NULL,
            proxy               TEXT DEFAULT '',
            status              TEXT DEFAULT 'inactive',
            avatar_path         TEXT DEFAULT '',
            tiktok_username     TEXT DEFAULT '',
            display_name        TEXT DEFAULT '',
            bio                 TEXT DEFAULT '',
            deepseek_api_key    TEXT DEFAULT '',
            tg_bot_token        TEXT DEFAULT '',
            tg_chat_id          TEXT DEFAULT '',
            tg_report_success   INTEGER DEFAULT 1,
            tg_report_fail      INTEGER DEFAULT 1,
            tg_report_interval  INTEGER DEFAULT 60,
            post_interval_min   INTEGER DEFAULT 60,
            post_interval_max   INTEGER DEFAULT 180,
            max_posts_per_day   INTEGER DEFAULT 5,
            hashtag_count       INTEGER DEFAULT 10,
            target_audience     TEXT DEFAULT '',
            niche               TEXT DEFAULT '',
            created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS videos (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id      INTEGER NOT NULL,
            file_path       TEXT NOT NULL,
            caption         TEXT DEFAULT '',
            hashtags        TEXT DEFAULT '',
            status          TEXT DEFAULT 'pending',
            views           INTEGER DEFAULT 0,
            likes           INTEGER DEFAULT 0,
            comments        INTEGER DEFAULT 0,
            posted_at       TIMESTAMP,
            tiktok_video_id TEXT DEFAULT '',
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS global_settings (
            key     TEXT PRIMARY KEY,
            value   TEXT
        );
        """)
        self.conn.commit()

    def _seed_settings(self):
        defaults = {
            "deepseek_api_key":          "",
            "tg_bot_token":              "",
            "tg_chat_id":                "",
            "default_post_interval_min": "60",
            "default_post_interval_max": "180",
            "default_max_posts_per_day": "5",
            "default_hashtag_count":     "10",
            "headless_browser":          "0",
            "random_delay_min":          "2",
            "random_delay_max":          "8",
        }
        for k, v in defaults.items():
            self.conn.execute(
                "INSERT OR IGNORE INTO global_settings (key, value) VALUES (?, ?)", (k, v)
            )
        self.conn.commit()

    # ------------------------------------------------------------------ #
    #  Accounts                                                            #
    # ------------------------------------------------------------------ #

    def add_account(self, login: str, password: str) -> int:
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO accounts (login, password) VALUES (?, ?)",
            (login, password),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_all_accounts(self):
        return self.conn.execute("SELECT * FROM accounts ORDER BY id").fetchall()

    def get_account(self, account_id: int):
        return self.conn.execute(
            "SELECT * FROM accounts WHERE id = ?", (account_id,)
        ).fetchone()

    def update_account(self, account_id: int, **kwargs):
        if not kwargs:
            return
        fields = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [account_id]
        self.conn.execute(f"UPDATE accounts SET {fields} WHERE id = ?", values)
        self.conn.commit()

    def update_account_status(self, account_id: int, status: str):
        self.conn.execute(
            "UPDATE accounts SET status = ? WHERE id = ?", (status, account_id)
        )
        self.conn.commit()

    def delete_account(self, account_id: int):
        self.conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        self.conn.commit()

    # ------------------------------------------------------------------ #
    #  Videos                                                             #
    # ------------------------------------------------------------------ #

    def add_video(self, account_id: int, file_path: str,
                  caption: str = "", hashtags: str = "") -> int:
        cur = self.conn.execute(
            "INSERT INTO videos (account_id, file_path, caption, hashtags) VALUES (?, ?, ?, ?)",
            (account_id, file_path, caption, hashtags),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_video(self, video_id: int):
        return self.conn.execute(
            "SELECT * FROM videos WHERE id = ?", (video_id,)
        ).fetchone()

    def get_videos_for_account(self, account_id: int):
        return self.conn.execute(
            "SELECT * FROM videos WHERE account_id = ? ORDER BY id DESC",
            (account_id,)
        ).fetchall()

    def get_pending_videos(self, account_id: int):
        return self.conn.execute(
            "SELECT * FROM videos WHERE account_id = ? AND status = 'pending' ORDER BY id",
            (account_id,)
        ).fetchall()

    def update_video_status(self, video_id: int, status: str, tiktok_video_id: str = ""):
        self.conn.execute(
            "UPDATE videos SET status = ?, tiktok_video_id = ?, "
            "posted_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, tiktok_video_id, video_id),
        )
        self.conn.commit()

    def update_video_stats(self, video_id: int, views: int, likes: int, comments: int):
        self.conn.execute(
            "UPDATE videos SET views = ?, likes = ?, comments = ? WHERE id = ?",
            (views, likes, comments, video_id),
        )
        self.conn.commit()

    # ------------------------------------------------------------------ #
    #  Settings                                                           #
    # ------------------------------------------------------------------ #

    def get_setting(self, key: str, default: str = "") -> str:
        row = self.conn.execute(
            "SELECT value FROM global_settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO global_settings (key, value) VALUES (?, ?)",
            (key, str(value)),
        )
        self.conn.commit()

    def get_all_settings(self) -> dict:
        rows = self.conn.execute(
            "SELECT key, value FROM global_settings"
        ).fetchall()
        return {r["key"]: r["value"] for r in rows}

    # ------------------------------------------------------------------ #
    #  Stats                                                              #
    # ------------------------------------------------------------------ #

    def get_stats_summary(self) -> dict:
        total_accounts = self.conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
        total_videos   = self.conn.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
        posted_videos  = self.conn.execute(
            "SELECT COUNT(*) FROM videos WHERE status = 'posted'"
        ).fetchone()[0]
        failed_videos  = self.conn.execute(
            "SELECT COUNT(*) FROM videos WHERE status = 'failed'"
        ).fetchone()[0]
        total_views    = self.conn.execute("SELECT SUM(views) FROM videos").fetchone()[0]
        total_likes    = self.conn.execute("SELECT SUM(likes) FROM videos").fetchone()[0]
        return {
            "total_accounts": total_accounts,
            "total_videos":   total_videos,
            "posted_videos":  posted_videos,
            "failed_videos":  failed_videos,
            "total_views":    total_views or 0,
            "total_likes":    total_likes or 0,
        }

    def get_top_accounts(self, limit: int = 5) -> list:
        rows = self.conn.execute("""
            SELECT
                a.id, a.login, a.display_name,
                COUNT(v.id)                  AS video_count,
                COALESCE(SUM(v.views),  0)   AS total_views,
                COALESCE(SUM(v.likes),  0)   AS total_likes
            FROM accounts a
            LEFT JOIN videos v ON v.account_id = a.id
            GROUP BY a.id
            ORDER BY total_views DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]
