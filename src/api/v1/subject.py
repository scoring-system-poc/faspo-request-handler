import typing
import logging
import fastapi

from src.model.subject import Subject, Address
from src.service import subject_handler


logger = logging.getLogger(__name__)
router = fastapi.APIRouter(
    prefix="/subject",
    tags=["subject"],
)


@router.get("")
async def search_subject(
    ic: str = None,
    name: str = None,
    include_not_active: bool = False,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> list[Subject]:
    """
    Search for subjects
    :param ic: IC number of the subject
    :param name: Name of the subject
    :param include_not_active: Include not active subjects
    :param correlation_id: Correlation ID for tracing
    :return: List of subjects matching the search criteria
    """
    return await subject_handler.search_subject(ic=ic, name=name, include_not_active=include_not_active)


@router.get("/{subject_id}")
async def get_subject(
    subject_id: str,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> Subject:
    """
    Get subject by ID
    :param subject_id: ID of the subject
    :param correlation_id: Correlation ID for tracing
    :return: Subject object or raise HTTPException if not found
    """
    return await subject_handler.get_subject(subject_id=subject_id)


@router.patch("/{subject_id}")
async def update_subject(
    subject_id: str,
    name: typing.Annotated[str | None, fastapi.Body()] = None,
    address: typing.Annotated[Address | None, fastapi.Body()] = None,
    currency: typing.Annotated[str | None, fastapi.Body()] = None,
    active: typing.Annotated[bool | None, fastapi.Body()] = None,
    extra: typing.Annotated[str | None, fastapi.Body()] = None,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> Subject:
    """
    Update subject information
    :param subject_id: Subject ID
    :param name: New name of the subject
    :param address: Address object containing new address information
    :param currency: Currency code
    :param active: Boolean indicating if the subject is active
    :param extra: Additional information
    :param correlation_id: Correlation ID for tracing
    :return: Updated Subject object
    """
    return await subject_handler.update_subject(
        subject_id=subject_id,
        name=name,
        address=address,
        currency=currency,
        active=active,
        extra=extra,
    )


@router.post("", status_code=201)
async def create_subject(
    subject: Subject,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> Subject:
    """
    Create a new subject (only temporary for testing purposes)
    :param subject: Subject object containing the new subject information
    :param correlation_id: Correlation ID for tracing
    :return: Created Subject object
    """
    return await subject_handler.create_subject(subject=subject)


@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: str,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> dict:
    """
    Delete a subject by ID (only temporary for testing purposes)
    :param subject_id: ID of the subject to be deleted
    :param correlation_id: Correlation ID for tracing
    :return: Deleted Subject object
    """
    await subject_handler.delete_subject(subject_id=subject_id)
    return {"detail": "OK"}

