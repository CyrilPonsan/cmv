import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from passlib.context import CryptContext

from app.dependancies.db_session import get_db
from app.sql.models import Base, Role, User
from app.main import app

DATABASE_URL = "sqlite:///:memory:"


def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as asyncio")


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
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


@pytest.fixture(scope="function")
def user(db_session):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("Toto@1234")

    role = Role(name="home", label="accueil")
    db_session.add(role)
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
