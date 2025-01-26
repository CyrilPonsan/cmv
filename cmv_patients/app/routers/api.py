from fastapi import APIRouter

from app.routers import documents
from app.routers import patients
from app.routers import admissions

router = APIRouter(prefix="/api", tags=["api"])

router.include_router(admissions.router)
router.include_router(documents.router)
router.include_router(patients.router)
