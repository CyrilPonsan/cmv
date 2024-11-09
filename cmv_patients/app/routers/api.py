from fastapi import APIRouter

from app.routers import documents
from app.routers import patients

router = APIRouter(prefix="/api", tags=["api"])


router.include_router(documents.router)
router.include_router(patients.router)
