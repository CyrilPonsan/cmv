def test_fixtures(client, db):
    response = client.get("/fixtures")
    assert response.status_code == 200
    assert response.json() == {"message": "done"}


def test_login(client, db):
    response = client.post(
        "/api/auth/login", json={"username": "tata@toto.fr", "password": "Abcd@1234"}
    )
    assert response.status_code == 200
