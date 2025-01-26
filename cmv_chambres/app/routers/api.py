from fastapi import APIRouter

from app.routers import services
from app.routers import chambres

router = APIRouter(prefix="/api", tags=["api"])

router.include_router(services.router)
router.include_router(chambres.router)
