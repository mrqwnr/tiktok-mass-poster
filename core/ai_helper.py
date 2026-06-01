import requests
import json
import random

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

class AIHelper:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _chat(self, prompt: str, max_tokens: int = 500) -> str:
        if not self.api_key:
            raise ValueError("DeepSeek API key not set")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.8
        }
        resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

    def generate_hashtags(self, niche: str, target_audience: str, count: int = 10) -> list:
        prompt = f"""Generate {count} TikTok hashtags for:
Niche: {niche}
Target audience: {target_audience}

Rules:
- Mix popular and niche hashtags
- No spaces in hashtags
- Return ONLY hashtags separated by spaces, nothing else
- Include # symbol"""
        result = self._chat(prompt, max_tokens=200)
        tags = [t.strip() for t in result.split() if t.startswith("#")]
        return tags[:count]

    def rephrase_caption(self, original_text: str) -> str:
        prompt = f"""Rephrase this TikTok caption. Keep the same meaning but use different words. 
Make it engaging and natural. Keep it short (under 150 chars).
Original: {original_text}
Return ONLY the rephrased caption, nothing else."""
        return self._chat(prompt, max_tokens=100)

    def generate_profile(self) -> dict:
        prompt = """Generate a realistic human TikTok profile. Return JSON only:
{
  "username": "realistic_username_no_spaces",
  "display_name": "Real Looking Name",
  "bio": "Short bio under 80 chars, casual tone"
}
Make it look like a real person, not a bot."""
        result = self._chat(prompt, max_tokens=150)
        try:
            start = result.find("{")
            end = result.rfind("}") + 1
            return json.loads(result[start:end])
        except Exception:
            return {
                "username": f"user_{random.randint(1000, 9999)}",
                "display_name": "User",
                "bio": "Just vibing 🎵"
            }

    def generate_post_schedule(self, posts_per_day: int, interval_min: int, interval_max: int) -> list:
        prompt = f"""Generate a realistic TikTok posting schedule for {posts_per_day} posts per day.
Post interval: {interval_min}-{interval_max} minutes between posts.
Return ONLY a JSON array of times in HH:MM format, e.g. ["09:00", "13:30", "18:00"]
Make times realistic for human behavior (not too early, not too late)."""
        result = self._chat(prompt, max_tokens=100)
        try:
            start = result.find("[")
            end = result.rfind("]") + 1
            return json.loads(result[start:end])
        except Exception:
            return ["09:00", "13:00", "18:00"][:posts_per_day]
