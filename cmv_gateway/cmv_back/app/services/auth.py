"""
Ce service gère la logique métier des endpoints liés à la connexion,
déconnexion et à l'authentification de manière générale.
Il n'est pas implémenté en suivant le pattern du singleton car le cas
d'utilisation ne le justifie pas.
Ce service est injecté sous forme de dépendances dans les endpoints
qui en ont besoin.
"""

from datetime import timedelta
from fastapi import HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from jose import jwt

from app.dependancies.auth import (
    authenticate_user,
    create_session,
    create_token,
)
from app.dependancies.redis import redis_client
from app.schemas.user import User
from app.utils.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM,
)
from app.utils.logging_setup import LoggerSetup


# Initialisation du service d'authentification
def get_auth_service():
    return AuthService(
        access_token_expire_minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES),
        refresh_token_expire_minutes=int(REFRESH_TOKEN_EXPIRE_MINUTES),
        algorithm=ALGORITHM,
        secret_key=SECRET_KEY,
    )


class AuthService:
    logger = LoggerSetup()

    def __init__(
        self,
        access_token_expire_minutes: int,
        refresh_token_expire_minutes: int,
        algorithm: str,
        secret_key: str,
    ):
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_minutes = refresh_token_expire_minutes
        self.algorithm = algorithm
        self.secret_key = secret_key

    # Méthode pour créer et configurer les tokens
    async def _create_and_set_tokens(
        self,
        user_id: str,
        response: Response,
    ) -> dict:
        # Création d'une session
        session_id = await create_session(user_id)

        # Création des tokens
        access_token = await create_token(
            data={
                "sub": str(user_id),
                "session_id": session_id,
            },
            expires_delta=timedelta(minutes=self.access_token_expire_minutes),
        )

        refresh_token = await create_token(
            data={
                "sub": str(user_id),
                "session_id": session_id,
            },
            expires_delta=timedelta(minutes=self.refresh_token_expire_minutes),
        )

        # Configuration des cookies
        for token_type, token in [
            ("access_token", access_token),
            ("refresh_token", refresh_token),
        ]:
            response.set_cookie(
                key=token_type,
                value=token,
                httponly=True,
                secure=True,
                samesite="Lax",
            )

        return access_token, refresh_token, session_id

    # Méthode pour vérifier les identifiants et créer les tokens
    async def login(
        self,
        db: Session,
        request: Request,
        response: Response,
        username: str,
        password: str,
    ) -> User:
        # Authentification de l'utilisateur
        user = await authenticate_user(db, username, password, request)

        # Utilisation de la nouvelle méthode pour créer et configurer les tokens
        await self._create_and_set_tokens(user.id_user, response)

        # Log de l'événement
        self.logger.write_log(f"{user.role.name} connection ", request)
        return user

    # Méthode pour la déconnexion
    async def signout(self, request: Request, response: Response) -> dict:
        # Récupération du token dans les cookies
        token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        if not token or not refresh_token:
            raise HTTPException(status_code=400, detail="Aucun token trouvé")

        try:
            # Décodage du token pour extraire la session et l'utilisateur
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            session_id = payload.get("session_id")
            user_id = payload.get("sub")

            # Suppression de la session et ajout du token à la blacklist
            if session_id:
                await redis_client.delete(f"session:{session_id}")
            await redis_client.setex(f"blacklist:{token}", 3600, "true")
            await redis_client.setex(f"blacklist:{refresh_token}", 3600, "true")

            # Suppression du cookie d'accès
            response.delete_cookie(key="access_token", path="/", domain=None)
            response.delete_cookie(key="refresh_token", path="/", domain=None)
            # Log de la déconnexion
            if user_id:
                self.logger.write_log(f"{user_id} déconnection ", request)

            return {"message": "Déconnexion réussie"}

        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide",
            )

    # Méthode de rafraîchissement du token
    async def refresh(self, request: Request, response: Response) -> dict:
        # On récupère le refresh token au lieu du access token
        refresh_token = request.cookies.get("refresh_token")
        # vérifie que le token ne soit pas blacklist
        is_blacklisted = await redis_client.get(f"blacklist:{refresh_token}")
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="refresh_token_blacklisted",
            )
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="no_refresh_token",
            )

        try:
            # On décode le refresh token
            payload = jwt.decode(
                refresh_token, self.secret_key, algorithms=[self.algorithm]
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="refresh_token_expired",
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="not_valid_token",
            )

        user_id = payload.get("sub")
        session_id = payload.get("session_id")

        if not session_id:
            raise HTTPException(status_code=403, detail="no_session_found")

        # Vérifie que la session existe
        session_exists = await redis_client.exists(f"session:{session_id}")
        if not session_exists:
            raise HTTPException(status_code=403, detail="session_not_found")

        # Suppression de l'ancienne session et blacklist de l'ancien token
        await redis_client.delete(f"session:{session_id}")
        await redis_client.setex(f"blacklist:{refresh_token}", 3600, "true")

        # Utilisation de la nouvelle méthode pour créer et configurer les tokens
        await self._create_and_set_tokens(user_id, response)

        return {"message": "Token rafraîchi avec succès"}
