import typing
import logging
import fastapi
import datetime as dt

from src.core.config import CONFIG
from src.service import http_handler


logger = logging.getLogger(__name__)
router = fastapi.APIRouter(
    prefix="/export",
    tags=["export"],
)


@router.post("/{export_id}")
async def trigger_export(
    export_id: str,
    date_from: typing.Annotated[dt.datetime | None, fastapi.Body()] = None,
    date_to: typing.Annotated[dt.datetime | None, fastapi.Body()] = None,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> dict:
    """
    Trigger specified export job.
    :param export_id: ID of the export job to trigger.
    :param date_from: Date from which to export data.
    :param date_to: Date until which to export data.
    :param correlation_id: Correlation ID for tracing.
    :return: Status of the export job.
    """
    result = await http_handler.post_data(
        url=f"{CONFIG.EXPORT_SERVICE_URL}/export/{export_id}",
        data={"date_from": date_from, "date_to": date_to},
        correlation_id=correlation_id,
    )
    return {"detail": result}

