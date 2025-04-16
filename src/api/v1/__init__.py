import fastapi

from .probe import router as probe_router
from .subject import router as subject_router
from .document import router as document_router
from .score import router as score_router
from .export import router as export_router


router = fastapi.APIRouter(
    prefix="/api/v1",
)

router.include_router(probe_router)
router.include_router(subject_router)
router.include_router(document_router, prefix="/subject/{subject_id}")
router.include_router(score_router, prefix="/subject/{subject_id}")
router.include_router(export_router)
