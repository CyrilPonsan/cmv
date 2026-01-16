import pytest


@pytest.mark.asyncio
async def test_fixtures(ac):
    response = await ac.get("/fixtures")
    assert response.status_code == 200
    assert response.json() == {"message": "done"}


@pytest.mark.asyncio
async def test_login(ac, user):
    print(f"USER : {user.prenom}")
    response = await ac.post(
        "/api/auth/login",
        json={"username": "test.user@test.fr", "password": "MrToto@123456"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_wrong_user(ac, user):
    print(f"USER : {user.prenom}")
    response = await ac.post(
        "/api/auth/login",
        json={"username": "foo.user@test.fr", "password": "MrToto@123456"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_wrong_password(ac, user):
    print(f"USER : {user.prenom}")
    response = await ac.post(
        "/api/auth/login",
        json={"username": "test.user@test.fr", "password": "Fool@1234"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_wrong_username_type(ac, user):
    print(f"USER : {user.prenom}")
    response = await ac.post(
        "/api/auth/login",
        json={"username": "test", "password": "MrToto@123456"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_wrong_password_type(ac, user):
    print(f"USER : {user.prenom}")
    response = await ac.post(
        "/api/auth/login",
        json={"username": "test.user@test.fr", "password": "@1234"},
    )
    assert response.status_code == 401
