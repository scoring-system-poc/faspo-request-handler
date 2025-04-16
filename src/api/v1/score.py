import typing
import logging
import fastapi
import datetime as dt

from src.core.exception import HTTPException
from src.model.score import ScoreSummary
from src.service import score_handler


logger = logging.getLogger(__name__)
router = fastapi.APIRouter(
    prefix="/score",
    tags=["score"],
)


@router.get("")
async def get_most_recent_score(
    subject_id: str,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> ScoreSummary:
    """
    Get the most recent score for a subject
    :param subject_id: ID of the subject
    :param correlation_id: Correlation ID for tracing
    :return: Most recent score value for the subject
    """
    score_history = await score_handler.get_score_history(subject_id=subject_id)

    if not score_history:
        raise HTTPException(
            status_code=404,
            logger_name=__name__,
            logger_lvl=logging.INFO,
        )

    return score_history[0]


@router.get("/history")
async def get_score_history(
    subject_id: str,
    date_from: typing.Annotated[dt.datetime | None, fastapi.Query()] = None,
    date_to: typing.Annotated[dt.datetime | None, fastapi.Query()] = None,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> list[ScoreSummary]:
    """
    Get the score history for a subject
    :param subject_id: ID of the subject
    :param date_from: Start date for the score history
    :param date_to: End date for the score history
    :param correlation_id: Correlation ID for tracing
    :return: List of historical calculations
    """
    return await score_handler.get_score_history(subject_id=subject_id, date_from=date_from, date_to=date_to)


@router.post("")
async def trigger_score(
    subject_id: str,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> ScoreSummary:
    """
    Trigger score calculation for a subject
    :param subject_id: ID of the subject
    :param correlation_id: Correlation ID for tracing
    :return: Calculated score
    """
    return await score_handler.trigger_score(subject_id=subject_id, correlation_id=correlation_id)

