from fastapi import APIRouter
from . import chambres, patients, services

router = APIRouter(prefix="/api", tags=["api"])


router.include_router(chambres.router)
router.include_router(patients.router)
router.include_router(services.router)
