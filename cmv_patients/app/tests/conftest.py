# Imports nécessaires pour les tests
from datetime import datetime, timedelta
from app.sql import models
from app.utils.config import ALGORITHM, SECRET_KEY
import pytest
from redis.asyncio import Redis
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from jose import jwt

from app.dependancies.db_session import get_db
from app.sql.models import Base
from app.main import app

# URL de la base de données de test en mémoire
DATABASE_URL = "sqlite:///:memory:"


# Fixture pour le client Redis
@pytest.fixture(scope="session")
async def redis_client():
    client = Redis.from_url("redis://redis:6379", decode_responses=True)
    yield client
    await client.aclose()


# Fixture pour créer le moteur SQLAlchemy
@pytest.fixture(scope="session")
def engine():
    return create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


# Fixture pour créer une session de base de données
@pytest.fixture(scope="function")
def db_session(engine):
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


# Fixture pour créer un client HTTP asynchrone
@pytest.fixture(scope="function")
async def ac():
    """Crée un client HTTP asynchrone pour les tests d'API."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


# Retourne un cookie avec un jeton d'accès qui sera utilisé pour tester les routes protégées
@pytest.fixture
async def internal_token():
    internal_payload = {
        "user_id": 1,
        "role": "home",
        "exp": datetime.now() + timedelta(minutes=15),
        "source": "api_gateway",
    }
    return jwt.encode(internal_payload, SECRET_KEY or "", algorithm=ALGORITHM or "")


# Retourne un cookie avec un jeton d'accès invalide pour tester les cas d'erreur
@pytest.fixture
async def wrong_internal_token():
    internal_payload = {
        "user_id": 1,
        "role": "home",
        "exp": datetime.now() + timedelta(minutes=15),
        "source": "api_gateway",
    }
    return jwt.encode(internal_payload, "SECRET_KEY" or "", algorithm=ALGORITHM or "")


# Fixture pour remplacer la dépendance de base de données par notre session de test
@pytest.fixture(autouse=True)
def override_dependency(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    del app.dependency_overrides[get_db]


# Fixture pour créer un jeu de données de test avec des patients et des documents
@pytest.fixture(scope="function")
def patients(db_session):
    # Création d'une liste de 20 patients
    patients: list[models.Patient] = []
    for i in range(0, 20):
        patient = models.Patient(
            civilite="AUTRE",
            nom=f"nom_test_{i}",
            prenom=f"prenom_test_{i}",
            adresse="2 rue truc muche",
            code_postal="64000",
            ville="gelos",
            telephone="06.66.69.96.99",
            date_de_naissance=datetime(year=1969, month=7, day=21),
        )
        patients.append(patient)

    # Ajout d'un patient supplémentaire nommé "toto"
    patient = models.Patient(
        civilite="AUTRE",
        nom="toto",
        prenom=f"prenom_test_{i}",
        adresse="2 rue truc muche",
        code_postal="64000",
        ville="gelos",
        telephone="06.66.69.96.99",
        date_de_naissance=datetime(year=1969, month=7, day=21),
    )
    patients.append(patient)

    # Sauvegarde des patients dans la base de données
    db_session.add_all(patients)
    db_session.commit()

    # Récupération du premier patient pour lui ajouter des documents
    patient = (
        db_session.query(models.Patient).filter(models.Patient.id_patient == 1).first()
    )

    # Création et association de 2 documents au premier patient
    documents: list[models.Document] = []
    for i in range(0, 2):
        document = models.Document(
            nom_fichier=f"document_test_{i}",
            type_document="MISCELLANEOUS",
        )
        documents.append(document)
    patient.documents = documents

    # Sauvegarde des modifications
    db_session.add(patient)
    db_session.commit()
    return patients
