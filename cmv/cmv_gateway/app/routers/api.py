from fastapi import APIRouter

from . import auth, patients, users

router = APIRouter(prefix="/api", tags=["api"])


router.include_router(auth.router)
router.include_router(users.router)
router.include_router(patients.router)
