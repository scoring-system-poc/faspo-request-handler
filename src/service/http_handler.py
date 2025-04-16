import aiohttp

from src.core.exception import HTTPException


async def post_data(url: str, data: dict | list[dict], correlation_id: str | None = None) -> str | dict:
    """
    Post data to the specified URL.
    :param url: Target URL
    :param data: JSON data to be posted
    :param correlation_id: Correlation ID for tracing the request
    :return: Response text from the API
    """
    async with (
        aiohttp.ClientSession() as async_session,
        async_session.post(url=url, headers={"Correlation-Id": correlation_id}, json=data) as response,
    ):
        if response.status < 200 or response.status > 299:
            raise HTTPException(
                status_code=response.status,
                detail=f"Request to {url} failed: {response.reason}",
                logger_name=__name__,
            )

        return await response.json()
