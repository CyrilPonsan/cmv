from fastapi import APIRouter

from . import auth, home, users

router = APIRouter(prefix="/api", tags=["api"])


router.include_router(auth.router)
router.include_router(users.router)
router.include_router(home.router)
