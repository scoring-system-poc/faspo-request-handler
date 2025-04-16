import logging
import fastapi
import azure.cosmos.exceptions

from src.core.exception import HTTPException


router = fastapi.APIRouter(
    prefix="/probe",
    tags=["probe"],
)


@router.get("/alive")
async def alive() -> fastapi.responses.JSONResponse:
    """
    Health check endpoint to check if the service is alive.
    :return: fastapi.responses.JSONResponse
    """
    return fastapi.responses.JSONResponse(
        status_code=200,
        content={"detail": "Alive"},
    )


@router.get("/ready")
async def ready() -> fastapi.responses.JSONResponse:
    """
    Readiness check endpoint to check if the service is ready to process requests.
    :return: fastapi.responses.JSONResponse
    """
    try:
        from src.db.cosmos import db
        await db.read()
    except azure.cosmos.exceptions.CosmosHttpResponseError as e:
        raise HTTPException(
            status_code=503,
            logger_name=__name__,
            logger_lvl=logging.ERROR,
            logger_msg=str(e),
        )

    return fastapi.responses.JSONResponse(
        status_code=200,
        content={"detail": "Ready"},
    )

