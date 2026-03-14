from celery import Celery

from app.core.config import get_settings

celery_app = Celery("deribit_price_tracker")


def _configure_celery() -> None:
    settings = get_settings()
    celery_app.conf.broker_url = settings.celery_broker_url
    celery_app.conf.result_backend = settings.celery_result_backend
    celery_app.conf.timezone = "UTC"
    celery_app.conf.imports = ("app.services.price_tasks",)
    celery_app.conf.beat_schedule = {
        "fetch-index-prices-every-minute": {
            "task": "app.services.price_tasks.fetch_index_prices",
            "schedule": 60.0,
        }
    }


_configure_celery()
