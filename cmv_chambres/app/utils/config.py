"""Configuration du microservice Chambres avec validation Pydantic."""

from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensemble des valeurs de SECRET_KEY connues comme faibles
WEAK_SECRETS = {"cle_tres_secrete", "secret", "changez-moi", "password", "123456"}


class ChambresSettings(BaseSettings):
    """Paramètres de configuration du microservice Chambres.

    Charge les variables depuis les variables d'environnement système
    (priorité) puis depuis le fichier .env.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Base de données — obligatoire
    CHAMBRES_DATABASE_URL: str

    # JWT — SECRET_KEY obligatoire, ALGORITHM avec défaut
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Environnement
    ENVIRONMENT: Literal["dev", "staging", "production", "test"] = "dev"

    @field_validator("CHAMBRES_DATABASE_URL")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError(
                "CHAMBRES_DATABASE_URL doit être une URL PostgreSQL valide"
            )
        return v

    def model_post_init(self, __context) -> None:
        if self.ENVIRONMENT == "production":
            if len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "SECRET_KEY doit avoir au moins 32 caractères en production"
                )
            if self.SECRET_KEY in WEAK_SECRETS:
                raise ValueError("SECRET_KEY utilise une valeur faible connue")


# Singleton — instancié une seule fois au démarrage
settings = ChambresSettings()

# Aliases pour la compatibilité avec le code existant
DATABASE_URL = settings.CHAMBRES_DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ENVIRONMENT = settings.ENVIRONMENT
