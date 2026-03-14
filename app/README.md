# Deribit Price Tracker

Сервис каждую минуту получает индексные цены Deribit для `btc_usd` и `eth_usd`, сохраняет их в PostgreSQL и предоставляет FastAPI API для чтения истории и последней цены.

## Требования

- Docker + Docker Compose (рекомендуется)
- Или локально: Python 3.11+, PostgreSQL и Redis

## Быстрый старт (Docker)

```bash
cd app
docker compose up --build
```

Подожди около 1 минуты, затем проверь:

```bash
curl "http://localhost:8000/prices/latest?ticker=btc_usd"
```

## Конфигурация

- `DATABASE_URL` (обязательная)
- `CELERY_BROKER_URL` (обязательная)
- `CELERY_RESULT_BACKEND` (обязательная)
- `DERIBIT_BASE_URL` (по умолчанию `https://www.deribit.com/api/v2`)
- `PRICE_POLL_TICKERS` (по умолчанию `btc_usd,eth_usd`)

## API

Все методы `GET` и требуют query-параметр `ticker`.

- `GET /prices?ticker=btc_usd` - все цены по тикеру
- `GET /prices/latest?ticker=btc_usd` - последняя цена
- `GET /prices/by-date?ticker=btc_usd&date_from=2026-03-14T00:00:00Z&date_to=2026-03-14T23:59:59Z` - цены по датам

## Локальный запуск

```bash
pip install -r app/requirements.txt
pip install -r app/requirements-dev.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
celery -A app.core.celery_app worker -l info
celery -A app.core.celery_app beat -l info
```

## Тесты

```bash
python -m pytest app/tests -q
```

## Решения по дизайну

- Асинхронный HTTP и БД для неблокирующего IO.
- Celery для периодического сбора цен.
- UNIX timestamp для простой сортировки и фильтрации.
- Конфиг через переменные окружения.
