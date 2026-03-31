"""Tests pour ChambresSettings — validation des variables d'environnement."""

import pytest
from pydantic import ValidationError

from app.utils.config import ChambresSettings, WEAK_SECRETS


VALID_PARAMS = {
    "CHAMBRES_DATABASE_URL": "postgresql://postgres:pwd@localhost:6003/cmv_chambres",
    "SECRET_KEY": "une-cle-valide-de-32-caracteres-ok",
    "_env_file": None,
}


def _make(**overrides):
    return ChambresSettings(**{**VALID_PARAMS, **overrides})


# --- Instanciation réussie ---


def test_valid_config():
    s = _make()
    assert s.CHAMBRES_DATABASE_URL == VALID_PARAMS["CHAMBRES_DATABASE_URL"]
    assert s.ALGORITHM == "HS256"
    assert s.ENVIRONMENT in ("dev", "test", "staging", "production")


def test_asyncpg_url_accepted():
    s = _make(CHAMBRES_DATABASE_URL="postgresql+asyncpg://postgres:pwd@localhost/db")
    assert s.CHAMBRES_DATABASE_URL.startswith("postgresql+asyncpg://")


# --- Variables obligatoires manquantes ---


@pytest.mark.parametrize("missing", ["CHAMBRES_DATABASE_URL", "SECRET_KEY"])
def test_missing_required_field(missing):
    params = {**VALID_PARAMS}
    del params[missing]
    with pytest.raises(ValidationError) as exc_info:
        ChambresSettings(**params)
    assert missing in str(exc_info.value)


# --- URL PostgreSQL invalide ---


@pytest.mark.parametrize("bad_url", [
    "mysql://postgres:pwd@localhost/db",
    "sqlite:///test.db",
    "",
    "not-a-url",
])
def test_invalid_db_url_rejected(bad_url):
    with pytest.raises(ValidationError, match="PostgreSQL"):
        _make(CHAMBRES_DATABASE_URL=bad_url)


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


def test_valid_secret_key_in_production(monkeypatch):
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    long_key = "a" * 32
    s = _make(SECRET_KEY=long_key, ENVIRONMENT="production")
    assert s.SECRET_KEY == long_key


# --- ENVIRONMENT invalide ---


def test_invalid_environment_rejected(monkeypatch):
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    with pytest.raises(ValidationError):
        _make(ENVIRONMENT="invalid")
