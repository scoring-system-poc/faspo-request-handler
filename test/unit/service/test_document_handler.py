import unittest.mock

import pytest
import azure.cosmos.exceptions

from src.core.exception import HTTPException
from ..conftest import _AsyncIterator


@pytest.mark.asyncio
async def test_get_documents(mock_cosmos, mock_docs):
    from src.service.document_handler import get_documents

    mock_cosmos.get_container_client().query_items.return_value = _AsyncIterator([d.model_dump() for d in mock_docs])
    documents = await get_documents(subject_id="x")

    assert len(documents) == len(mock_docs)


@pytest.mark.asyncio
async def test_get_documents__no_data(mock_cosmos):
    from src.service.document_handler import get_documents

    mock_cosmos.get_container_client().query_items.return_value = _AsyncIterator([])
    documents = await get_documents(subject_id="x")

    assert len(documents) == 0


@pytest.mark.asyncio
async def test_get_document(mock_cosmos, mock_docs):
    from src.service.document_handler import get_document

    mock_cosmos.get_container_client().read_item.return_value = mock_docs[0]
    document = await get_document(subject_id="x", document_id="y")

    assert document.id == mock_docs[0].id


@pytest.mark.asyncio
async def test_get_document__not_found(mock_cosmos):
    from src.service.document_handler import get_document

    mock_cosmos.get_container_client().read_item.side_effect = azure.cosmos.exceptions.CosmosHttpResponseError
    with pytest.raises(HTTPException):
        await get_document(subject_id="x", document_id="y")


@pytest.mark.asyncio
async def test_get_document_sheets(mock_cosmos, mock_sheets):
    from src.service.document_handler import get_document_sheets

    mock_cosmos.get_container_client().query_items.return_value = _AsyncIterator([s.model_dump() for s in mock_sheets])
    sheets = await get_document_sheets(subject_id="x", document_id="y")

    assert len(sheets) == len(mock_sheets)


@pytest.mark.asyncio
async def test_get_document_sheets__no_data(mock_cosmos):
    from src.service.document_handler import get_document_sheets

    mock_cosmos.get_container_client().query_items.return_value = _AsyncIterator([])
    sheets = await get_document_sheets(subject_id="x", document_id="y")

    assert len(sheets) == 0


@pytest.mark.asyncio
async def test_get_document_sheet(mock_cosmos, mock_sheets):
    from src.service.document_handler import get_document_sheet

    mock_cosmos.get_container_client().query_items.return_value = _AsyncIterator([s.model_dump() for s in mock_sheets])
    sheet = await get_document_sheet(subject_id="x", document_id="y", sheet_num=1)

    assert sheet.id == mock_sheets[0].id


@pytest.mark.asyncio
async def test_get_document_sheet__not_found(mock_cosmos):
    from src.service.document_handler import get_document_sheet

    mock_cosmos.get_container_client().query_items.return_value = _AsyncIterator([])
    with pytest.raises(HTTPException):
        await get_document_sheet(subject_id="x", document_id="y", sheet_num=1)


@pytest.mark.asyncio
async def test_patch_data(mock_cosmos, mock_sheets):
    from src.service.document_handler import patch_sheet_data

    mock_cosmos.get_container_client().query_items.return_value = _AsyncIterator([s.model_dump() for s in mock_sheets])
    assert await patch_sheet_data(subject_id="x", document_id="y", sheet_num=1, cell_data=[])


@pytest.mark.asyncio
async def test_patch_data__not_found(mock_cosmos):
    from src.service.document_handler import patch_sheet_data

    mock_cosmos.get_container_client().query_items.return_value = _AsyncIterator([])
    with pytest.raises(HTTPException):
        await patch_sheet_data(subject_id="x", document_id="y", sheet_num=1, cell_data=[])


@pytest.mark.asyncio
async def test_refresh_documents():
    with unittest.mock.patch("src.service.document_handler.http_handler") as mock_http_handler:
        from src.service.document_handler import refresh_documents
        mock_http_handler.post_data.side_effect = unittest.mock.AsyncMock(return_value="OK")

        result = await refresh_documents(subject_id="x")

        assert result == {
            "001": {"detail": "OK", "status": 200},
            "002": {"detail": "OK", "status": 200},
            "003": {"detail": "OK", "status": 200},
            "080": {"detail": "OK", "status": 200},
        }


@pytest.mark.asyncio
async def test_refresh_documents__error():
    with unittest.mock.patch("src.service.document_handler.http_handler") as mock_http_handler:
        from src.service.document_handler import refresh_documents
        mock_http_handler.post_data.side_effect = unittest.mock.AsyncMock(
            side_effect=[
                "OK",
                HTTPException(status_code=500),
                "OK",
                "OK",
            ]
        )

        result = await refresh_documents(subject_id="x")

        assert result == {
            "001": {"detail": "OK", "status": 200},
            "002": {"detail": "Internal Server Error", "status": 500},
            "003": {"detail": "OK", "status": 200},
            "080": {"detail": "OK", "status": 200},
        }
