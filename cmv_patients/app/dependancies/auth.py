# Import des dépendances nécessaires
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.dependancies.db_session import get_db
from app.schemas.user import InternalPayload
from app.utils.config import CHAMBRES_SECRET_KEY

from ..utils.config import ALGORITHM, SECRET_KEY

# Configuration du schéma OAuth2 avec l'URL du endpoint de token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def check_authorization(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """
    Vérifie et décode le token JWT fourni.

    Args:
        token: Le token JWT à vérifier, injecté par FastAPI via le schéma OAuth2

    Returns:
        dict: Les données décodées du token si valide

    Raises:
        HTTPException: Si le token est invalide ou expiré (401)
                      Si une erreur survient pendant le décodage (500)
                      Si le payload est vide (403)
    """
    try:
        # Décodage du token JWT avec la clé secrète
        payload: dict = jwt.decode(token, SECRET_KEY or "", algorithms=[ALGORITHM])
    except JWTError:
        # Erreur si le token est invalide ou expiré
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not_authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        # Erreur générique lors du traitement du token
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the token",
        )

    # Vérification que le payload n'est pas vide
    if not payload or payload["source"] != "api_gateway":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="not_authorized"
        )

    return payload


async def get_permissions(
    internal_payload: Annotated[InternalPayload, Depends(check_authorization)],
) -> str:
    if not internal_payload:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="not_authorized"
        )
    token = {
        "user_id": internal_payload["user_id"],
        "role": internal_payload["role"],
        "exp": datetime.now() + timedelta(seconds=15),
        "source": "api_patients",
    }
    return jwt.encode(token, CHAMBRES_SECRET_KEY or "", algorithm=ALGORITHM or "")
