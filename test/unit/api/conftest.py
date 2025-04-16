import pytest
import unittest.mock
import httpx


@pytest.fixture
async def async_client(mock_environ, mock_cosmos) -> httpx.AsyncClient:
    from main import app

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_document_service() -> unittest.mock.Mock:
    with unittest.mock.patch("src.api.v1.document.document_handler") as mock:
        yield mock


@pytest.fixture
def mock_score_service_in_document() -> unittest.mock.Mock:
    with unittest.mock.patch("src.api.v1.document.score_handler") as mock:
        yield mock


@pytest.fixture
def mock_score_service_in_score() -> unittest.mock.Mock:
    with unittest.mock.patch("src.api.v1.score.score_handler") as mock:
        yield mock


@pytest.fixture
def mock_subject_service() -> unittest.mock.Mock:
    with unittest.mock.patch("src.api.v1.subject.subject_handler") as mock:
        yield mock


@pytest.fixture
def mock_http_service() -> unittest.mock.Mock:
    with unittest.mock.patch("src.api.v1.export.http_handler") as mock:
        yield mock

