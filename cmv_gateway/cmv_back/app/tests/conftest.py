import asyncio
import pytest
from redis.asyncio import Redis
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from passlib.context import CryptContext

from app.dependancies.db_session import get_db
from app.services.patients import PatientsService, get_patients_service
from app.sql.models import Base, Permission, Role, User
from app.main import app

# URL de la base de données SQLite en mémoire pour les tests
DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Crée une boucle d'événements asyncio pour les tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def redis_client():
    """Configure et fournit un client Redis pour les tests."""
    client = Redis.from_url("redis://redis:6379", decode_responses=True)
    yield client
    await client.aclose()


@pytest.fixture(scope="session")
def engine():
    """Crée et configure le moteur SQLAlchemy pour les tests."""
    return create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture(scope="function")
def db_session(engine):
    """
    Crée une session de base de données pour chaque test.
    Nettoie la base de données après chaque test.
    """
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
    """Crée un client HTTP asynchrone pour les tests d'API."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture(scope="function")
def user(db_session):
    """
    Crée un utilisateur de test avec un rôle et des permissions.
    Retourne l'utilisateur créé.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("Toto@1234")

    role = Role(name="home", label="Service Accueil")
    db_session.add(role)
    db_session.commit()

    permission = Permission(role=role, action="get", resource="patients")
    db_session.add(permission)
    db_session.commit()

    user = User(
        username="test.user@test.fr",
        password=hashed_password,
        prenom="test",
        nom="test",
        is_active=True,
        service="home",
        role=role,
    )
    db_session.add(user)
    db_session.commit()

    return user


@pytest.fixture
async def auth_cookie(ac, user):
    """
    Génère un cookie d'authentification en simulant une connexion utilisateur.
    Retourne le cookie contenant le jeton d'accès.
    """
    response = await ac.post(
        "/api/auth/login",
        json={"username": user.username, "password": "Toto@1234"},
    )
    assert response.status_code == 200
    return response.cookies.get("access_token")


@pytest.fixture
def mock_patients_service():
    """Crée un service mock pour les patients."""
    return PatientsService(url_api_patients="http://mock-patients-service")


@pytest.fixture(autouse=True)
def override_dependency(db_session, mock_patients_service):
    """
    Remplace les dépendances de l'application par des versions de test.
    Restaure les dépendances originales après les tests.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    def override_get_patients_service():
        return mock_patients_service

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_patients_service] = override_get_patients_service
    yield
    del app.dependency_overrides[get_db]
    del app.dependency_overrides[get_patients_service]
