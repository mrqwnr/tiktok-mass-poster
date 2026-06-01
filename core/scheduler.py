import asyncio
import threading
from datetime import datetime, timedelta
import random

class Scheduler:
    """Manages posting schedules for accounts."""

    def __init__(self, db, poster):
        self.db = db
        self.poster = poster
        self._thread = None
        self._running = False

    def start(self, account_ids: list, video_paths: list, caption: str, niche: str, target_audience: str):
        """Start the scheduler in a background thread."""
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            args=(account_ids, video_paths, caption, niche, target_audience),
            daemon=True
        )
        self._thread.start()

    def stop(self):
        self._running = False
        self.poster.stop()

    def _run_loop(self, account_ids, video_paths, caption, niche, target_audience):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            self.poster.run_posting_session(account_ids, video_paths, caption, niche, target_audience)
        )
        loop.close()
