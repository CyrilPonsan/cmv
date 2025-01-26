from fastapi import APIRouter

from app.routers import documents
from app.routers import patients
from app.routers import admission

router = APIRouter(prefix="/api", tags=["api"])

router.include_router(admission.router)
router.include_router(documents.router)
router.include_router(patients.router)
