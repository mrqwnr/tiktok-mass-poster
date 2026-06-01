import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "app.db")

class Database:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def init(self):
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT NOT NULL,
            password TEXT NOT NULL,
            proxy TEXT DEFAULT '',
            status TEXT DEFAULT 'inactive',
            avatar_path TEXT DEFAULT '',
            username TEXT DEFAULT '',
            display_name TEXT DEFAULT '',
            bio TEXT DEFAULT '',
            tiktok_username TEXT DEFAULT '',
            deepseek_api_key TEXT DEFAULT '',
            tg_bot_token TEXT DEFAULT '',
            tg_chat_id TEXT DEFAULT '',
            tg_report_success INTEGER DEFAULT 1,
            tg_report_fail INTEGER DEFAULT 1,
            tg_report_interval INTEGER DEFAULT 30,
            post_interval_min INTEGER DEFAULT 60,
            post_interval_max INTEGER DEFAULT 180,
            max_posts_per_day INTEGER DEFAULT 5,
            hashtag_count INTEGER DEFAULT 10,
            target_audience TEXT DEFAULT '',
            niche TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER,
            file_path TEXT NOT NULL,
            caption TEXT DEFAULT '',
            hashtags TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            posted_at TIMESTAMP,
            tiktok_video_id TEXT DEFAULT '',
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS global_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)
        defaults = [
            ("deepseek_api_key", ""),
            ("tg_bot_token", ""),
            ("tg_chat_id", ""),
            ("default_post_interval_min", "60"),
            ("default_post_interval_max", "180"),
            ("default_max_posts_per_day", "5"),
            ("default_hashtag_count", "10"),
            ("headless_browser", "1"),
            ("random_delay_min", "2"),
            ("random_delay_max", "8"),
        ]
        for key, val in defaults:
            c.execute("INSERT OR IGNORE INTO global_settings (key, value) VALUES (?, ?)", (key, val))
        self.conn.commit()

    def get_setting(self, key, default=""):
        c = self.conn.cursor()
        c.execute("SELECT value FROM global_settings WHERE key=?", (key,))
        row = c.fetchone()
        return row["value"] if row else default

    def set_setting(self, key, value):
        self.conn.execute(
            "INSERT OR REPLACE INTO global_settings (key, value) VALUES (?, ?)",
            (key, str(value))
        )
        self.conn.commit()

    def get_all_accounts(self):
        return self.conn.execute("SELECT * FROM accounts ORDER BY id").fetchall()

    def get_account(self, account_id):
        return self.conn.execute("SELECT * FROM accounts WHERE id=?", (account_id,)).fetchone()

    def add_account(self, login, password):
        c = self.conn.cursor()
        c.execute("INSERT INTO accounts (login, password) VALUES (?, ?)", (login, password))
        self.conn.commit()
        return c.lastrowid

    def update_account(self, account_id, **kwargs):
        if not kwargs:
            return
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [account_id]
        self.conn.execute(f"UPDATE accounts SET {sets} WHERE id=?", vals)
        self.conn.commit()

    def delete_account(self, account_id):
        self.conn.execute("DELETE FROM accounts WHERE id=?", (account_id,))
        self.conn.commit()

    def get_videos_for_account(self, account_id):
        return self.conn.execute(
            "SELECT * FROM videos WHERE account_id=? ORDER BY posted_at DESC",
            (account_id,)
        ).fetchall()

    def add_video(self, account_id, file_path, caption="", hashtags=""):
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO videos (account_id, file_path, caption, hashtags) VALUES (?, ?, ?, ?)",
            (account_id, file_path, caption, hashtags)
        )
        self.conn.commit()
        return c.lastrowid

    def update_video(self, video_id, **kwargs):
        if not kwargs:
            return
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [video_id]
        self.conn.execute(f"UPDATE videos SET {sets} WHERE id=?", vals)
        self.conn.commit()

    def get_stats_summary(self):
        row = self.conn.execute("""
            SELECT
                COUNT(DISTINCT a.id) as total_accounts,
                COUNT(v.id) as total_videos,
                SUM(v.views) as total_views,
                SUM(v.likes) as total_likes,
                SUM(CASE WHEN v.status='posted' THEN 1 ELSE 0 END) as posted_videos,
                SUM(CASE WHEN v.status='failed' THEN 1 ELSE 0 END) as failed_videos
            FROM accounts a
            LEFT JOIN videos v ON v.account_id = a.id
        """).fetchone()
        return dict(row) if row else {}

    def get_top_accounts(self, limit=3):
        return self.conn.execute("""
            SELECT a.*,
                   SUM(v.views) as total_views,
                   SUM(v.likes) as total_likes,
                   COUNT(v.id) as video_count
            FROM accounts a
            LEFT JOIN videos v ON v.account_id = a.id
            GROUP BY a.id
            ORDER BY total_views DESC
            LIMIT ?
        """, (limit,)).fetchall()
