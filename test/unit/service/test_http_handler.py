import pytest
import unittest.mock

from src.core.exception import HTTPException
from src.service import http_handler


@pytest.fixture
def mock_aiohttp():
    with unittest.mock.patch("aiohttp.ClientSession") as mock_client:
        mock_client.return_value = mock_client
        mock_client.__aenter__.return_value = mock_client
        yield mock_client


@pytest.mark.asyncio
async def test_post_data(mock_aiohttp):
    mock_aiohttp.post = mock_aiohttp
    mock_aiohttp.status = 200
    mock_aiohttp.json.side_effect = unittest.mock.AsyncMock(return_value={"key": "value"})

    assert await http_handler.post_data("http://test.com", {"key": "value"}) == {"key": "value"}


@pytest.mark.asyncio
async def test_post_data__error(mock_aiohttp):
    mock_aiohttp.post = mock_aiohttp
    mock_aiohttp.status = 400

    with pytest.raises(HTTPException):
        await http_handler.post_data("http://test.com", {"key": "value"})

