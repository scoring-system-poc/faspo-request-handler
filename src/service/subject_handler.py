import logging
import azure.cosmos.exceptions

from src.core.exception import HTTPException
from src.model.subject import Subject, Address
from src.db import cosmos


async def search_subject(ic: str = None, name: str = None, include_not_active: bool = False) -> list[Subject]:
    """
    Search for subjects in the database based on IC number, name, and active status.
    :param ic: IC number of the subject
    :param name: Name of the subject
    :param include_not_active: Include not active subjects
    :return: List of subjects matching the search criteria
    """
    return [
        Subject(**doc)
        async for doc
        in cosmos.c_subject.query_items(
            query=f"SELECT * FROM c "
                  f"WHERE RegexMatch(c.id, @ic, 'i')"
                  f"AND RegexMatch(c.name, @name, 'i')"
                  f"{'AND c.active = true' if not include_not_active else ''}",
            parameters=[
                {"name": "@ic", "value": ic or ".*"},
                {"name": "@name", "value": name or ".*"},
            ],
            continuation_token_limit=1,
        )
    ]


async def get_subject(subject_id: str) -> Subject:
    """
    Get subject by ID.
    :param subject_id: ID of the subject
    :return: Subject object or None if not found
    """
    try:
        return await cosmos.c_subject.read_item(
            item=subject_id,
            partition_key=subject_id,
        )
    except azure.cosmos.exceptions.CosmosHttpResponseError as e:
        raise HTTPException(
            status_code=e.status_code,
            logger_name=__name__,
            logger_lvl=logging.INFO,
            logger_msg=str(e.reason),
        )


async def update_subject(
    subject_id: str,
    name: str | None = None,
    address: Address | None = None,
    currency: str | None = None,
    active: bool | None = None,
    extra: str | None = None,
) -> Subject:
    """
    Update subject information.
    :param subject_id: Subject ID
    :param name: Name of the subject
    :param address: Address of the subject
    :param currency: Currency of the subject
    :param active: Active status of the subject
    :param extra: Extra information about the subject
    :return: Updated subject information
    """
    try:
        return Subject(
            **await cosmos.c_subject.patch_item(
                item=subject_id,
                partition_key=subject_id,
                patch_operations=[
                    *([{"op": "set", "path": "/name", "value": name}] if name else []),
                    *([{"op": "set", "path": "/address/region", "value": address.region}] if address else []),
                    *([{"op": "set", "path": "/address/street", "value": address.street}] if address else []),
                    *([{"op": "set", "path": "/address/zip", "value": address.zip}] if address else []),
                    *([{"op": "set", "path": "/currency", "value": currency}] if currency else []),
                    *([{"op": "set", "path": "/active", "value": active}] if active else []),
                    *([{"op": "set", "path": "/extra", "value": extra}] if extra else []),
                ],
            )
        )
    except azure.cosmos.exceptions.CosmosHttpResponseError as e:
        raise HTTPException(
            status_code=e.status_code,
            logger_name=__name__,
            logger_lvl=logging.INFO,
            logger_msg=str(e.reason),
        )


async def create_subject(subject: Subject) -> Subject:
    """
    Create a new subject.
    :param subject: Subject object containing the new subject information
    :return: Created subject information
    """
    try:
        return Subject(
            **await cosmos.c_subject.create_item(
                body=subject.model_dump(mode="json", by_alias=True),
            )
        )
    except azure.cosmos.exceptions.CosmosHttpResponseError as e:
        raise HTTPException(
            status_code=e.status_code,
            logger_name=__name__,
            logger_lvl=logging.INFO,
            logger_msg=str(e.reason),
        )


async def delete_subject(subject_id: str) -> None:
    """
    Delete a subject by ID.
    :param subject_id: ID of the subject to be deleted
    :return: None
    """
    try:
        await cosmos.c_subject.delete_item(
            item=subject_id,
            partition_key=subject_id,
        )
    except azure.cosmos.exceptions.CosmosHttpResponseError as e:
        raise HTTPException(
            status_code=e.status_code,
            logger_name=__name__,
            logger_lvl=logging.INFO,
            logger_msg=str(e.reason),
        )


