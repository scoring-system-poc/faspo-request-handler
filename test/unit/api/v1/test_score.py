import pytest
import unittest.mock
import httpx
import datetime as dt

from src.core.exception import HTTPException
from src.model.score import ScoreSummary


@pytest.mark.asyncio
async def test_get_most_recent_score(
    async_client: httpx.AsyncClient,
    mock_score_service_in_score,
    mock_score_summary,
) -> None:
    mock_score_service_in_score.get_score_history = unittest.mock.AsyncMock(return_value=mock_score_summary)

    response = await async_client.get("/api/v1/subject/subject-id/score")

    assert response.status_code == 200
    assert response.json() == mock_score_summary[0].model_dump(mode="json", by_alias=True)
    mock_score_service_in_score.get_score_history.assert_awaited_once_with(subject_id="subject-id")


@pytest.mark.asyncio
async def test_get_most_recent_score__no_data(async_client: httpx.AsyncClient, mock_score_service_in_score) -> None:
    mock_score_service_in_score.get_score_history = unittest.mock.AsyncMock(return_value=[])

    response = await async_client.get("/api/v1/subject/subject-id/score")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
async def test_get_score_history(
    async_client: httpx.AsyncClient,
    mock_score_service_in_score,
    mock_score_summary,
) -> None:
    mock_score_service_in_score.get_score_history = unittest.mock.AsyncMock(return_value=mock_score_summary)

    response = await async_client.get(
        "/api/v1/subject/subject-id/score/history?date_from=1970-01-01&date_to=1970-12-31",
    )

    assert response.status_code == 200
    assert response.json() == [score.model_dump(mode="json", by_alias=True) for score in mock_score_summary]
    mock_score_service_in_score.get_score_history.assert_awaited_once_with(
        subject_id="subject-id",
        date_from=dt.datetime(1970, 1, 1),
        date_to=dt.datetime(1970, 12, 31),
    )


@pytest.mark.asyncio
async def test_get_score_history__no_data(async_client: httpx.AsyncClient, mock_score_service_in_score) -> None:
    mock_score_service_in_score.get_score_history = unittest.mock.AsyncMock(return_value=[])

    response = await async_client.get(
        "/api/v1/subject/subject-id/score/history?date_from=1970-01-01&date_to=1970-12-31",
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_trigger_score(
    async_client: httpx.AsyncClient,
    mock_score_service_in_score,
    mock_score_summary,
) -> None:
    mock_score_service_in_score.trigger_score = unittest.mock.AsyncMock(return_value=mock_score_summary[0])

    response = await async_client.post(
        "/api/v1/subject/subject-id/score",
        headers={"Correlation-Id": "correlation-id"},
    )

    assert response.status_code == 200
    assert response.json() == mock_score_summary[0].model_dump(mode="json", by_alias=True)
    mock_score_service_in_score.trigger_score.assert_awaited_once_with(
        subject_id="subject-id",
        correlation_id="correlation-id",
    )


@pytest.mark.asyncio
async def test_trigger_score__error(async_client: httpx.AsyncClient, mock_score_service_in_score) -> None:
    mock_score_service_in_score.trigger_score.side_effect = HTTPException(500)

    response = await async_client.post(
        "/api/v1/subject/subject-id/score",
        headers={"Correlation-Id": "correlation-id"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
