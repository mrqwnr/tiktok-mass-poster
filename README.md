# TikTok Mass Poster

Десктопное приложение для массового постинга в TikTok через множество аккаунтов.

## Запуск

```bash
pip install -r requirements.txt
playwright install chromium
python main.py
```

## Формат файла аккаунтов (TXT)

Каждый аккаунт — две строки подряд: **юзернейм** и **пароль**.  
Пустые строки игнорируются.

```
username1
password1
username2
password2
username3
password3
```

> Вход выполняется по юзернейму — без кода подтверждения по SMS/email.

## Стек

- Python 3.11+, PyQt6
- Playwright (Chromium)
- SQLite
- DeepSeek API (AI-хэштеги и описания)
- python-telegram-bot

## Структура

```
main.py              — точка входа
db/database.py       — SQLite база
core/
  account_manager.py — вход в аккаунты
  poster.py          — публикация видео
  ai_helper.py       — DeepSeek AI
ui/
  main_window.py     — главное окно
  dashboard.py       — статистика
  accounts_page.py   — управление аккаунтами
  posting_page.py    — постинг
  settings_page.py   — настройки
  styles.py          — стили
data/
  sessions/          — сохранённые сессии браузера
assets/
  DMSans.ttf         — шрифт (скачать отдельно)
```
