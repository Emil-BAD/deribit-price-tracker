from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(..., alias="DATABASE_URL")
    celery_broker_url: str = Field(..., alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(..., alias="CELERY_RESULT_BACKEND")
    deribit_base_url: str = Field("https://www.deribit.com/api/v2", alias="DERIBIT_BASE_URL")
    price_poll_tickers: str = Field("btc_usd,eth_usd", alias="PRICE_POLL_TICKERS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
