import pytest


@pytest.mark.asyncio
async def test_users_me(ac, auth_cookie):
    headers = {"Cookie": f"access_token={auth_cookie}"}
    response = await ac.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"role": "home"}


@pytest.mark.asyncio
async def test_users_me_no_cookie(ac):
    response = await ac.get("/api/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "not_authenticated"}
