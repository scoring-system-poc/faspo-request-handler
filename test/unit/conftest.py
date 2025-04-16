import pytest
import unittest.mock

import os
import azure.cosmos.aio
import azure.cosmos.exceptions

from src.model.subject import Subject
from src.model.document import Document
from src.model.sheet import Sheet
from src.model.score import ScoreSummary


class _AsyncIterator:
    def __init__(self, seq):
        self._seq = seq
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            self.iter = iter(self._seq)
            raise StopAsyncIteration


@pytest.fixture(autouse=True)
def mock_environ(monkeypatch) -> None:
    with unittest.mock.patch.dict(os.environ, clear=True):
        env = {
            "AZURE_CLIENT_ID": "00000000-0000-0000-0000-000000000000",
            "AZURE_TENANT_ID": "00000000-0000-0000-0000-000000000000",
            "AZURE_SUBSCRIPTION_ID": "00000000-0000-0000-0000-000000000000",
            "COSMOS_URL": "https://test.documents.azure.com:443/",
            "COSMOS_DB": "test",
            "COSMOS_DOCUMENT_CONTAINER": "document",
            "COSMOS_SUBJECT_CONTAINER": "subject",
            "ONLINE_DATA_SERVICE_URL": "http://faspo-online-data-service/api/v1",
            "MODEL_SERVICE_URL": "http://faspo-model-service/api/v1",
            "EXPORT_SERVICE_URL": "http://faspo-export-service/api/v1",
        }
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        yield


@pytest.fixture(autouse=True, scope="session")
def mock_cosmos() -> azure.cosmos.aio.DatabaseProxy:
    with (
        unittest.mock.patch("azure.identity.aio.WorkloadIdentityCredential"),
        unittest.mock.patch("azure.cosmos.aio.CosmosClient") as mock_client,
    ):
        mock_db = unittest.mock.AsyncMock(spec=azure.cosmos.aio.DatabaseProxy)
        mock_container = unittest.mock.AsyncMock(spec=azure.cosmos.aio.ContainerProxy)

        mock_container.query_items.return_value = _AsyncIterator([{"subject_id": "x", "sheets": [{"id": "sheet_id"}]}])
        mock_container.read_item.return_value = {"id": "sheet_id"}

        mock_db.get_container_client.return_value = mock_container

        mock_client.return_value = mock_client
        mock_client.get_database_client.return_value = mock_db

        yield mock_db



@pytest.fixture
def mock_docs() -> list[Document]:
    return [
        Document(
            id=str(i),
            subject_id="1",
            type={"key": "001", "name": "doc_name", "layer": 1, "order": 1},
            period=period,
            version={"version": 1, "author": "author", "created": "1970-01-01T00:00:00"},
            sheets=[
                {
                    "id": "1",
                    "subject_id": str(i),
                    "doc_id": "1",
                    "name": "sheet_name_1",
                    "number": 1,
                    "items": [["a", "b", 1.0, 2.0, 3.0, 4.0], ["c", "d", 5.0, 6.0, 7.0, 8.0]],
                },
                {
                    "id": "2",
                    "subject_id": "1",
                    "doc_id": str(i),
                    "name": "sheet_name_2",
                    "number": 2,
                    "items": [["a", "b", 1.0, 2.0], ["c", "d", 3.0, 4.0]],
                },
            ],
        )
        for i, period in enumerate(["1970-01-01", "1971-01-01", "1972-01-01"], 1)
    ]


@pytest.fixture
def mock_sheets() -> list[Sheet]:
    return [
        Sheet(
            id="1",
            subject_id="1",
            doc_id="1",
            name="sheet_name_1",
            number=1,
            items=[["a", "b", 1.0, 2.0, 3.0, 4.0], ["c", "d", 5.0, 6.0, 7.0, 8.0]],
        ),
        Sheet(
            id="2",
            subject_id="1",
            doc_id="1",
            name="sheet_name_2",
            number=2,
            items=[["a", "b", 1.0, 2.0], ["c", "d", 3.0, 4.0]],
        ),
    ]


@pytest.fixture
def mock_score_summary() -> list[ScoreSummary]:
    return [
        ScoreSummary(
            created="1970-01-01T00:00:00",
            period="1970-01-01",
            score=1.0,
        ),
        ScoreSummary(
            created="1971-01-01T00:00:00",
            period="1971-01-01",
            score=2.0,
        ),
    ]


@pytest.fixture
def mock_subject() -> list[Subject]:
    return [
        Subject(
            id="1",
            name="subject_name_1",
            address={
                "region": "region_1",
                "street": "street_1",
                "zip": "zip_1",
            },
            currency="USD",
            created="1970-01-01",
            updated="1970-01-02",
            active=True,
            extra="extra_1",
        ),
        Subject(
            id="2",
            name="subject_name_2",
            address={
                "region": "region_2",
                "street": "street_2",
                "zip": "zip_2",
            },
            currency="EUR",
            created="1971-01-01",
            updated="1971-01-02",
            active=False,
            extra="extra_2",
        ),
    ]


