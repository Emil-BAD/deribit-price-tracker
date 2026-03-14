from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import get_session
from app.main import app
from app.models.base import Base
from app.models.price import Price

Price.__table__.c.id.autoincrement = True


@pytest_asyncio.fixture()
async def test_session_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield SessionLocal
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def client(test_session_factory):
    async def override_get_session():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


async def _seed_prices(session_factory):
    now = int(datetime(2026, 3, 14, 12, 0, tzinfo=timezone.utc).timestamp())
    async with session_factory() as session:
        session.add_all(
            [
                Price(id=1, ticker="btc_usd", price=100.0, ts_unix=now - 120),
                Price(id=2, ticker="btc_usd", price=110.0, ts_unix=now - 60),
                Price(id=3, ticker="btc_usd", price=120.0, ts_unix=now),
                Price(id=4, ticker="eth_usd", price=200.0, ts_unix=now),
            ]
        )
        await session.commit()
    return now


@pytest.mark.asyncio
async def test_get_prices(client, test_session_factory):
    await _seed_prices(test_session_factory)
    resp = await client.get("/prices", params={"ticker": "btc_usd"})
    assert resp.status_code == 200
    data = resp.json()
    assert [item["price"] for item in data][:3] == [120.0, 110.0, 100.0]


@pytest.mark.asyncio
async def test_get_latest_price(client, test_session_factory):
    await _seed_prices(test_session_factory)
    resp = await client.get("/prices/latest", params={"ticker": "btc_usd"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["price"] == 120.0


@pytest.mark.asyncio
async def test_get_prices_by_date_range(client, test_session_factory):
    now = await _seed_prices(test_session_factory)
    date_from = datetime.fromtimestamp(now - 90, tz=timezone.utc).isoformat()
    date_to = datetime.fromtimestamp(now - 30, tz=timezone.utc).isoformat()
    resp = await client.get(
        "/prices/by-date",
        params={"ticker": "btc_usd", "date_from": date_from, "date_to": date_to},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert [item["price"] for item in data] == [110.0]


@pytest.mark.asyncio
async def test_get_prices_by_date_missing_filters(client):
    resp = await client.get("/prices/by-date", params={"ticker": "btc_usd"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_get_prices_by_date_invalid_range(client):
    resp = await client.get(
        "/prices/by-date",
        params={
            "ticker": "btc_usd",
            "date_from": "2026-03-14T12:00:00Z",
            "date_to": "2026-03-13T12:00:00Z",
        },
    )
    assert resp.status_code == 400
