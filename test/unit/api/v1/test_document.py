import pytest
import unittest.mock
import httpx
import datetime as dt

from src.core.exception import HTTPException
from src.model.sheet import SheetCell


@pytest.mark.asyncio
async def test_get_documents(async_client: httpx.AsyncClient, mock_document_service, mock_docs) -> None:
    mock_document_service.get_documents = unittest.mock.AsyncMock(return_value=mock_docs)

    response = await async_client.get("/api/v1/subject/subject-id/document")

    assert response.status_code == 200
    assert response.json() == [doc.model_dump(mode="json", by_alias=True) for doc in mock_docs]
    mock_document_service.get_documents.assert_awaited_once_with(subject_id="subject-id")


@pytest.mark.asyncio
async def test_get_documents__no_data(async_client: httpx.AsyncClient, mock_document_service) -> None:
    mock_document_service.get_documents = unittest.mock.AsyncMock(return_value=[])

    response = await async_client.get("/api/v1/subject/subject-id/document")

    assert response.status_code == 200
    assert response.json() == []
    mock_document_service.get_documents.assert_awaited_once_with(subject_id="subject-id")


@pytest.mark.asyncio
async def test_get_document(async_client: httpx.AsyncClient, mock_document_service, mock_docs) -> None:
    mock_document_service.get_document = unittest.mock.AsyncMock(return_value=mock_docs[0])

    response = await async_client.get("/api/v1/subject/subject-id/document/doc-id")

    assert response.status_code == 200
    assert response.json() == mock_docs[0].model_dump(mode="json", by_alias=True)
    mock_document_service.get_document.assert_awaited_once_with(subject_id="subject-id", document_id="doc-id")


@pytest.mark.asyncio
async def test_get_document__no_data(async_client: httpx.AsyncClient, mock_document_service) -> None:
    mock_document_service.get_document.side_effect = HTTPException(404)

    response = await async_client.get("/api/v1/subject/subject-id/document/doc-id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
async def test_get_document_sheets(async_client: httpx.AsyncClient, mock_document_service, mock_sheets) -> None:
    mock_document_service.get_document_sheets = unittest.mock.AsyncMock(return_value=mock_sheets)

    response = await async_client.get("/api/v1/subject/subject-id/document/doc-id/sheet")

    assert response.status_code == 200
    assert response.json() == [sheet.model_dump(mode="json", by_alias=True) for sheet in mock_sheets]
    mock_document_service.get_document_sheets.assert_awaited_once_with(subject_id="subject-id", document_id="doc-id")


@pytest.mark.asyncio
async def test_get_document_sheets__no_data(async_client: httpx.AsyncClient, mock_document_service) -> None:
    mock_document_service.get_document_sheets = unittest.mock.AsyncMock(return_value=[])

    response = await async_client.get("/api/v1/subject/subject-id/document/doc-id/sheet")

    assert response.status_code == 200
    assert response.json() == []
    mock_document_service.get_document_sheets.assert_awaited_once_with(subject_id="subject-id", document_id="doc-id")


@pytest.mark.asyncio
async def test_get_document_sheet(async_client: httpx.AsyncClient, mock_document_service, mock_sheets) -> None:
    mock_document_service.get_document_sheet = unittest.mock.AsyncMock(return_value=mock_sheets[0])

    response = await async_client.get("/api/v1/subject/subject-id/document/doc-id/sheet/1")

    assert response.status_code == 200
    assert response.json() == mock_sheets[0].model_dump(mode="json", by_alias=True)
    mock_document_service.get_document_sheet.assert_awaited_once_with(
        subject_id="subject-id",
        document_id="doc-id",
        sheet_num=1,
    )


@pytest.mark.asyncio
async def test_get_document_sheet__no_data(async_client: httpx.AsyncClient, mock_document_service) -> None:
    mock_document_service.get_document_sheet.side_effect = HTTPException(404)

    response = await async_client.get("/api/v1/subject/subject-id/document/doc-id/sheet/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
async def test_patch_document(
    async_client: httpx.AsyncClient,
    mock_document_service,
    mock_score_service_in_document,
    mock_sheets,
) -> None:
    mock_document_service.patch_sheet_data = unittest.mock.AsyncMock(return_value=mock_sheets[0])
    mock_score_service_in_document.trigger_score = unittest.mock.AsyncMock()

    response = await async_client.patch(
        "/api/v1/subject/subject-id/document/doc-id/sheet/1",
        json=[{"row_num": 1, "col_num": 1, "value": "new_value"}, {"row_num": 2, "col_num": 2, "value": 2.0}],
        headers={"Correlation-Id": "correlation-id"},
    )

    assert response.status_code == 200
    assert response.json() == mock_sheets[0].model_dump(mode="json", by_alias=True)
    mock_document_service.patch_sheet_data.assert_awaited_once_with(
        subject_id="subject-id",
        document_id="doc-id",
        sheet_num=1,
        cell_data=[SheetCell(row_num=1, col_num=1, value="new_value"), SheetCell(row_num=2, col_num=2, value=2.0)],
    )
    mock_score_service_in_document.trigger_score.assert_awaited_once_with(
        subject_id="subject-id",
        correlation_id="correlation-id",
    )


@pytest.mark.asyncio
async def test_patch_document__no_data(async_client: httpx.AsyncClient, mock_document_service) -> None:
    mock_document_service.patch_sheet_data.side_effect = HTTPException(404)

    response = await async_client.patch(
        "/api/v1/subject/subject-id/document/doc-id/sheet/1",
        json=[{"row_num": 1, "col_num": 1, "value": "new_value"}, {"row_num": 2, "col_num": 2, "value": 2.0}],
        headers={"Correlation-Id": "correlation-id"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
async def test_patch_document__scoring_error(
    async_client: httpx.AsyncClient,
    mock_document_service,
    mock_score_service_in_document,
) -> None:
    mock_document_service.patch_sheet_data = unittest.mock.AsyncMock()
    mock_score_service_in_document.trigger_score.side_effect = HTTPException(500)

    response = await async_client.patch(
        "/api/v1/subject/subject-id/document/doc-id/sheet/1",
        json=[{"row_num": 1, "col_num": 1, "value": "new_value"}, {"row_num": 2, "col_num": 2, "value": 2.0}],
        headers={"Correlation-Id": "correlation-id"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}


@pytest.mark.asyncio
async def test_refresh_documents(async_client: httpx.AsyncClient, mock_document_service) -> None:
    mock_document_service.refresh_documents = unittest.mock.AsyncMock(return_value={"status": "OK"})

    response = await async_client.post(
        "/api/v1/subject/subject-id/document/refresh",
        json={"doc_type": "001", "period": "1970-01-01"},
        headers={"Correlation-Id": "correlation-id"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
    mock_document_service.refresh_documents.assert_awaited_once_with(
        subject_id="subject-id",
        doc_type="001",
        period=dt.date(1970, 1, 1),
        correlation_id="correlation-id",
    )


@pytest.mark.asyncio
async def test_refresh_documents__error(async_client: httpx.AsyncClient, mock_document_service) -> None:
    mock_document_service.refresh_documents.side_effect = HTTPException(500)

    response = await async_client.post("/api/v1/subject/subject-id/document/refresh")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}

