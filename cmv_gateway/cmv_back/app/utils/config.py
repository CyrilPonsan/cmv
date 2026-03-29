"""Configuration du microservice Gateway avec validation Pydantic."""

from typing import Literal
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensemble des valeurs de SECRET_KEY connues comme faibles
WEAK_SECRETS = {"cle_tres_secrete", "secret", "changez-moi", "password", "123456"}


class GatewaySettings(BaseSettings):
    """Paramètres de configuration du microservice Gateway.

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
    GATEWAY_DATABASE_URL: str
    TEST_DATABASE_URL: str = "sqlite:///:memory:"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_MAX_AGE: int = 30
    REFRESH_MAX_AGE: int = 1440

    # Services — obligatoires
    PATIENTS_SERVICE: str
    CHAMBRES_SERVICE: str
    ML_SERVICE: str

    # Environnement
    ENVIRONMENT: Literal["dev", "staging", "production", "test"] = "dev"

    # Valkey
    VALKEY_HOST: str = "redis"
    VALKEY_PORT: int = 6379
    PATIENTS_SECRET_KEY: str
    CHAMBRES_SECRET_KEY: str
    ML_SECRET_KEY: str

    @field_validator("GATEWAY_DATABASE_URL")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError(
                "GATEWAY_DATABASE_URL doit être une URL PostgreSQL valide"
            )
        return v

    @field_validator("PATIENTS_SERVICE", "CHAMBRES_SERVICE", "ML_SERVICE")
    @classmethod
    def validate_service_urls(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError(
                "L'URL de service doit commencer par http:// ou https://"
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
settings = GatewaySettings()

# Aliases pour la compatibilité avec le code existant
DATABASE_URL = settings.GATEWAY_DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_MAX_AGE
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_MAX_AGE
ENVIRONMENT = settings.ENVIRONMENT
PATIENTS_SERVICE = settings.PATIENTS_SERVICE
CHAMBRES_SERVICE = settings.CHAMBRES_SERVICE
ML_SERVICE = settings.ML_SERVICE
VALKEY_HOST = settings.VALKEY_HOST
VALKEY_PORT = settings.VALKEY_PORT
PATIENTS_SECRET_KEY = settings.PATIENTS_SECRET_KEY
CHAMBRES_SECRET_KEY = settings.CHAMBRES_SECRET_KEY
ML_SECRET_KEY = settings.ML_SECRET_KEY