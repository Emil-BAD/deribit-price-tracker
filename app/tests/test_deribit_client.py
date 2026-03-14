import httpx
import pytest
import respx

from app.client.deribit_client import DeribitClient


@pytest.mark.asyncio
async def test_get_index_price_success():
    with respx.mock() as mock:
        mock.get(
            "https://test.deribit.com/api/v2/public/get_index_price",
            params={"index_name": "btc_usd"},
        ).respond(
            status_code=200,
            json={"result": {"index_price": 123.45}},
        )

        async with DeribitClient(base_url="https://test.deribit.com/api/v2") as client:
            price = await client.get_index_price("btc_usd")

        assert price == 123.45


@pytest.mark.asyncio
async def test_get_index_price_invalid_payload():
    with respx.mock() as mock:
        mock.get(
            "https://test.deribit.com/api/v2/public/get_index_price",
            params={"index_name": "btc_usd"},
        ).respond(
            status_code=200,
            json={"foo": "bar"},
        )

        async with DeribitClient(base_url="https://test.deribit.com/api/v2") as client:
            with pytest.raises(ValueError, match="Unexpected response format"):
                await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_get_index_price_http_error():
    with respx.mock() as mock:
        mock.get(
            "https://test.deribit.com/api/v2/public/get_index_price",
            params={"index_name": "btc_usd"},
        ).respond(
            status_code=500,
            json={},
        )

        async with DeribitClient(base_url="https://test.deribit.com/api/v2") as client:
            with pytest.raises(httpx.HTTPStatusError):
                await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_get_index_prices_multiple():
    with respx.mock() as mock:
        mock.get(
            "https://test.deribit.com/api/v2/public/get_index_price",
            params={"index_name": "btc_usd"},
        ).respond(
            status_code=200,
            json={"result": {"index_price": 111.0}},
        )
        mock.get(
            "https://test.deribit.com/api/v2/public/get_index_price",
            params={"index_name": "eth_usd"},
        ).respond(
            status_code=200,
            json={"result": {"index_price": 222.0}},
        )

        async with DeribitClient(base_url="https://test.deribit.com/api/v2") as client:
            prices = await client.get_index_prices(["btc_usd", "eth_usd"])

        assert prices == {"btc_usd": 111.0, "eth_usd": 222.0}

@pytest.mark.asyncio
async def test_authenticate_success():
    with respx.mock() as mock:
        mock.get(
            "https://test.deribit.com/api/v2/public/auth",
            params={
                "grant_type": "client_credentials",
                "client_id": "id",
                "client_secret": "secret",
            },
        ).respond(
            status_code=200,
            json={"result": {"access_token": "token", "expires_in": 10}},
        )

        async with DeribitClient(base_url="https://test.deribit.com/api/v2", client_id="id", client_secret="secret") as client:
            token = await client.authenticate()

        assert token == "token"


@pytest.mark.asyncio
async def test_authenticate_invalid_payload():
    with respx.mock() as mock:
        mock.get(
            "https://test.deribit.com/api/v2/public/auth",
            params={
                "grant_type": "client_credentials",
                "client_id": "id",
                "client_secret": "secret",
            },
        ).respond(
            status_code=200,
            json={"result": {}},
        )

        async with DeribitClient(base_url="https://test.deribit.com/api/v2", client_id="id", client_secret="secret") as client:
            with pytest.raises(ValueError, match="Unexpected auth response format"):
                await client.authenticate()


@pytest.mark.asyncio
async def test_authenticate_http_error():
    with respx.mock() as mock:
        mock.get(
            "https://test.deribit.com/api/v2/public/auth",
            params={
                "grant_type": "client_credentials",
                "client_id": "id",
                "client_secret": "secret",
            },
        ).respond(
            status_code=400,
            json={},
        )

        async with DeribitClient(base_url="https://test.deribit.com/api/v2", client_id="id", client_secret="secret") as client:
            with pytest.raises(httpx.HTTPStatusError):
                await client.authenticate()


@pytest.mark.asyncio
async def test_get_account_summary_success():
    with respx.mock() as mock:
        mock.get(
            "https://test.deribit.com/api/v2/public/auth",
            params={
                "grant_type": "client_credentials",
                "client_id": "id",
                "client_secret": "secret",
            },
        ).respond(
            status_code=200,
            json={"result": {"access_token": "token", "expires_in": 10}},
        )
        mock.get(
            "https://test.deribit.com/api/v2/private/get_account_summary",
            params={"currency": "BTC"},
            headers={"Authorization": "Bearer token"},
        ).respond(
            status_code=200,
            json={"result": {"currency": "BTC", "balance": 1.0}},
        )

        async with DeribitClient(base_url="https://test.deribit.com/api/v2", client_id="id", client_secret="secret") as client:
            summary = await client.get_account_summary("BTC")

        assert summary == {"currency": "BTC", "balance": 1.0}


@pytest.mark.asyncio
async def test_get_account_summary_invalid_payload():
    with respx.mock() as mock:
        mock.get(
            "https://test.deribit.com/api/v2/public/auth",
            params={
                "grant_type": "client_credentials",
                "client_id": "id",
                "client_secret": "secret",
            },
        ).respond(
            status_code=200,
            json={"result": {"access_token": "token", "expires_in": 10}},
        )
        mock.get(
            "https://test.deribit.com/api/v2/private/get_account_summary",
            params={"currency": "BTC"},
            headers={"Authorization": "Bearer token"},
        ).respond(
            status_code=200,
            json={"foo": "bar"},
        )

        async with DeribitClient(base_url="https://test.deribit.com/api/v2", client_id="id", client_secret="secret") as client:
            with pytest.raises(ValueError, match="Unexpected account summary response format"):
                await client.get_account_summary("BTC")
