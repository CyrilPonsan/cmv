"""Fixtures partagées pour les tests du microservice Chambres."""
from datetime import datetime, timedelta
import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.dependancies.db_session import get_db
from app.main import app
from app.sql.models import Base, Chambre, Service, Status
from app.utils.config import ALGORITHM, SECRET_KEY

DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    return create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

@pytest.fixture(scope="function")
def db_session(engine):
    Base.metadata.create_all(engine)
    S = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = S()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

@pytest.fixture
def internal_token():
    p = {"user_id": 1, "role": "home", "exp": datetime.now() + timedelta(minutes=15), "source": "api_gateway"}
    return jwt.encode(p, SECRET_KEY or "", algorithm=ALGORITHM or "")

@pytest.fixture
def wrong_internal_token():
    p = {"user_id": 1, "role": "home", "exp": datetime.now() + timedelta(minutes=15), "source": "api_gateway"}
    return jwt.encode(p, "WRONG_KEY", algorithm=ALGORITHM or "")

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

@pytest.fixture(scope="function")
def services_and_chambres(db_session):
    s1 = Service(nom="Cardiologie")
    s2 = Service(nom="Neurologie")
    db_session.add_all([s1, s2])
    db_session.flush()
    now = datetime.now()
    chambres = [
        Chambre(nom="C101", status=Status.LIBRE, dernier_nettoyage=now, service_id=s1.id_service),
        Chambre(nom="C102", status=Status.OCCUPEE, dernier_nettoyage=now, service_id=s1.id_service),
        Chambre(nom="C201", status=Status.LIBRE, dernier_nettoyage=now, service_id=s2.id_service),
    ]
    db_session.add_all(chambres)
    db_session.commit()
    return {"services": [s1, s2], "chambres": chambres}
