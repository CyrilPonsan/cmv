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
    create_access_token,
    create_session,
)
from app.dependancies.redis import redis_client
from app.schemas.user import User
from app.utils.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from app.utils.logging_setup import LoggerSetup


# Initialisation du service d'authentification
def get_auth_service():
    return AuthService(
        access_token_expire_minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES),
        algorithm=ALGORITHM,
        secret_key=SECRET_KEY,
    )


class AuthService:
    logger = LoggerSetup()

    def __init__(
        self, access_token_expire_minutes: int, algorithm: str, secret_key: str
    ):
        self.access_token_expire_minutes = access_token_expire_minutes
        self.algorithm = algorithm
        self.secret_key = secret_key

    # Méthode d'instance pour le login
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

        # Création d'un token JWT avec expiration
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = await create_access_token(
            data={
                "sub": str(user.id_user),
                "session_id": await create_session(user.id_user),
            },
            expires_delta=access_token_expires,
        )

        # Ajout du token dans le cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        # Log de l'événement
        self.logger.write_log(f"{user.role.name} connection ", request)
        return user

    # Méthode d'instance pour la déconnexion (logout)
    async def signout(self, request: Request, response: Response) -> dict:
        # Récupération du token dans les cookies
        token = request.cookies.get("access_token")
        if not token:
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

            # Suppression du cookie d'accès
            response.delete_cookie(key="access_token", path="/", domain=None)

            # Log de la déconnexion
            if user_id:
                self.logger.write_log(f"{user_id} déconnection ", request)

            return {"message": "Déconnexion réussie"}

        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide",
            )
