from datetime import datetime, timedelta
from app.sql import models
from app.utils.config import ALGORITHM, SECRET_KEY
import pytest
from redis.asyncio import Redis
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from jose import jwt

from app.dependancies.db_session import get_db
from app.sql.models import Base
from app.main import app

DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
async def redis_client():
    client = Redis.from_url("redis://redis:6379", decode_responses=True)
    yield client
    await client.aclose()


@pytest.fixture(scope="session")
def engine():
    return create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


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


@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(app=app, base_url="http://test") as client:
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


# Retourne un cookie avec un jeton d'accès qui sera utilisé pour tester les routes protégées
@pytest.fixture
async def wrong_internal_token():
    internal_payload = {
        "user_id": 1,
        "role": "home",
        "exp": datetime.now() + timedelta(minutes=15),
        "source": "api_gateway",
    }
    return jwt.encode(internal_payload, "SECRET_KEY" or "", algorithm=ALGORITHM or "")


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


# Création d'une vingtaine de patients pour tester la pagination
@pytest.fixture(scope="function")
def patients(db_session):
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
    db_session.add_all(patients)
    db_session.commit()
    patient = (
        db_session.query(models.Patient).filter(models.Patient.id_patient == 1).first()
    )
    documents: list[models.Document] = []
    for i in range(0, 2):
        document = models.Document(
            nom_fichier=f"document_test_{i}",
            type_document="MISCELLANEOUS",
        )
        documents.append(document)
    patient.documents = documents
    db_session.add(patient)
    db_session.commit()
    return patients
