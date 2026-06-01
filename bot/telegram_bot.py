import asyncio
import threading
from telegram import Bot
from telegram.error import TelegramError

class TelegramReporter:
    """Sends posting reports to Telegram."""

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=token) if token else None

    async def _send(self, text: str):
        if not self.bot or not self.chat_id:
            return
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode="HTML")
        except TelegramError as e:
            print(f"Telegram error: {e}")

    def send(self, text: str):
        """Send message synchronously."""
        if not self.token or not self.chat_id:
            return
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._send(text))
        loop.close()

    def report_post_success(self, account_login: str, video_path: str):
        self.send(f"✅ <b>Опубликовано</b>\nАккаунт: <code>{account_login}</code>\nВидео: {video_path}")

    def report_post_fail(self, account_login: str, reason: str):
        self.send(f"❌ <b>Ошибка публикации</b>\nАккаунт: <code>{account_login}</code>\nПричина: {reason}")

    def report_stats(self, account_login: str, views: int, likes: int, video_count: int):
        self.send(
            f"📊 <b>Статистика</b>\n"
            f"Аккаунт: <code>{account_login}</code>\n"
            f"Видео: {video_count} | 👁 {views} | ❤️ {likes}"
        )
