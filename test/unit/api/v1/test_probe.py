import pytest
import httpx
import azure.cosmos.exceptions


@pytest.mark.asyncio
async def test_alive(async_client: httpx.AsyncClient) -> None:
    response = await async_client.get("/api/v1/probe/alive")

    assert response.status_code == 200
    assert response.json() == {"detail": "Alive"}


@pytest.mark.asyncio
async def test_ready__success(async_client: httpx.AsyncClient) -> None:
    response = await async_client.get("/api/v1/probe/ready")

    assert response.status_code == 200
    assert response.json() == {"detail": "Ready"}


@pytest.mark.asyncio
async def test_ready__failure(async_client: httpx.AsyncClient, mock_cosmos) -> None:
    mock_cosmos.read.side_effect = azure.cosmos.exceptions.CosmosHttpResponseError

    response = await async_client.get("/api/v1/probe/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "Service Unavailable"}

