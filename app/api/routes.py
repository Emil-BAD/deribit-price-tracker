from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import PriceOut
from app.core.database import get_session
from app.models.price import Price

router = APIRouter()


def _to_unix(dt: datetime) -> int:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


@router.get("/prices", response_model=list[PriceOut])
async def get_prices(
    ticker: str = Query(..., min_length=1),
    session: AsyncSession = Depends(get_session),
) -> list[PriceOut]:
    result = await session.execute(
        select(Price).where(Price.ticker == ticker).order_by(Price.ts_unix.desc())
    )
    rows = result.scalars().all()
    return [PriceOut(ticker=row.ticker, price=float(row.price), ts_unix=row.ts_unix) for row in rows]


@router.get("/prices/latest", response_model=PriceOut)
async def get_latest_price(
    ticker: str = Query(..., min_length=1),
    session: AsyncSession = Depends(get_session),
) -> PriceOut:
    result = await session.execute(
        select(Price).where(Price.ticker == ticker).order_by(Price.ts_unix.desc()).limit(1)
    )
    row = result.scalars().first()
    if row is None:
        raise HTTPException(status_code=404, detail="No data for ticker")
    return PriceOut(ticker=row.ticker, price=float(row.price), ts_unix=row.ts_unix)


@router.get("/prices/by-date", response_model=list[PriceOut])
async def get_prices_by_date(
    ticker: str = Query(..., min_length=1),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> list[PriceOut]:
    if date_from is None and date_to is None:
        raise HTTPException(status_code=400, detail="date_from or date_to is required")
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from must be <= date_to")

    conditions = [Price.ticker == ticker]
    if date_from is not None:
        conditions.append(Price.ts_unix >= _to_unix(date_from))
    if date_to is not None:
        conditions.append(Price.ts_unix <= _to_unix(date_to))

    result = await session.execute(select(Price).where(*conditions).order_by(Price.ts_unix.desc()))
    rows = result.scalars().all()
    return [PriceOut(ticker=row.ticker, price=float(row.price), ts_unix=row.ts_unix) for row in rows]
