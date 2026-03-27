"""Tests unitaires pour GatewaySettings — validation des variables d'environnement."""

import pytest
from pydantic import ValidationError

from app.utils.config import GatewaySettings, WEAK_SECRETS


# --- Helpers ---

VALID_PARAMS = {
    "GATEWAY_DATABASE_URL": "postgresql://postgres:pwd@localhost:6001/cmv_gateway",
    "SECRET_KEY": "une-cle-valide-de-32-caracteres-ok",
    "PATIENTS_SERVICE": "http://localhost:8002/api",
    "CHAMBRES_SERVICE": "http://localhost:8003/api",
    "ML_SERVICE": "http://localhost:8004",
    "_env_file": None,  # Isoler du .env présent dans le container
}


def _make(**overrides):
    """Crée un GatewaySettings avec des paramètres valides, surchargés par overrides."""
    return GatewaySettings(**{**VALID_PARAMS, **overrides})


# --- Instanciation réussie ---


def test_valid_config():
    s = _make()
    assert s.GATEWAY_DATABASE_URL == VALID_PARAMS["GATEWAY_DATABASE_URL"]
    assert s.SECRET_KEY == VALID_PARAMS["SECRET_KEY"]
    assert s.PATIENTS_SERVICE == VALID_PARAMS["PATIENTS_SERVICE"]


def test_valid_config_asyncpg_url():
    s = _make(GATEWAY_DATABASE_URL="postgresql+asyncpg://postgres:pwd@localhost/db")
    assert s.GATEWAY_DATABASE_URL.startswith("postgresql+asyncpg://")


# --- Valeurs par défaut ---


def test_default_values(monkeypatch):
    # Supprimer les variables système qui écrasent les défauts
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("VALKEY_HOST", raising=False)
    monkeypatch.delenv("VALKEY_PORT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    s = _make()
    assert s.ALGORITHM == "HS256"
    assert s.ACCESS_MAX_AGE == 30
    assert s.REFRESH_MAX_AGE == 1440
    assert s.ENVIRONMENT == "dev"
    assert s.VALKEY_HOST == "redis"
    assert s.VALKEY_PORT == 6379
    assert s.TEST_DATABASE_URL == "sqlite:///:memory:"


# --- Variables obligatoires manquantes ---


@pytest.mark.parametrize("missing_field", [
    "GATEWAY_DATABASE_URL",
    "SECRET_KEY",
    "PATIENTS_SERVICE",
    "CHAMBRES_SERVICE",
    "ML_SERVICE",
])
def test_missing_required_field(missing_field):
    params = {**VALID_PARAMS}
    del params[missing_field]
    with pytest.raises(ValidationError) as exc_info:
        GatewaySettings(**params)
    assert missing_field in str(exc_info.value)


# --- Rejet d'URLs PostgreSQL invalides ---


@pytest.mark.parametrize("bad_url", [
    "mysql://postgres:pwd@localhost/db",
    "ftp://postgres:pwd@localhost/db",
    "http://localhost:5432/db",
    "sqlite:///test.db",
    "",
    "not-a-url",
])
def test_invalid_postgres_url_rejected(bad_url):
    with pytest.raises(ValidationError, match="PostgreSQL"):
        _make(GATEWAY_DATABASE_URL=bad_url)


# --- Rejet d'URLs de services invalides ---


@pytest.mark.parametrize("field", [
    "PATIENTS_SERVICE",
    "CHAMBRES_SERVICE",
    "ML_SERVICE",
])
@pytest.mark.parametrize("bad_url", [
    "ftp://localhost:8002",
    "tcp://localhost:8002",
    "",
    "not-a-url",
])
def test_invalid_service_url_rejected(field, bad_url):
    with pytest.raises(ValidationError, match="http://"):
        _make(**{field: bad_url})


# --- SECRET_KEY en production ---


def test_short_secret_key_rejected_in_production(monkeypatch):
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    with pytest.raises(ValidationError, match="32 caractères"):
        _make(SECRET_KEY="trop-court", ENVIRONMENT="production")


@pytest.mark.parametrize("weak_key", list(WEAK_SECRETS))
def test_weak_secret_key_rejected_in_production(weak_key, monkeypatch):
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    with pytest.raises(ValidationError):
        _make(SECRET_KEY=weak_key, ENVIRONMENT="production")


def test_short_secret_key_accepted_in_dev():
    s = _make(SECRET_KEY="short", ENVIRONMENT="dev")
    assert s.SECRET_KEY == "short"


def test_valid_secret_key_accepted_in_production(monkeypatch):
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    long_key = "a" * 32
    s = _make(SECRET_KEY=long_key, ENVIRONMENT="production")
    assert s.SECRET_KEY == long_key


# --- ENVIRONMENT invalide ---


def test_invalid_environment_rejected(monkeypatch):
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    with pytest.raises(ValidationError):
        _make(ENVIRONMENT="invalid")


# --- URLs de services valides avec https ---


def test_https_service_urls_accepted():
    s = _make(
        PATIENTS_SERVICE="https://patients.prod.example.com/api",
        CHAMBRES_SERVICE="https://chambres.prod.example.com/api",
        ML_SERVICE="https://ml.prod.example.com",
    )
    assert s.PATIENTS_SERVICE.startswith("https://")
