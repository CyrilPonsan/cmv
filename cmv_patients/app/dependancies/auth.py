# Import des dépendances nécessaires
from typing import Annotated
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from .redis import redis_client
from ..utils.config import SECRET_KEY, ALGORITHM

# Initialisation du client Redis
redis = redis_client

# Configuration du schéma OAuth2 avec l'URL du endpoint de token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuration du contexte de hachage des mots de passe avec bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
            status_code=status.HTTP_401_UNAUTHORIZED,
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
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="not_authorized"
        )

    return payload
