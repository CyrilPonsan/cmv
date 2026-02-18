"""Dépendance pour obtenir une session de base de données."""

from typing import Generator

from sqlalchemy.orm import Session

from ..utils.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Crée et gère une session de base de données.

    Yields:
        Session: Une session de base de données active

    Note:
        La session est automatiquement fermée après utilisation grâce au bloc finally
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
