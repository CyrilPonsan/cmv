from fastapi import APIRouter
from . import patients

router = APIRouter(prefix="/api", tags=["api"])


router.include_router(patients.router)
