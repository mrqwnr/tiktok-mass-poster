import asyncio
import random
import os
from playwright.async_api import async_playwright
from core.video_editor import VideoEditor
from core.ai_helper import AIHelper

class Poster:
    """Handles posting videos to TikTok."""

    def __init__(self, db, progress_callback=None):
        self.db = db
        self.progress_callback = progress_callback
        self.editor = VideoEditor()
        self._running = False

    def log(self, msg):
        if self.progress_callback:
            self.progress_callback(msg)

    async def post_video(self, account_id: int, video_path: str, caption: str, hashtags: list) -> dict:
        """Post a single video to TikTok for given account."""
        account = self.db.get_account(account_id)
        if not account:
            return {"success": False, "message": "Account not found"}

        proxy = account["proxy"]
        proxy_config = {"server": proxy} if proxy else None

        full_caption = caption
        if hashtags:
            full_caption += " " + " ".join(hashtags)

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.db.get_setting("headless_browser", "1") == "1",
                    proxy=proxy_config,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    viewport={"width": 1280, "height": 720}
                )
                page = await context.new_page()

                self.log(f"[{account['login']}] Открываю TikTok Studio...")
                await page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="networkidle")
                await asyncio.sleep(random.uniform(2, 4))

                # Upload video file
                self.log(f"[{account['login']}] Загружаю видео...")
                file_input = await page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(video_path)
                    await asyncio.sleep(random.uniform(5, 10))

                # Fill caption
                caption_input = await page.query_selector('[data-text="true"]')
                if caption_input:
                    await caption_input.click()
                    await asyncio.sleep(0.5)
                    await page.keyboard.type(full_caption, delay=random.randint(50, 150))
                    await asyncio.sleep(random.uniform(1, 2))

                # Post
                post_btn = await page.query_selector('button:has-text("Post")')
                if post_btn:
                    await post_btn.click()
                    await asyncio.sleep(random.uniform(3, 6))
                    self.log(f"[{account['login']}] Видео опубликовано!")
                    await browser.close()
                    return {"success": True, "message": "Опубликовано"}

                await browser.close()
                return {"success": False, "message": "Кнопка Post не найдена"}

        except Exception as e:
            return {"success": False, "message": str(e)}

    async def run_posting_session(self, account_ids: list, video_paths: list, caption: str, niche: str, target_audience: str):
        """Run posting session for multiple accounts."""
        self._running = True
        for account_id in account_ids:
            if not self._running:
                break

            account = self.db.get_account(account_id)
            api_key = account["deepseek_api_key"] or self.db.get_setting("deepseek_api_key")

            # Pick random video
            video_path = random.choice(video_paths)

            # Generate hashtags via AI
            hashtags = []
            if api_key:
                try:
                    ai = AIHelper(api_key)
                    hashtags = ai.generate_hashtags(niche, target_audience, account["hashtag_count"])
                    caption_final = ai.rephrase_caption(caption)
                except Exception as e:
                    self.log(f"AI error: {e}")
                    caption_final = caption
            else:
                caption_final = caption

            # Process video
            try:
                processed_path = self.editor.process_video(video_path, caption_final)
            except Exception as e:
                self.log(f"Video processing error: {e}")
                processed_path = video_path

            # Post
            result = await self.post_video(account_id, processed_path, caption_final, hashtags)

            # Save to DB
            video_id = self.db.add_video(
                account_id, processed_path, caption_final, " ".join(hashtags)
            )
            self.db.update_video(
                video_id,
                status="posted" if result["success"] else "failed"
            )

            # Delay between accounts
            delay_min = int(self.db.get_setting("random_delay_min", "2"))
            delay_max = int(self.db.get_setting("random_delay_max", "8"))
            await asyncio.sleep(random.uniform(delay_min * 60, delay_max * 60))

        self._running = False

    def stop(self):
        self._running = False
