import asyncio
import datetime as dt

from src.model.document import Document, FullDocument
from src.model.sheet import Sheet
from src.model.score import ScoreSummary

from src.core.config import CONFIG
from src.db import cosmos
from src.service import http_handler


async def get_score_history(
    subject_id: str,
    date_from: dt.datetime = None,
    date_to: dt.datetime = None,
) -> list[ScoreSummary]:
    """
    Get the score history for a subject
    :param subject_id: ID of the subject
    :param date_from: Start date for the score history
    :param date_to: End date for the score history
    :return: List of historical calculations
    """
    score_docs = [
        Document(**doc)
        async for doc
        in cosmos.c_document.query_items(
            query=f"SELECT * FROM c "
                  f"WHERE c._type = 'doc' "
                  f"AND c.type.key = 'FC' "
                  f"{'AND @date_from <= c.version.created' if date_from else ''} "
                  f"{'AND @date_to >= c.version.created' if date_to else ''} "
                  f"ORDER BY c.version.created DESC",
            parameters=[
                {"name": "@subject_id", "value": subject_id},
                {"name": "@date_from", "value": date_from},
                {"name": "@date_to", "value": date_to},
            ],
            partition_key=subject_id,
        )
    ]

    score_sheets = [
        Sheet(**await cosmos.c_document.read_item(item=doc.parts[0].id, partition_key=subject_id))
        for doc in score_docs
    ]

    return [
        ScoreSummary(
            created=doc.version.created,
            period=doc.period,
            score=sheet.items[-1][-1],
        )
        for doc, sheet in zip(score_docs, score_sheets)
    ]


async def trigger_score(subject_id: str, correlation_id: str | None = None) -> ScoreSummary:
    """
    Trigger calculation of scoring document
    :param subject_id: ID of the subject
    :param correlation_id: Correlation ID for tracing
    :return: Score summary
    """
    required_docs = list()
    periods = dict()

    async for doc in cosmos.c_document.query_items(
        query="SELECT * FROM c "
              "WHERE c._type = 'doc' "
              "AND c.type.layer = 1 "
              "AND c.type.period >= @min_period "
              "ORDER BY c.period DESC",
        parameters=[
            {"name": "@min_period", "value": dt.date(dt.date.today().year - 4, 12, 31)},
        ],
        partition_key=subject_id,
    ):
        doc = Document(**doc)

        if doc.type.key in periods and (doc.period in periods[doc.type.key] or len(periods[doc.type.key]) == 3):
            continue

        doc.sheets = await asyncio.gather(*[
            cosmos.c_subject.read_item(item=sheet.id, partition_key=subject_id) for sheet in doc.sheets
        ])

        required_docs.append(doc.model_dump(mode="json", by_alias=True))
        periods[doc.type.key] = periods.get(doc.type.key, set()) + {doc.period}

    result = FullDocument(
        **await http_handler.post_data(
            url=f"{CONFIG.SCORE_SERVICE_URL}/score",
            data=required_docs,
            correlation_id=correlation_id,
        )
    )

    return ScoreSummary(
        created=result.version.created,
        period=result.period,
        score=result.sheets[0].items[-1][-1],
    )
