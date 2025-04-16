import asyncio
import logging
import datetime as dt
import azure.cosmos.exceptions

from src.core.config import CONFIG
from src.core.exception import HTTPException
from src.model.document import Document
from src.model.sheet import Sheet, SheetCell
from src.db import cosmos
from src.service import http_handler


async def get_documents(subject_id: str) -> list[Document]:
    """
    Get documents for a subject
    :param subject_id: ID of the subject
    :return: List of documents for the subject
    """
    return [
        Document(**doc)
        async for doc
        in cosmos.c_document.query_items(query="SELECT * FROM c WHERE c._type = 'doc'", partition_key=subject_id)
    ]


async def get_document(subject_id: str, document_id: str) -> Document:
    """
    Get document by ID
    :param subject_id: ID of the subject
    :param document_id: ID of the document
    :return: Document object or raise HTTPException if not found
    """
    try:
        return await cosmos.c_document.read_item(
            item=document_id,
            partition_key=subject_id,
        )
    except azure.cosmos.exceptions.CosmosHttpResponseError as e:
        raise HTTPException(
            status_code=e.status_code,
            logger_name=__name__,
            logger_lvl=logging.INFO,
            logger_msg=str(e.reason),
        )


async def get_document_sheets(subject_id: str, document_id: str) -> list[Sheet]:
    """
    Get document sheets
    :param subject_id: ID of the subject
    :param document_id: ID of the document
    :return: List of document sheets
    """
    return [
        Sheet(**sheet)
        async for sheet
        in cosmos.c_document.query_items(
            query="SELECT * FROM c WHERE c._type = 'sheet' AND c.doc_id = @doc_id",
            parameters=[
                {"name": "@doc_id", "value": document_id},
            ],
            partition_key=subject_id,
        )
    ]


async def get_document_sheet(subject_id: str, document_id: str, sheet_num: int) -> Sheet:
    """
    Get document sheet by number
    :param subject_id: ID of the subject
    :param document_id: ID of the document
    :param sheet_num: Sheet number
    :return: Document sheet object or None if not found
    """
    sheets = [
        Sheet(**sheet)
        async for sheet
        in cosmos.c_document.query_items(
            query="SELECT * FROM c WHERE c._type = 'sheet' AND c.doc_id = @doc_id AND c.number = @sheet_num",
            parameters=[
                {"name": "@doc_id", "value": document_id},
                {"name": "@sheet_num", "value": sheet_num},
            ],
            partition_key=subject_id,
        )
    ]

    if not sheets:
        raise HTTPException(
            status_code=404,
            logger_name=__name__,
            logger_lvl=logging.INFO
        )

    return sheets[0]


async def patch_sheet_data(
    subject_id: str,
    document_id: str,
    sheet_num: int,
    cell_data: list[SheetCell],
) -> Sheet:
    """
    Update sheet data
    :param subject_id: ID of the subject
    :param document_id: ID of the document
    :param sheet_num: Sheet number
    :param cell_data: List of cell data to update
    :return: Updated sheet object
    """
    sheet = await get_document_sheet(subject_id=subject_id, document_id=document_id, sheet_num=sheet_num)
    await asyncio.gather(
        *[
            cosmos.c_document.patch_item(
                item=sheet.id,
                partition_key=subject_id,
                patch_operations=[
                    {"op": "set", "path": f"/items/{cell.row_num}/{cell.col_num}", "value": cell.value}
                    for cell in cell_data[i:i + 10]
                ]
            )
            for i in range(0, len(cell_data), 10)
        ]
    )

    return await get_document_sheet(subject_id=subject_id, document_id=document_id, sheet_num=sheet_num)


async def refresh_documents(
    subject_id: str,
    doc_type: str = None,
    period: dt.date = None,
    correlation_id: str = None,
) -> dict:
    """
    Refresh documents for a subject (i.e. online-data fetch).
    :param subject_id: ID of the subject
    :param doc_type: Type of the document (optional - if not provided all types from L1 are fetched)
    :param period: Period of the document (optional - if not provided latest period is used)
    :param correlation_id: Correlation ID for tracing (optional)
    :return: Dictionary with document types and their statuses
    """
    doc_types = [doc_type] if doc_type else ["001", "002", "003", "080"]
    results = {}

    for doc_type in doc_types:
        try:
            results[doc_type] = {
                "status": 200,
                "detail": await http_handler.post_data(
                    url=f"{CONFIG.ONLINE_DATA_SERVICE_URL}/mfcr/{doc_type}?subject_id={subject_id}&period={period}",
                    data={},
                    correlation_id=correlation_id,
                )
            }
        except HTTPException as e:
            results[doc_type] = {
                "status": e.status_code,
                "detail": e.detail,
            }

    return results
