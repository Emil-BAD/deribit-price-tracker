import asyncio
import time

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.client.deribit_client import DeribitClient
from app.core.celery_app import celery_app
from app.core.config import get_settings
from app.models.price import Price


async def _fetch_and_store_prices() -> None:
    settings = get_settings()
    tickers = [t.strip() for t in settings.price_poll_tickers.split(",") if t.strip()]
    if not tickers:
        return

    async with DeribitClient(base_url=settings.deribit_base_url) as client:
        prices = await client.get_index_prices(tickers)

    ts_unix = int(time.time())
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with SessionLocal() as session:
        for ticker, price in prices.items():
            session.add(Price(ticker=ticker, price=price, ts_unix=ts_unix))
        await session.commit()
    await engine.dispose()


@celery_app.task(name="app.services.price_tasks.fetch_index_prices")
def fetch_index_prices() -> None:
    asyncio.run(_fetch_and_store_prices())
