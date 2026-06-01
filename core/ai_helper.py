import aiohttp
import json


class AIHelper:
    def __init__(self, db):
        self.db = db

    def _get_api_key(self) -> str:
        key = self.db.get_setting("deepseek_api_key", "")
        if not key:
            raise ValueError("DeepSeek API ключ не задан. Укажите его в Настройках.")
        return key

    async def _ask(self, prompt: str) -> str:
        api_key = self._get_api_key()
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 300,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise ValueError(f"DeepSeek API ошибка {resp.status}: {text[:200]}")
                data = await resp.json()
                return data["choices"][0]["message"]["content"].strip()

    async def generate_caption(self, niche: str = "", audience: str = "") -> str:
        niche_str = niche or "общая тематика"
        audience_str = audience or "широкая аудитория"
        prompt = (
            f"Напиши короткое цепляющее описание для TikTok видео. "
            f"Ниша: {niche_str}. Целевая аудитория: {audience_str}. "
            f"Максимум 2 предложения. Только текст, без хэштегов."
        )
        return await self._ask(prompt)

    async def generate_hashtags(self, niche: str = "", audience: str = "", count: int = 10) -> str:
        niche_str = niche or "общая тематика"
        audience_str = audience or "широкая аудитория"
        prompt = (
            f"Дай {count} релевантных хэштегов для TikTok. "
            f"Ниша: {niche_str}. Аудитория: {audience_str}. "
            f"Формат: #хэштег1 #хэштег2 ... Только хэштеги, ничего лишнего."
        )
        return await self._ask(prompt)

    async def generate_profile(self, niche: str = "", audience: str = "") -> dict:
        niche_str = niche or "общая тематика"
        prompt = (
            f"Придумай профиль TikTok аккаунта для ниши: {niche_str}. "
            f"Верни JSON с полями: display_name (имя), bio (описание профиля до 80 символов). "
            f"Только JSON, без пояснений."
        )
        raw = await self._ask(prompt)
        try:
            raw = raw.strip().strip("```json").strip("```").strip()
            return json.loads(raw)
        except Exception:
            return {"display_name": "", "bio": raw}
