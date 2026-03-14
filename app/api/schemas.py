from pydantic import BaseModel


class PriceOut(BaseModel):
    ticker: str
    price: float
    ts_unix: int
