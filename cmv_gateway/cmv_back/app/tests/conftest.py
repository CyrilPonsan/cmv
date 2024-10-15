import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fakeredis import FakeStrictRedis

from app.dependancies.db_session import get_db
from app.sql.models import Base
from app.main import app
from app.dependancies.redis import redis_client

DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_app():
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        database = TestingSessionLocal()
        try:
            yield database
        finally:
            database.close()

    app.dependency_overrides[get_db] = override_get_db

    Base.metadata.create_all(bind=engine)

    yield app

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_app):
    with TestClient(test_app) as client:
        yield client


@pytest.fixture(scope="function")
def db(test_app):
    engine = create_engine(DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def redis():
    fake_redis = FakeStrictRedis()

    def override_get_redis():
        return fake_redis

    app.dependency_overrides[redis_client] = override_get_redis

    yield fake_redis

    fake_redis.flushall()
