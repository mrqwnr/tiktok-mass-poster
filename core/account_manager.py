import asyncio
import random
from playwright.async_api import async_playwright

class AccountManager:
    """Manages TikTok account login and session handling."""

    def __init__(self, db):
        self.db = db
        self.sessions = {}  # account_id -> browser context

    async def login_account(self, account_id: int, progress_callback=None) -> dict:
        """
        Attempt to log in to TikTok with given account credentials.
        Returns: {"success": bool, "status": str, "message": str}
        """
        account = self.db.get_account(account_id)
        if not account:
            return {"success": False, "status": "error", "message": "Account not found"}

        login = account["login"]
        password = account["password"]
        proxy = account["proxy"]

        proxy_config = None
        if proxy:
            proxy_config = {"server": proxy}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False,
                    proxy=proxy_config,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720},
                    locale="en-US"
                )
                page = await context.new_page()

                if progress_callback:
                    progress_callback(f"Открываю TikTok для {login}...")

                await page.goto("https://www.tiktok.com/login/phone-or-email/email", wait_until="networkidle")
                await asyncio.sleep(random.uniform(2, 4))

                # Fill email
                await page.fill('input[name="username"]', login)
                await asyncio.sleep(random.uniform(0.5, 1.5))

                # Fill password
                await page.fill('input[type="password"]', password)
                await asyncio.sleep(random.uniform(0.5, 1.5))

                # Click login
                await page.click('button[type="submit"]')
                await asyncio.sleep(random.uniform(3, 6))

                # Check result
                current_url = page.url
                if "tiktok.com/foryou" in current_url or "tiktok.com/@" in current_url:
                    self.db.update_account(account_id, status="active")
                    await browser.close()
                    return {"success": True, "status": "active", "message": "Успешный вход"}

                # Check for captcha
                if "captcha" in await page.content():
                    await browser.close()
                    return {"success": False, "status": "captcha", "message": "Требуется капча"}

                # Check for email verification
                if "verify" in current_url or "code" in await page.content():
                    await browser.close()
                    return {"success": False, "status": "verify", "message": "Требуется код подтверждения"}

                await browser.close()
                return {"success": False, "status": "failed", "message": "Не удалось войти"}

        except Exception as e:
            return {"success": False, "status": "error", "message": str(e)}

    async def login_all(self, progress_callback=None) -> list:
        """Login all accounts and return results."""
        accounts = self.db.get_all_accounts()
        results = []
        for acc in accounts:
            result = await self.login_account(acc["id"], progress_callback)
            result["account_id"] = acc["id"]
            result["login"] = acc["login"]
            results.append(result)
            await asyncio.sleep(random.uniform(3, 8))
        return results

    def import_from_txt(self, filepath: str) -> list:
        """
        Import accounts from txt file.
        Format: LOGIN\nPASSWORD\nLOGIN\nPASSWORD...
        Returns list of (login, password) tuples.
        """
        accounts = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
            for i in range(0, len(lines) - 1, 2):
                login = lines[i]
                password = lines[i + 1]
                accounts.append((login, password))
        except Exception as e:
            raise ValueError(f"Ошибка чтения файла: {e}")
        return accounts

    def save_imported_accounts(self, accounts: list) -> int:
        """Save imported accounts to DB. Returns count added."""
        count = 0
        for login, password in accounts:
            self.db.add_account(login, password)
            count += 1
        return count
