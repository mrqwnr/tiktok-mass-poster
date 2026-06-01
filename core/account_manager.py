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
        """Read LOGIN\nPASSWORD\n... pairs from a text file."""
        accounts = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
            if len(lines) % 2 != 0:
                raise ValueError("File must have an even number of lines (login + password pairs).")
            for i in range(0, len(lines), 2):
                accounts.append((lines[i], lines[i + 1]))
        except Exception as e:
            raise ValueError(f"Failed to read file: {e}")
        return accounts

    def save_imported_accounts(self, accounts: list[tuple[str, str]]) -> int:
        count = 0
        for login, password in accounts:
            self.db.add_account(login, password)
            count += 1
        return count

    # ------------------------------------------------------------------ #
    #  Login                                                               #
    # ------------------------------------------------------------------ #

    def session_path(self, account_id: int) -> Path:
        return SESSIONS_DIR / f"account_{account_id}.json"

    async def login_account(self, account_id: int, progress_cb=None) -> dict:
        """
        Log in to TikTok for a single account.
        Saves browser session (cookies + storage) to disk.
        Returns: {success, status, message, account_id, login}
        """
        acc = dict(self.db.get_account(account_id))
        login = acc["login"]
        password = acc["password"]
        proxy = acc.get("proxy", "")

        def log(msg):
            if progress_cb:
                progress_cb(f"[{login}] {msg}")

        log("Starting login...")

        proxy_config = None
        if proxy:
            proxy_config = {"server": proxy}

        async with async_playwright() as p:
            settings = self.db.get_all_settings()
            headless = settings.get("headless_browser", "0") == "1"

            browser = await p.chromium.launch(
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
                proxy=proxy_config,
            )

            context_args = {
                "viewport": {"width": 1280, "height": 800},
                "user_agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "locale": "en-US",
                "timezone_id": "America/New_York",
            }

            # Restore existing session if available
            sess = self.session_path(account_id)
            if sess.exists():
                log("Restoring saved session...")
                try:
                    with open(sess) as f:
                        storage = json.load(f)
                    context = await browser.new_context(
                        **context_args,
                        storage_state=storage,
                    )
                    page = await context.new_page()
                    await self._stealth(page)
                    await page.goto("https://www.tiktok.com/foryou", wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(3000)

                    if await self._is_logged_in(page):
                        log("Session valid — already logged in.")
                        await self._save_session(context, account_id)
                        await browser.close()
                        self.db.update_account_status(account_id, "active")
                        return {"success": True, "status": "active", "message": "Session restored", "account_id": account_id, "login": login}
                    else:
                        log("Session expired, re-logging in...")
                        await context.close()
                except Exception as e:
                    log(f"Session restore failed: {e}")

            # Fresh login
            context = await browser.new_context(**context_args)
            page = await context.new_page()
            await self._stealth(page)

            try:
                result = await self._do_login(page, login, password, log)
            except Exception as e:
                log(f"Login error: {e}")
                await browser.close()
                self.db.update_account_status(account_id, "failed")
                return {"success": False, "status": "failed", "message": str(e), "account_id": account_id, "login": login}

            if result["success"]:
                await self._save_session(context, account_id)
                self.db.update_account_status(account_id, "active")
            else:
                self.db.update_account_status(account_id, result["status"])

            await browser.close()
            result["account_id"] = account_id
            result["login"] = login
            return result

    async def _do_login(self, page, login: str, password: str, log) -> dict:
        """Navigate TikTok login flow."""
        await page.goto(
            "https://www.tiktok.com/login/phone-or-email/email",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        await page.wait_for_timeout(random.uniform(1500, 2500))

        # Fill email/username
        log("Filling credentials...")
        email_sel = 'input[name="username"], input[placeholder*="email"], input[type="text"]'
        await page.wait_for_selector(email_sel, timeout=15000)
        await self._human_type(page, email_sel, login)
        await page.wait_for_timeout(random.uniform(600, 1200))

        # Fill password
        pass_sel = 'input[type="password"]'
        await page.wait_for_selector(pass_sel, timeout=10000)
        await self._human_type(page, pass_sel, password)
        await page.wait_for_timeout(random.uniform(800, 1500))

        # Click login button
        log("Submitting...")
        login_btn = 'button[type="submit"], button[data-e2e="login-button"]'
        await page.click(login_btn)
        await page.wait_for_timeout(4000)

        # Check result
        url = page.url
        log(f"After submit URL: {url}")

        # Captcha
        if "captcha" in url or await page.query_selector('[id*="captcha"], [class*="captcha"]'):
            log("Captcha detected — waiting up to 60s for manual solve...")
            self.db.update_account_status(
                self.db.get_account_id_by_login(login) if hasattr(self.db, "get_account_id_by_login") else 0,
                "captcha"
            )
            try:
                await page.wait_for_url("**/foryou**", timeout=60000)
            except PlaywrightTimeout:
                return {"success": False, "status": "captcha", "message": "Captcha not solved in time"}

        # Verify login
        await page.wait_for_timeout(2000)
        if await self._is_logged_in(page):
            log("Login successful!")
            return {"success": True, "status": "active", "message": "Logged in"}

        # Wrong password / error message
        err_sel = '[class*="error"], [class*="warning"], [data-e2e*="error"]'
        err_el = await page.query_selector(err_sel)
        if err_el:
            err_text = await err_el.inner_text()
            return {"success": False, "status": "failed", "message": err_text.strip()}

        return {"success": False, "status": "failed", "message": "Login failed — unknown reason"}

    async def _is_logged_in(self, page) -> bool:
        """Check if current page shows a logged-in TikTok session."""
        try:
            # Logged-in indicators
            indicators = [
                '[data-e2e="profile-icon"]',
                '[data-e2e="nav-profile"]',
                'a[href*="/profile"]',
                '[class*="avatar"]',
            ]
            for sel in indicators:
                el = await page.query_selector(sel)
                if el:
                    return True
            # URL check
            if "/foryou" in page.url or "/following" in page.url:
                # Make sure login page is not showing
                login_el = await page.query_selector('input[type="password"]')
                if not login_el:
                    return True
        except Exception:
            pass
        return False

    async def _human_type(self, page, selector: str, text: str):
        """Type text character by character with random delays."""
        await page.click(selector)
        await page.wait_for_timeout(random.uniform(200, 500))
        for char in text:
            await page.type(selector, char, delay=random.uniform(60, 180))

    async def _stealth(self, page):
        """Inject basic anti-detection JS."""
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

    async def _save_session(self, context, account_id: int):
        """Save browser cookies + localStorage to disk."""
        storage = await context.storage_state()
        with open(self.session_path(account_id), "w") as f:
            json.dump(storage, f)

    # ------------------------------------------------------------------ #
    #  Batch login                                                         #
    # ------------------------------------------------------------------ #

    async def login_all(self, progress_cb=None) -> list[dict]:
        accounts = self.db.get_all_accounts()
        results = []
        for acc in accounts:
            result = await self.login_account(acc["id"], progress_cb)
            results.append(result)
            delay = random.uniform(4, 10)
            if progress_cb:
                progress_cb(f"Waiting {delay:.1f}s before next account...")
            await asyncio.sleep(delay)
        return results
