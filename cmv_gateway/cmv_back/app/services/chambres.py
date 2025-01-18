import httpx

from fastapi import HTTPException, Request

from app.utils.config import CHAMBRES_SERVICE


def get_chambres_service():
    print(CHAMBRES_SERVICE)
    return ChambresService(url_api_chambres=CHAMBRES_SERVICE)


class ChambresService:
    def __init__(
        self,
        url_api_chambres: str,
    ):
        self.url_api_chambres = url_api_chambres

    async def get_chambres(
        self, path: str, request: Request, client: httpx.AsyncClient
    ):
        full_path = path
        if request.query_params:
            full_path = f"{path}?{request.query_params}"
        url = f"{self.url_api_chambres}/{full_path}"

        response = await client.get(
            url,
            # headers={"Authorization": f"Bearer {internal_token}"},
            follow_redirects=True,
        )
        if response.status_code == 200:
            return response.json()
        else:
            result = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=result["detail"] or "server_issue",
            )
