from fastapi import APIRouter

from app.routers import services

router = APIRouter(prefix="/api", tags=["api"])

router.include_router(services.router)
