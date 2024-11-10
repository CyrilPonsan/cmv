import pytest


@pytest.mark.asyncio
async def test_get_patients_no_cookie(ac, patients):
    """Test l'accès à la liste des patients sans cookie d'authentification"""
    # Envoi d'une requête GET sans cookie d'authentification
    response = await ac.get("/api/patients/")
    print(f"RESPONSE : {response.status_code} {response.json()}")

    # Vérification que l'accès est refusé avec le bon code d'erreur
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_patients_wrong_token(ac, wrong_internal_token, patients):
    """Test l'accès à la liste des patients avec un token invalide"""
    # Préparation des headers avec un token invalide
    headers = {"Authorization": f"Bearer {wrong_internal_token}"}
    # Envoi de la requête avec le token invalide
    response = await ac.get("/api/patients/", headers=headers)

    # Vérification que l'accès est refusé avec le bon code d'erreur
    assert response.status_code == 401
    assert response.json() == {"detail": "not_authorized"}


@pytest.mark.asyncio
async def test_pagination_limit(ac, internal_token, patients):
    """Test la limitation du nombre de résultats par page"""
    # Préparation des headers avec un token valide
    headers = {"Authorization": f"Bearer {internal_token}"}
    # Envoi d'une requête avec une limite de 5 résultats
    response = await ac.get("/api/patients/?limit=5", headers=headers)

    result = response.json()

    # Vérification du bon fonctionnement de la limitation
    assert response.status_code == 200
    assert result["total"] == 21  # Nombre total de patients
    assert len(result["data"]) == 5  # Limite respectée


@pytest.mark.asyncio
async def test_pagination_offset(ac, internal_token, patients):
    """Test la pagination avec un offset (page 2)"""
    # Préparation des headers avec un token valide
    headers = {"Authorization": f"Bearer {internal_token}"}
    # Envoi d'une requête pour la deuxième page avec 5 résultats par page
    response = await ac.get("/api/patients/?limit=5&page=2", headers=headers)

    result = response.json()

    # Vérification de la pagination
    assert response.status_code == 200
    assert result["total"] == 21
    assert len(result["data"]) == 5
    assert result["data"][0]["id_patient"] == 14  # Premier patient de la page 2


@pytest.mark.asyncio
async def test_pagination_tri_prenom_desc(ac, internal_token, patients):
    """Test le tri des résultats par prénom en ordre décroissant"""
    # Préparation des headers avec un token valide
    headers = {"Authorization": f"Bearer {internal_token}"}
    # Envoi d'une requête avec tri par prénom décroissant
    response = await ac.get(
        "/api/patients/?limit=5&page=2&order=desc&field=prenom", headers=headers
    )

    result = response.json()

    # Vérification du tri
    assert response.status_code == 200
    assert result["total"] == 21
    assert len(result["data"]) == 5
    assert result["data"][0]["prenom"] == "prenom_test_4"


@pytest.mark.asyncio
async def test_pagination_bad_type_page(ac, internal_token, patients):
    """Test la gestion d'erreur avec un numéro de page invalide"""
    # Préparation des headers avec un token valide
    headers = {"Authorization": f"Bearer {internal_token}"}
    # Envoi d'une requête avec un numéro de page invalide
    response = await ac.get(
        "/api/patients/?limit=5&page=toto&order=desc&field=prenom", headers=headers
    )

    # Vérification de la gestion d'erreur
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_pagination_bad_type_limit(ac, internal_token, patients):
    """Test la gestion d'erreur avec une limite invalide"""
    # Préparation des headers avec un token valide
    headers = {"Authorization": f"Bearer {internal_token}"}
    # Envoi d'une requête avec une limite invalide
    response = await ac.get(
        "/api/patients/?limit=toto&page=1&order=desc&field=prenom", headers=headers
    )

    # Vérification de la gestion d'erreur
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_pagination_tri_nom_asc(ac, internal_token, patients):
    """Test le tri des résultats par nom en ordre croissant"""
    # Préparation des headers avec un token valide
    headers = {"Authorization": f"Bearer {internal_token}"}
    # Envoi d'une requête avec tri par nom croissant
    response = await ac.get(
        "/api/patients/?limit=5&page=1&order=asc&field=nom", headers=headers
    )

    result = response.json()

    # Vérification du tri
    assert response.status_code == 200
    assert result["total"] == 21
    assert len(result["data"]) == 5
    assert result["data"][0]["nom"] == "nom_test_0"


@pytest.mark.asyncio
async def test_pagination_limit_extreme(ac, internal_token, patients):
    """Test la pagination avec une limite très élevée"""
    # Préparation des headers avec un token valide
    headers = {"Authorization": f"Bearer {internal_token}"}
    # Envoi d'une requête avec une limite très élevée
    response = await ac.get("/api/patients/?limit=1000", headers=headers)

    result = response.json()

    # Vérification que tous les résultats sont retournés
    assert response.status_code == 200
    assert result["total"] == 21
    assert len(result["data"]) == 21


@pytest.mark.asyncio
async def test_search_patients(ac, internal_token, patients):
    """Test la recherche d'un patient spécifique"""
    # Préparation des headers avec un token valide
    headers = {"Authorization": f"Bearer {internal_token}"}
    # Recherche d'un patient spécifique
    response = await ac.get("/api/patients/search?search=toto", headers=headers)

    result = response.json()

    # Vérification des résultats de recherche
    assert response.status_code == 200
    assert result["total"] == 1
    assert result["data"][0]["nom"] == "toto"


@pytest.mark.asyncio
async def test_search_mass_patients(ac, internal_token, patients):
    """Test la recherche retournant plusieurs patients"""
    # Préparation des headers avec un token valide
    headers = {"Authorization": f"Bearer {internal_token}"}
    # Recherche retournant plusieurs résultats
    response = await ac.get("/api/patients/search?search=test", headers=headers)

    result = response.json()

    # Vérification des résultats multiples
    assert response.status_code == 200
    assert result["total"] == 20
    assert len(result["data"]) == 10
    assert result["data"][0]["nom"] == "nom_test_0"


@pytest.mark.asyncio
async def test_no_data_found_from_search(ac, internal_token, patients):
    """Test la recherche ne retournant aucun résultat"""
    # Préparation des headers avec un token valide
    headers = {"Authorization": f"Bearer {internal_token}"}
    # Recherche sans résultat attendu
    response = await ac.get("/api/patients/search?search=blabla", headers=headers)

    result = response.json()

    # Vérification de l'absence de résultats
    assert response.status_code == 200
    assert result["total"] == 0
    assert len(result["data"]) == 0
    assert result["data"] == []


@pytest.mark.asyncio
async def test_get_patient_detail_no_cookie(ac, patients):
    """Test l'accès aux détails d'un patient sans cookie d'authentification"""
    # Tentative d'accès aux détails sans authentification
    response = await ac.get("/api/patients/detail/1")
    # Vérification que l'accès est refusé
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_patient_detail_wrong_token(ac, wrong_internal_token, patients):
    """Test l'accès aux détails d'un patient avec un token invalide"""
    # Préparation des headers avec un token invalide
    headers = {"Authorization": f"Bearer {wrong_internal_token}"}
    # Tentative d'accès avec token invalide
    response = await ac.get("/api/patients/detail/1", headers=headers)
    # Vérification que l'accès est refusé
    assert response.status_code == 401
    assert response.json() == {"detail": "not_authorized"}


@pytest.mark.asyncio
async def test_get_patient_detail_not_found(ac, internal_token):
    """Test la récupération des détails d'un patient inexistant"""
    # Préparation des headers avec un token valide
    headers = {"Authorization": f"Bearer {internal_token}"}
    # Tentative d'accès à un patient inexistant
    response = await ac.get("/api/patients/detail/999", headers=headers)
    # Vérification de la gestion du cas non trouvé
    assert response.status_code == 404
    assert response.json() == {"detail": "patient_not_found"}


@pytest.mark.asyncio
async def test_get_patient_detail_success(ac, internal_token, patients):
    """Test la récupération réussie des détails d'un patient"""
    # Préparation des headers avec un token valide
    headers = {"Authorization": f"Bearer {internal_token}"}
    # Récupération des détails d'un patient existant
    response = await ac.get("/api/patients/detail/1", headers=headers)
    result = response.json()

    # Vérification de la présence de tous les champs attendus
    assert response.status_code == 200
    assert result["id_patient"] == 1
    assert "nom" in result
    assert "prenom" in result
    assert "date_de_naissance" in result
    assert "adresse" in result
    assert "code_postal" in result
    assert "ville" in result
    assert "telephone" in result
    assert "email" in result
    assert "documents" in result
    assert len(result["documents"]) == 2
    assert result["documents"][0]["nom_fichier"] == "document_test_0"
    assert result["documents"][1]["nom_fichier"] == "document_test_1"
