import asyncio
import time
from typing import Iterable, Mapping

import httpx


class DeribitClient:
    def __init__(
        self,
        base_url: str = "https://www.deribit.com/api/v2",
        timeout: float = 10.0,
        client: httpx.AsyncClient | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = client
        self._owns_client = client is None
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token: str | None = None
        self._token_expires_at: float | None = None

    async def __aenter__(self) -> "DeribitClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)
        return self._client

    async def get_index_price(self, index_name: str) -> float:
        if not index_name:
            raise ValueError("index_name must be non-empty")

        client = await self._get_client()
        response = await client.get("public/get_index_price", params={"index_name": index_name})
        response.raise_for_status()
        data = response.json()

        try:
            price = data["result"]["index_price"]
        except (KeyError, TypeError) as exc:
            raise ValueError("Unexpected response format from Deribit") from exc

        if not isinstance(price, (int, float)):
            raise ValueError("Invalid price type in Deribit response")

        return float(price)

    async def get_index_prices(self, index_names: Iterable[str]) -> Mapping[str, float]:
        names = [name for name in index_names if name]
        if not names:
            raise ValueError("index_names must contain at least one name")

        tasks = [self.get_index_price(name) for name in names]
        prices = await asyncio.gather(*tasks)
        return dict(zip(names, prices))

    async def authenticate(self) -> str:
        if not self._client_id or not self._client_secret:
            raise ValueError("client_id and client_secret are required for authentication")

        client = await self._get_client()
        response = await client.get(
            "public/auth",
            params={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
        )
        response.raise_for_status()
        data = response.json()
        try:
            token = data["result"]["access_token"]
            expires_in = data["result"]["expires_in"]
        except (KeyError, TypeError) as exc:
            raise ValueError("Unexpected auth response format from Deribit") from exc

        if not isinstance(token, str) or not token:
            raise ValueError("Invalid access token in Deribit response")
        if not isinstance(expires_in, (int, float)) or expires_in <= 0:
            raise ValueError("Invalid expires_in in Deribit response")

        self._access_token = token
        self._token_expires_at = time.time() + float(expires_in) - 30.0
        return token

    async def _get_access_token(self) -> str:
        if self._access_token and self._token_expires_at and time.time() < self._token_expires_at:
            return self._access_token
        return await self.authenticate()

    async def get_account_summary(self, currency: str) -> dict:
        if not currency:
            raise ValueError("currency must be non-empty")

        token = await self._get_access_token()
        client = await self._get_client()
        response = await client.get(
            "private/get_account_summary",
            params={"currency": currency},
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        data = response.json()
        try:
            return data["result"]
        except (KeyError, TypeError) as exc:
            raise ValueError("Unexpected account summary response format from Deribit") from exc
