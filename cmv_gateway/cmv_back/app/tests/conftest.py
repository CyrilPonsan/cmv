import asyncio
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
import pytest
import pytest_asyncio
from redis.asyncio import Redis
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from passlib.context import CryptContext

from app.dependancies.db_session import get_db
from app.dependancies.httpx_client import get_http_client
from app.services.patients import PatientsService
from app.sql.models import Base, Permission, Role, User
from app.main import app

DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


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


# Créé un utilisateur test dans la bdd
@pytest.fixture(scope="function")
def user(db_session):
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


# Retourne un cookie avec un jeton d'accès qui sera utilisé pour tester les routes protégées
@pytest.fixture
async def auth_cookie(ac, user):
    response = await ac.post(
        "/api/auth/login",
        json={"username": user.username, "password": "Toto@1234"},
    )
    assert response.status_code == 200
    return response.cookies.get("access_token")


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


# Mocker la dépendance pour get_dynamic_permissions
@pytest_asyncio.fixture
def mock_dynamic_permissions(user):
    return user


@pytest_asyncio.fixture
async def mock_httpx_client(mocker):
    # Créer un mock pour PatientsService
    mock_service = mocker.Mock(spec=PatientsService)
    # Simuler la méthode get_patients
    mock_service.get_patients = AsyncMock(return_value={"data": "mocked_data"})
    return mock_service


@pytest.fixture
def mock_http_client():
    mock_client = AsyncMock(spec=AsyncClient)
    return mock_client


@pytest.fixture
def client(mock_http_client):
    app.dependency_overrides[get_http_client] = lambda: mock_http_client
    return TestClient(app)
