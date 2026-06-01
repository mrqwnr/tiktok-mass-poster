import asyncio
import json
import random
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

SESSIONS_DIR = Path("data/sessions")


class TikTokPoster:
    def __init__(self, db):
        self.db = db

    def session_path(self, account_id: int) -> Path:
        return SESSIONS_DIR / f"account_{account_id}.json"

    async def post_video(self, account_id: int, video_id: int, progress_cb=None) -> dict:
        """
        Публикует одно видео в TikTok.
        Возвращает: {success, message, tiktok_video_id}
        """
        acc = dict(self.db.get_account(account_id))
        video = dict(self.db.get_video(video_id))
        login = acc["login"]

        def log(msg):
            if progress_cb:
                progress_cb(f"[{login}] {msg}")

        sess = self.session_path(account_id)
        if not sess.exists():
            return {"success": False, "message": "Нет сессии. Сначала войдите в аккаунт."}

        with open(sess) as f:
            storage = json.load(f)

        proxy_config = None
        if acc.get("proxy"):
            proxy_config = {"server": acc["proxy"]}

        settings = self.db.get_all_settings()
        headless = settings.get("headless_browser", "0") == "1"

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
                proxy=proxy_config,
            )

            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="en-US",
                timezone_id="America/New_York",
                storage_state=storage,
            )

            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.chrome = { runtime: {} };
            """)

            page = await context.new_page()

            try:
                log("Открываю страницу загрузки...")
                await page.goto(
                    "https://www.tiktok.com/upload",
                    wait_until="domcontentloaded",
                    timeout=30000,
                )
                await page.wait_for_timeout(random.uniform(2000, 3500))

                # Проверяем что залогинены
                if "login" in page.url:
                    await browser.close()
                    return {"success": False, "message": "Сессия истекла. Войдите заново."}

                log("Загружаю видеофайл...")
                file_input = await page.wait_for_selector(
                    'input[type="file"]', timeout=15000
                )
                await file_input.set_input_files(video["file_path"])
                await page.wait_for_timeout(random.uniform(3000, 5000))

                # Ждём загрузки видео
                log("Жду обработки видео...")
                try:
                    await page.wait_for_selector(
                        '[class*="upload-progress"][class*="100"], '
                        '[class*="video-info"], '
                        '[data-e2e="upload-desc"]',
                        timeout=60000,
                    )
                except PWTimeout:
                    log("Видео загружается медленно, продолжаю...")

                await page.wait_for_timeout(random.uniform(2000, 3000))

                # Заполняем описание
                caption = video.get("caption", "")
                hashtags = video.get("hashtags", "")
                full_caption = f"{caption} {hashtags}".strip()

                if full_caption:
                    log("Заполняю описание...")
                    desc_sel = (
                        '[data-e2e="upload-desc"], '
                        '[class*="caption-input"], '
                        'div[contenteditable="true"]'
                    )
                    try:
                        desc = await page.wait_for_selector(desc_sel, timeout=10000)
                        await desc.click()
                        await page.wait_for_timeout(500)
                        # Очищаем и вводим
                        await page.keyboard.press("Control+a")
                        await page.keyboard.press("Delete")
                        await page.wait_for_timeout(300)
                        for char in full_caption:
                            await page.keyboard.type(char, delay=random.uniform(30, 80))
                        await page.wait_for_timeout(random.uniform(800, 1500))
                    except Exception as e:
                        log(f"Не удалось заполнить описание: {e}")

                # Нажимаем "Опубликовать"
                log("Публикую...")
                post_btn_sel = (
                    'button[data-e2e="post-button"], '
                    'button[class*="post-btn"], '
                    'button:has-text("Post"), '
                    'button:has-text("Опубликовать")'
                )
                post_btn = await page.wait_for_selector(post_btn_sel, timeout=15000)
                await page.wait_for_timeout(random.uniform(500, 1000))
                await post_btn.click()

                log("Жду подтверждения публикации...")
                try:
                    await page.wait_for_url(
                        "**/profile**",
                        timeout=30000,
                    )
                    log("Видео опубликовано!")
                    await browser.close()
                    return {"success": True, "message": "Опубликовано", "tiktok_video_id": ""}
                except PWTimeout:
                    # Проверяем альтернативные признаки успеха
                    success_sel = '[class*="success"], [data-e2e="upload-success"]'
                    ok = await page.query_selector(success_sel)
                    if ok:
                        log("Видео опубликовано!")
                        await browser.close()
                        return {"success": True, "message": "Опубликовано", "tiktok_video_id": ""}

                    await browser.close()
                    return {"success": False, "message": "Не удалось подтвердить публикацию"}

            except Exception as e:
                log(f"Ошибка: {e}")
                await browser.close()
                return {"success": False, "message": str(e)}

    async def post_batch(self, tasks: list[dict], progress_cb=None) -> list[dict]:
        """
        tasks = [{"account_id": int, "video_id": int}, ...]
        Постит последовательно с задержками между аккаунтами.
        """
        results = []
        settings = self.db.get_all_settings()
        delay_min = int(settings.get("random_delay_min", "2"))
        delay_max = int(settings.get("random_delay_max", "8"))

        for task in tasks:
            acc_id = task["account_id"]
            vid_id = task["video_id"]

            result = await self.post_video(acc_id, vid_id, progress_cb)
            result["account_id"] = acc_id
            result["video_id"] = vid_id
            results.append(result)

            # Обновляем статус видео в БД
            if result["success"]:
                self.db.update_video_status(vid_id, "posted", result.get("tiktok_video_id", ""))
            else:
                self.db.update_video_status(vid_id, "failed")

            delay = random.uniform(delay_min * 10, delay_max * 10)
            if progress_cb:
                progress_cb(f"Пауза {delay:.0f}с перед следующим...")
            await asyncio.sleep(delay)

        return results
