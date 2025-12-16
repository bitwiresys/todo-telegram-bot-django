# ToDo + Telegram Bot

## Описание

Проект — ToDo-сервис с категориями и Telegram-ботом.

- Backend на Django/DRF хранит задачи и категории, привязанные к пользователю.
- Пользователь идентифицируется по `telegram_id` (заголовок `X-Telegram-Id`).
- У задач есть категория, дата создания и опциональный дедлайн.
- Celery периодически проверяет просроченные задачи и отправляет уведомления в Telegram.
- Telegram-бот (Aiogram + aiogram-dialog) показывает список задач (с категорией и датой создания) и позволяет добавлять задачи через диалог.

## Стек

- Django 5 + Django REST Framework
- PostgreSQL
- Celery + Redis
- Aiogram 3 + aiogram-dialog
- Docker + docker-compose

## Логика работы (кратко)

- Бот для каждого действия отправляет запросы в backend REST API.
- Перед CRUD-запросами бот вызывает `/api/users/ensure/`, чтобы убедиться что пользователь с данным `telegram_id` существует.
- Все CRUD эндпоинты работают в контексте пользователя из `X-Telegram-Id`.
- Первичные ключи основных сущностей — строковые, генерируются детерминированно через таблицу sequence с блокировкой строки в транзакции.

## Запуск и настройка

### Вариант 1: Docker (рекомендуется)

1) Создай `.env` на основе примера:

```bash
cp .env.example .env
```

2) Заполни в `.env`:

- `TELEGRAM_BOT_TOKEN` (выдаёт BotFather)

3) Запусти сервисы:

```bash
docker-compose up -d --build
```

Доступы:

- API: `http://localhost:8000/api/`
- Admin: `http://localhost:8000/admin/`

### Вариант 2: Локально (для разработки/проверок)

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -U pip
.\.venv\Scripts\python -m pip install -e ".[dev]"

.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m mypy .
.\.venv\Scripts\python -m pytest
```
