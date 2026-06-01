# TikTok Mass Poster

Десктопное приложение для массового постинга в TikTok через множество аккаунтов.

## Стек
- Python 3.11+
- PyQt6 (UI)
- Playwright (автоматизация TikTok)
- FFmpeg + MoviePy (монтаж видео)
- SQLite (локальная БД)
- DeepSeek API (хэштеги, перефраз, генерация профилей)
- python-telegram-bot (отчёты)

## Установка

```bash
pip install -r requirements.txt
playwright install chromium
```

## Запуск

```bash
python main.py
```
