"""
Ce service gère la logique métier des endpoints liés à la connexion,
déconnexion et à l'authentification de manière générale.
Il n'est pas implémenté en suivant le pattern du singleton car le cas
d'utilisation ne le justifie pas.
Ce service est injecté sous forme de dépendances dans les endpoints
qui en ont besoin.
"""

# Import des modules standards Python
from datetime import timedelta

# Import des modules FastAPI
from fastapi import HTTPException, Request, Response, status

# Import des modules SQLAlchemy et JWT
from sqlalchemy.orm import Session
from jose import jwt

# Import des dépendances internes pour l'authentification
from app.dependancies.auth import (
    authenticate_user,
    create_session,
    create_token,
)

# Import du client Redis
from app.dependancies.redis import redis_client

# Import des schémas et modèles
from app.schemas.user import User

# Import des configurations
from app.utils.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM,
)

# Import du logger personnalisé
from app.utils.logging_setup import LoggerSetup


# Fonction factory pour créer une instance du service d'authentification
def get_auth_service():
    return AuthService(
        access_token_expire_minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES),
        refresh_token_expire_minutes=int(REFRESH_TOKEN_EXPIRE_MINUTES),
        algorithm=ALGORITHM,
        secret_key=SECRET_KEY,
    )


class AuthService:
    # Initialisation du logger pour la classe
    logger = LoggerSetup()

    def __init__(
        self,
        access_token_expire_minutes: int,
        refresh_token_expire_minutes: int,
        algorithm: str,
        secret_key: str,
    ):
        """
        Initialise le service d'authentification avec les paramètres nécessaires
        pour la génération et la validation des tokens
        """
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_minutes = refresh_token_expire_minutes
        self.algorithm = algorithm
        self.secret_key = secret_key

    async def _create_and_set_tokens(
        self,
        user_id: str,
        response: Response,
    ) -> dict:
        """
        Crée une nouvelle session et génère les tokens d'accès et de rafraîchissement

        Args:
            user_id: Identifiant de l'utilisateur
            response: Objet Response pour définir les cookies

        Returns:
            Tuple contenant le token d'accès, le token de rafraîchissement et l'ID de session
        """
        # Création d'une nouvelle session pour l'utilisateur
        session_id = await create_session(user_id)

        # Génération du token d'accès avec une durée de validité limitée
        access_token = await create_token(
            data={
                "sub": str(user_id),
                "session_id": session_id,
            },
            expires_delta=timedelta(minutes=self.access_token_expire_minutes),
        )

        # Génération du token de rafraîchissement avec une durée de validité plus longue
        refresh_token = await create_token(
            data={
                "sub": str(user_id),
                "session_id": session_id,
            },
            expires_delta=timedelta(minutes=self.refresh_token_expire_minutes),
        )

        # Configuration des cookies sécurisés pour les deux tokens
        for token_type, token in [
            ("access_token", access_token),
            ("refresh_token", refresh_token),
        ]:
            response.set_cookie(
                key=token_type,
                value=token,
                httponly=True,  # Protection XSS
                secure=True,  # Uniquement en HTTPS
                samesite="Lax",  # Protection CSRF
            )

        return access_token, refresh_token, session_id

    async def login(
        self,
        db: Session,
        request: Request,
        response: Response,
        username: str,
        password: str,
    ) -> User:
        """
        Authentifie un utilisateur et configure sa session

        Args:
            db: Session de base de données
            request: Requête HTTP entrante
            response: Réponse HTTP sortante
            username: Nom d'utilisateur
            password: Mot de passe

        Returns:
            User: L'utilisateur authentifié
        """
        # Vérifie les identifiants de l'utilisateur
        user = await authenticate_user(db, username, password, request)

        # Crée et configure les tokens pour l'utilisateur
        await self._create_and_set_tokens(user.id_user, response)

        # Enregistre la connexion dans les logs
        self.logger.write_log(f"{user.role.name} connection ", request)
        return user

    async def signout(self, request: Request, response: Response) -> dict:
        """
        Déconnecte un utilisateur en invalidant sa session et ses tokens

        Args:
            request: Requête HTTP entrante
            response: Réponse HTTP sortante

        Returns:
            dict: Message de confirmation
        """
        # Récupération des tokens dans les cookies
        token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        if not token or not refresh_token:
            raise HTTPException(status_code=400, detail="Aucun token trouvé")

        try:
            # Extraction des informations du token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            session_id = payload.get("session_id")
            user_id = payload.get("sub")

            # Nettoyage des données de session
            if session_id:
                await redis_client.delete(f"session:{session_id}")
            # Blacklist des tokens pour empêcher leur réutilisation
            await redis_client.setex(f"blacklist:{token}", 3600, "true")
            await redis_client.setex(f"blacklist:{refresh_token}", 3600, "true")

            # Suppression des cookies
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

    async def refresh(self, request: Request, response: Response) -> dict:
        """
        Rafraîchit les tokens d'authentification d'un utilisateur

        Args:
            request: Requête HTTP entrante
            response: Réponse HTTP sortante

        Returns:
            dict: Message de confirmation
        """
        # Récupération du token de rafraîchissement
        refresh_token = request.cookies.get("refresh_token")

        # Vérification si le token est blacklisté
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
            # Validation et décodage du token
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

        # Extraction des informations du token
        user_id = payload.get("sub")
        session_id = payload.get("session_id")

        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="no_session_found"
            )

        # Vérification de l'existence de la session
        session_exists = await redis_client.exists(f"session:{session_id}")
        if not session_exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="session_not_found"
            )

        # Nettoyage de l'ancienne session
        await redis_client.delete(f"session:{session_id}")
        await redis_client.setex(f"blacklist:{refresh_token}", 3600, "true")

        # Génération de nouveaux tokens
        await self._create_and_set_tokens(user_id, response)

        return {"message": "Token rafraîchi avec succès"}
