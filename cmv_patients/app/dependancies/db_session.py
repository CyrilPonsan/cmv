from app.utils.database import SessionLocal


# Dépendance pour obtenir une session de base de données
def get_db():
    """
    Crée et gère une session de base de données.

    Yields:
        SessionLocal: Une session de base de données active

    Note:
        La session est automatiquement fermée après utilisation grâce au bloc finally
    """
    # Création d'une nouvelle session de base de données
    db = SessionLocal()
    try:
        # Retourne la session pour utilisation
        yield db
    finally:
        # Fermeture de la session une fois terminée
        db.close()
