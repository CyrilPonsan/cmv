# Import des dépendances nécessaires
from typing import Annotated
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from ..utils.config import SECRET_KEY, ALGORITHM

# Configuration du schéma OAuth2 avec l'URL du endpoint de token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def check_authorization(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """
    Vérifie et décode le token JWT fourni, extrait le user_id.

    Args:
        token: Le token JWT à vérifier, injecté par FastAPI via le schéma OAuth2

    Returns:
        dict: Les données décodées du token si valide, contenant user_id

    Raises:
        HTTPException: 
            - 401 Unauthorized si le token est manquant ou invalide
            - 403 Forbidden si le token est expiré
            - 500 Internal Server Error si une erreur survient pendant le décodage
    """
    try:
        # Décodage du token JWT avec la clé secrète
        payload: dict = jwt.decode(token, SECRET_KEY or "", algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        # Erreur si le token est expiré (Requirement 2.2)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="token_expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        # Erreur si le token est invalide (Requirement 2.1)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        # Erreur générique lors du traitement du token
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the token",
        )

    # Vérification que le payload n'est pas vide
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extraction du user_id du payload (Requirement 2.3)
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
