import pytest
import unittest.mock
import httpx
import datetime as dt

from src.core.exception import HTTPException


@pytest.mark.asyncio
async def test_trigger_export(async_client: httpx.AsyncClient, mock_http_service) -> None:
    mock_http_service.post_data = unittest.mock.AsyncMock(return_value="OK")

    response = await async_client.post(
        "/api/v1/export/export-id",
        json={"date_from": dt.datetime(1970, 1, 1).isoformat(), "date_to": dt.datetime(1970, 12, 31).isoformat()},
        headers={"Correlation-Id": "correlation-id"},
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "OK"}
    mock_http_service.post_data.assert_awaited_once_with(
        url=f"http://faspo-export-service/api/v1/export/export-id",
        data={"date_from": dt.datetime(1970, 1, 1), "date_to": dt.datetime(1970, 12, 31)},
        correlation_id="correlation-id",
    )


@pytest.mark.asyncio
async def test_trigger_export__error(async_client: httpx.AsyncClient, mock_http_service) -> None:
    mock_http_service.post_data.side_effect = HTTPException(404)

    response = await async_client.post(
        "/api/v1/export/export-id",
        json={"date_from": dt.datetime(1970, 1, 1).isoformat(), "date_to": dt.datetime(1970, 12, 31).isoformat()},
        headers={"Correlation-Id": "correlation-id"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

