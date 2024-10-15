def test_fixtures(client):
    response = client.get("/fixtures")
    assert response.status_code == 200
    assert response.json() == {"message": "done"}


def test_login(client, user):
    print(f"USER : {user.prenom}")
    response = client.post(
        "/api/auth/login",
        json={"username": "test.user@test.fr", "password": "Toto@1234"},
    )
    assert response.status_code == 200
