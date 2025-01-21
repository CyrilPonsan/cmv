from fastapi import APIRouter, Depends, Request

from app.services.chambres import get_chambres_service
from app.dependancies.httpx_client import get_http_client

router = APIRouter(prefix="/chambres", tags=["chambres"])


@router.get("/{path:path}")
async def read_all_chambres(
    path: str,
    request: Request,
    chambres_service=Depends(get_chambres_service),
    client=Depends(get_http_client),
):
    return await chambres_service.get_chambres(
        path=path, request=request, client=client
    )
