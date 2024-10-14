import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import timedelta
from passlib.context import CryptContext

from app.main import app  # Adjust this import based on your project structure
from app.dependancies.auth import authenticate_user, create_access_token, create_session
from app.schemas.user import User, Role, UserCreate

# Create a test client
client = TestClient(app)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash("Abcd@1234")

# Mock user data
mock_user = UserCreate(
    id_user="123",
    username="test@example.com",
    password=hashed_password,
    is_active=True,
    role=Role(id=1, name="user")
)

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.mark.asyncio
async def test_login_success(mock_db):
    with patch("app.dependancies.auth.authenticate_user", new_callable=AsyncMock) as mock_auth, \
         patch("app.dependancies.auth.create_access_token", new_callable=AsyncMock) as mock_token, \
         patch("app.dependancies.auth.create_session", new_callable=AsyncMock) as mock_session:
        
        mock_auth.return_value = mock_user
        mock_token.return_value = "fake_access_token"
        mock_session.return_value = "fake_session_id"

        response = client.post("/api/auth/login", json={"username": "test@example.com", "password": "Abcd@1234"})
        print(f"response : {response}")
        assert response.status_code == 200
        assert response.json() == {"message": "all good bro!"}
        assert "access_token" in response.cookies
        assert response.cookies["access_token"] == "fake_access_token"

        mock_auth.assert_called_once_with(mock_db,  "test@example.com", "Abcd@1234")
        mock_token.assert_called_once()
        mock_session.assert_called_once_with(mock_user.id_user)

@pytest.mark.asyncio
async def test_login_invalid_credentials(mock_db):
    with patch("app.routers.auth.authenticate_user", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = None

        response = client.post("/login", json={"username": "wrong@user.gg", "password": "Abcd@1234"})

        assert response.status_code == 400
        assert response.json() == {"detail": "Incorrect username or password"}

"""
@pytest.mark.asyncio
async def test_login_inactive_user(mock_db):
    inactive_user = User(
        id_user="456",
        username="inactiveuser",
        email="inactive@example.com",
        is_active=False,
        role=Role(name="user")
    )

    with patch("app.routers.auth.authenticate_user", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = inactive_user

        response = client.post("/login", json={"username": "inactiveuser", "password": "password123"})

        assert response.status_code == 400
        assert response.json() == {"detail": "Incorrect username or password"}

@pytest.mark.asyncio
async def test_login_exception_handling(mock_db):
    with patch("app.routers.auth.authenticate_user", new_callable=AsyncMock) as mock_auth:
        mock_auth.side_effect = Exception("Unexpected error")

        response = client.post("/login", json={"username": "testuser", "password": "password123"})

        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

"""
# Additional tests can be added here to cover more scenarios