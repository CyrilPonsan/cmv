from fastapi import APIRouter

from app.routers import chambres
from . import auth, patients, users

router = APIRouter(prefix="/api", tags=["api"])


router.include_router(auth.router)
router.include_router(chambres.router)
router.include_router(patients.router)
router.include_router(users.router)
