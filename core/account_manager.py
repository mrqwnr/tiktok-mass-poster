import asyncio
import json
import os
import random
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

SESSIONS_DIR = Path("data/sessions")
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


class AccountManager:
    def __init__(self, db):
        self.db = db

    # ------------------------------------------------------------------ #
    #  Import                                                              #
    # ------------------------------------------------------------------ #

    def import_from_txt(self, filepath: str) -> list[tuple[str, str]]:
        """
        Формат файла:
            username1
            password1
            username2
            password2
            ...
        Пустые строки игнорируются.
        """
        accounts = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
            if len(lines) % 2 != 0:
                raise ValueError(
                    f"Нечётное количество строк ({len(lines)}). "
                    "Файл должен содержать пары: юзернейм / пароль."
                )
            for i in range(0, len(lines), 2):
                accounts.append((lines[i], lines[i + 1]))
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Не удалось прочитать файл: {e}")
        return accounts

    def save_imported_accounts(self, accounts: list[tuple[str, str]]) -> int:
        count = 0
        for login, password in accounts:
            self.db.add_account(login, password)
            count += 1
        return count

    # ------------------------------------------------------------------ #
    #  Session helpers                                                     #
    # ------------------------------------------------------------------ #

    def session_path(self, account_id: int) -> Path:
        return SESSIONS_DIR / f"account_{account_id}.json"

    async def _save_session(self, context, account_id: int):
        storage = await context.storage_state()
        with open(self.session_path(account_id), "w") as f:
            json.dump(storage, f)

    async def _stealth(self, page):
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins',   { get: () => [1, 2, 3] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

    async def _human_type(self, page, selector: str, text: str):
        await page.click(selector)
        await page.wait_for_timeout(random.uniform(200, 500))
        for char in text:
            await page.type(selector, char, delay=random.uniform(60, 160))

    async def _is_logged_in(self, page) -> bool:
        try:
            for sel in [
                '[data-e2e="profile-icon"]',
                '[data-e2e="nav-profile"]',
                '[data-e2e="upload-icon"]',
                'a[href*="/profile"]',
            ]:
                if await page.query_selector(sel):
                    return True
            if "/foryou" in page.url or "/following" in page.url:
                if not await page.query_selector('input[type="password"]'):
                    return True
        except Exception:
            pass
        return False

    # ------------------------------------------------------------------ #
    #  Login — только по юзернейму                                        #
    # ------------------------------------------------------------------ #

    async def login_account(self, account_id: int, progress_cb=None) -> dict:
        acc = dict(self.db.get_account(account_id))
        login    = acc["login"]
        password = acc["password"]
        proxy    = acc.get("proxy", "")

        def log(msg):
            if progress_cb:
                progress_cb(f"[{login}] {msg}")

        proxy_config = {"server": proxy} if proxy else None

        settings  = self.db.get_all_settings()
        headless  = settings.get("headless_browser", "0") == "1"

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

            ctx_args = {
                "viewport":    {"width": 1280, "height": 800},
                "user_agent":  (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "locale":      "en-US",
                "timezone_id": "America/New_York",
            }

            # Пробуем восстановить сессию
            sess = self.session_path(account_id)
            if sess.exists():
                log("Восстанавливаю сессию...")
                try:
                    with open(sess) as f:
                        storage = json.load(f)
                    ctx  = await browser.new_context(**ctx_args, storage_state=storage)
                    page = await ctx.new_page()
                    await self._stealth(page)
                    await page.goto("https://www.tiktok.com/foryou",
                                    wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(3000)
                    if await self._is_logged_in(page):
                        log("Сессия активна.")
                        await self._save_session(ctx, account_id)
                        await browser.close()
                        self.db.update_account_status(account_id, "active")
                        return {"success": True, "status": "active",
                                "message": "Сессия восстановлена",
                                "account_id": account_id, "login": login}
                    log("Сессия истекла, вхожу заново...")
                    await ctx.close()
                except Exception as e:
                    log(f"Ошибка восстановления сессии: {e}")

            # Свежий вход
            ctx  = await browser.new_context(**ctx_args)
            page = await ctx.new_page()
            await self._stealth(page)

            try:
                result = await self._do_login_by_username(page, login, password, log)
            except Exception as e:
                log(f"Ошибка входа: {e}")
                await browser.close()
                self.db.update_account_status(account_id, "failed")
                return {"success": False, "status": "failed", "message": str(e),
                        "account_id": account_id, "login": login}

            if result["success"]:
                await self._save_session(ctx, account_id)
                self.db.update_account_status(account_id, "active")
            else:
                self.db.update_account_status(account_id, result["status"])

            await browser.close()
            result["account_id"] = account_id
            result["login"]      = login
            return result

    async def _do_login_by_username(self, page, username: str, password: str, log) -> dict:
        """
        Вход через юзернейм — не требует кода подтверждения.
        URL: /login/phone-or-email/email  → переключаемся на вкладку "Use phone / username"
        """
        log("Открываю страницу входа...")
        await page.goto(
            "https://www.tiktok.com/login/phone-or-email/email",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        await page.wait_for_timeout(random.uniform(1500, 2500))

        # Переключаемся на вкладку "Использовать юзернейм"
        log("Переключаюсь на вход по юзернейму...")
        username_tab_selectors = [
            'a:has-text("Use phone / username")',
            'a:has-text("username")',
            '[data-e2e="username-tab"]',
            'a[href*="username"]',
        ]
        switched = False
        for sel in username_tab_selectors:
            try:
                el = await page.wait_for_selector(sel, timeout=5000)
                if el:
                    await el.click()
                    await page.wait_for_timeout(random.uniform(800, 1500))
                    switched = True
                    break
            except Exception:
                continue

        if not switched:
            # Пробуем прямой URL для входа по юзернейму
            log("Пробую прямой URL для юзернейма...")
            await page.goto(
                "https://www.tiktok.com/login/phone-or-email/username",
                wait_until="domcontentloaded",
                timeout=20000,
            )
            await page.wait_for_timeout(random.uniform(1000, 2000))

        # Поле юзернейма
        log("Ввожу юзернейм...")
        user_sel = (
            'input[name="username"], ' 
            'input[placeholder*="username" i], '
            'input[placeholder*="юзернейм" i], '
            'input[autocomplete="username"], '
            'input[type="text"]' 
        )
        await page.wait_for_selector(user_sel, timeout=15000)
        await self._human_type(page, user_sel, username)
        await page.wait_for_timeout(random.uniform(600, 1200))

        # Поле пароля
        log("Ввожу пароль...")
        pass_sel = 'input[type="password"]'
        await page.wait_for_selector(pass_sel, timeout=10000)
        await self._human_type(page, pass_sel, password)
        await page.wait_for_timeout(random.uniform(800, 1500))

        # Кнопка входа
        log("Нажимаю войти...")
        btn_sel = (
            'button[type="submit"], '
            'button[data-e2e="login-button"], '
            'button:has-text("Log in"), '
            'button:has-text("Войти")' 
        )
        await page.click(btn_sel)
        await page.wait_for_timeout(4000)

        log(f"URL после входа: {page.url}")

        # Капча
        if "captcha" in page.url or await page.query_selector('[id*="captcha"], [class*="captcha"]'):
            log("Обнаружена капча — жду решения (до 90 сек)...")
            try:
                await page.wait_for_url("**/foryou**", timeout=90000)
            except PlaywrightTimeout:
                return {"success": False, "status": "captcha",
                        "message": "Капча не решена вовремя"}

        await page.wait_for_timeout(2000)

        if await self._is_logged_in(page):
            log("Вход выполнен успешно!")
            return {"success": True, "status": "active", "message": "Вошёл"}

        # Сообщение об ошибке от TikTok
        err_el = await page.query_selector(
            '[class*="error"], [class*="warning"], [data-e2e*="error"]' 
        )
        if err_el:
            err_text = (await err_el.inner_text()).strip()
            return {"success": False, "status": "failed", "message": err_text}

        return {"success": False, "status": "failed",
                "message": "Вход не выполнен — неизвестная причина"}

    # ------------------------------------------------------------------ #
    #  Batch                                                               #
    # ------------------------------------------------------------------ #

    async def login_all(self, progress_cb=None) -> list[dict]:
        accounts = self.db.get_all_accounts()
        results  = []
        for acc in accounts:
            result = await self.login_account(acc["id"], progress_cb)
            results.append(result)
            delay = random.uniform(5, 12)
            if progress_cb:
                progress_cb(f"Пауза {delay:.1f}с...")
            await asyncio.sleep(delay)
        return results
