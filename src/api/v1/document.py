import typing
import logging
import fastapi
import datetime as dt

from src.model.document import Document
from src.model.sheet import Sheet, SheetCell
from src.service import document_handler, score_handler


logger = logging.getLogger(__name__)
router = fastapi.APIRouter(
    prefix="/document",
    tags=["document"],
)


@router.get("")
async def get_documents(
    subject_id: str,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> list[Document]:
    """
    Get documents for a subject
    :param subject_id: ID of the subject
    :param correlation_id: Correlation ID for tracing
    :return: List of documents for the subject
    """
    return await document_handler.get_documents(subject_id=subject_id)


@router.get("/{document_id}")
async def get_document(
    subject_id: str,
    document_id: str,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> Document:
    """
    Get document by ID
    :param subject_id: ID of the subject
    :param document_id: ID of the document
    :param correlation_id: Correlation ID for tracing
    :return: Document object or raise HTTPException if not found
    """
    return await document_handler.get_document(subject_id=subject_id, document_id=document_id)


@router.get("/{document_id}/sheet")
async def get_document_sheets(
    subject_id: str,
    document_id: str,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> list[Sheet]:
    """
    Get document sheets
    :param subject_id: ID of the subject
    :param document_id: ID of the document
    :param correlation_id: Correlation ID for tracing
    :return: List of document sheets
    """
    return await document_handler.get_document_sheets(subject_id=subject_id, document_id=document_id)


@router.get("/{document_id}/sheet/{sheet_num}")
async def get_document_sheet(
    subject_id: str,
    document_id: str,
    sheet_num: int,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> Sheet:
    """
    Get document sheet
    :param subject_id: ID of the subject
    :param document_id: ID of the document
    :param sheet_num: Number of the sheet
    :param correlation_id: Correlation ID for tracing
    :return: Document sheet object or raise HTTPException if not found
    """
    return await document_handler.get_document_sheet(subject_id=subject_id, document_id=document_id, sheet_num=sheet_num)


@router.patch("/{document_id}/sheet/{sheet_num}")
async def update_document_sheet(
    subject_id: str,
    document_id: str,
    sheet_num: int,
    sheet_cells: typing.Annotated[list[SheetCell], fastapi.Body()],
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> Sheet:
    """
    Update document sheet
    :param subject_id: ID of the subject
    :param document_id: ID of the document
    :param sheet_num: Number of the sheet
    :param sheet_cells: List of sheet cells to update
    :param correlation_id: Correlation ID for tracing
    :return: Updated sheet object
    """
    sheet = await document_handler.patch_sheet_data(
        subject_id=subject_id,
        document_id=document_id,
        sheet_num=sheet_num,
        cell_data=sheet_cells,
    )

    # trigger recalculation (incorrect business logic, but for PoC purposes it does not matter)
    await score_handler.trigger_score(subject_id=subject_id, correlation_id=correlation_id)

    return sheet


@router.post("/refresh")
async def refresh_documents(
    subject_id: str,
    doc_type: typing.Annotated[str | None, fastapi.Body()] = None,
    period: typing.Annotated[dt.date | None, fastapi.Body()] = None,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> dict:
    """
    Trigger document refresh for a subject (i.e. online-data fetch).
    :param subject_id: ID of the subject
    :param correlation_id: Correlation ID for tracing
    :return: Status of the document refresh
    """
    return await document_handler.refresh_documents(
        subject_id=subject_id,
        doc_type=doc_type,
        period=period,
        correlation_id=correlation_id,
    )

