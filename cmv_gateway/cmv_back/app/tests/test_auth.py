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


def test_login_wrong_user(client, user):
    print(f"USER : {user.prenom}")
    response = client.post(
        "/api/auth/login",
        json={"username": "foo.user@test.fr", "password": "Toto@1234"},
    )
    assert response.status_code == 401


def test_login_wrong_password(client, user):
    print(f"USER : {user.prenom}")
    response = client.post(
        "/api/auth/login",
        json={"username": "test.user@test.fr", "password": "Fool@1234"},
    )
    assert response.status_code == 401


def test_login_wrong_username_type(client, user):
    print(f"USER : {user.prenom}")
    response = client.post(
        "/api/auth/login",
        json={"username": "test", "password": "Toto@1234"},
    )
    assert response.status_code == 422


def test_login_wrong_password_type(client, user):
    print(f"USER : {user.prenom}")
    response = client.post(
        "/api/auth/login",
        json={"username": "test.user@test.fr", "password": "@1234"},
    )
    assert response.status_code == 401
