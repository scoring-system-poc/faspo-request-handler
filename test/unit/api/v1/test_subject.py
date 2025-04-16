import pytest
import unittest.mock
import httpx
import datetime as dt

from src.core.exception import HTTPException
from src.model.subject import Subject, Address


@pytest.mark.asyncio
async def test_search_subject(async_client: httpx.AsyncClient, mock_subject_service, mock_subject) -> None:
    mock_subject_service.search_subject = unittest.mock.AsyncMock(return_value=mock_subject)

    response = await async_client.get("/api/v1/subject?ic=ic&name=name&include_not_active=true")

    assert response.status_code == 200
    assert response.json() == [subject.model_dump(mode="json", by_alias=True) for subject in mock_subject]
    mock_subject_service.search_subject.assert_awaited_once_with(
        ic="ic",
        name="name",
        include_not_active=True,
    )


@pytest.mark.asyncio
async def test_search_subject__no_data(async_client: httpx.AsyncClient, mock_subject_service, mock_subject) -> None:
    mock_subject_service.search_subject = unittest.mock.AsyncMock(return_value=[])

    response = await async_client.get("/api/v1/subject?ic=ic&name=name&include_not_active=true")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_subject(async_client: httpx.AsyncClient, mock_subject_service, mock_subject) -> None:
    mock_subject_service.get_subject = unittest.mock.AsyncMock(return_value=mock_subject[0])

    response = await async_client.get("/api/v1/subject/subject-id")

    assert response.status_code == 200
    assert response.json() == mock_subject[0].model_dump(mode="json", by_alias=True)
    mock_subject_service.get_subject.assert_awaited_once_with(subject_id="subject-id")


@pytest.mark.asyncio
async def test_get_subject__no_data(async_client: httpx.AsyncClient, mock_subject_service) -> None:
    mock_subject_service.get_subject.side_effect = HTTPException(404)

    response = await async_client.get("/api/v1/subject/subject-id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
async def test_update_subject(async_client: httpx.AsyncClient, mock_subject_service, mock_subject) -> None:
    mock_subject_service.update_subject = unittest.mock.AsyncMock(return_value=mock_subject[0])

    response = await async_client.patch(
        "/api/v1/subject/subject-id",
        json={
            "name": "name",
            "address": {"region": "region", "street": "street", "zip": "zip"},
            "currency": "CZK",
            "active": True,
            "extra": "extra",
        }
    )

    assert response.status_code == 200
    assert response.json() == mock_subject[0].model_dump(mode="json", by_alias=True)
    mock_subject_service.update_subject.assert_awaited_once_with(
        subject_id="subject-id",
        name="name",
        address=Address(
            region="region",
            street="street",
            zip="zip",
        ),
        currency="CZK",
        active=True,
        extra="extra",
    )


@pytest.mark.asyncio
async def test_update_subject__error(async_client: httpx.AsyncClient, mock_subject_service) -> None:
    mock_subject_service.update_subject.side_effect = HTTPException(400)

    response = await async_client.patch(
        "/api/v1/subject/subject-id",
        json={
            "name": "name",
            "address": {"region": "region", "street": "street", "zip": "zip"},
            "currency": "CZK",
            "active": True,
            "extra": "extra",
        }
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Bad Request"}


