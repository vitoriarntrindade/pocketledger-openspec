def test_create_category_success(client, auth_headers):
    response = client.post(
        "/api/v1/categories",
        json={"name": "Alimentacao", "type": "expense"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Alimentacao"
    assert body["type"] == "expense"


def test_create_duplicate_name_and_type_rejected(client, auth_headers):
    payload = {"name": "Alimentacao", "type": "expense"}
    client.post("/api/v1/categories", json=payload, headers=auth_headers)
    response = client.post(
        "/api/v1/categories", json=payload, headers=auth_headers
    )
    assert response.status_code == 409


def test_same_name_allowed_across_different_types(client, auth_headers):
    client.post(
        "/api/v1/categories",
        json={"name": "Outros", "type": "expense"},
        headers=auth_headers,
    )
    response = client.post(
        "/api/v1/categories",
        json={"name": "Outros", "type": "income"},
        headers=auth_headers,
    )
    assert response.status_code == 201


def test_type_immutable_on_edit(client, auth_headers):
    created = client.post(
        "/api/v1/categories",
        json={"name": "Alimentacao", "type": "expense"},
        headers=auth_headers,
    ).json()
    response = client.patch(
        f"/api/v1/categories/{created['id']}",
        json={"name": "Alimentacao"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["type"] == "expense"
    # The schema only accepts a name update - type has no edit path at all.


def test_rename_success(client, auth_headers):
    created = client.post(
        "/api/v1/categories",
        json={"name": "Alimentacao", "type": "expense"},
        headers=auth_headers,
    ).json()
    response = client.patch(
        f"/api/v1/categories/{created['id']}",
        json={"name": "Comida"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Comida"


def test_rename_to_duplicate_rejected(client, auth_headers):
    client.post(
        "/api/v1/categories",
        json={"name": "Comida", "type": "expense"},
        headers=auth_headers,
    )
    created = client.post(
        "/api/v1/categories",
        json={"name": "Alimentacao", "type": "expense"},
        headers=auth_headers,
    ).json()
    response = client.patch(
        f"/api/v1/categories/{created['id']}",
        json={"name": "Comida"},
        headers=auth_headers,
    )
    assert response.status_code == 409


def test_delete_unused_category_succeeds(client, auth_headers):
    created = client.post(
        "/api/v1/categories",
        json={"name": "Lazer", "type": "expense"},
        headers=auth_headers,
    ).json()
    response = client.delete(
        f"/api/v1/categories/{created['id']}", headers=auth_headers
    )
    assert response.status_code == 204


def test_delete_in_use_category_rejected(client, auth_headers):
    category = client.post(
        "/api/v1/categories",
        json={"name": "Alimentacao", "type": "expense"},
        headers=auth_headers,
    ).json()
    client.post(
        "/api/v1/transactions",
        json={
            "type": "expense",
            "description": "Almoco",
            "amount": "20.00",
            "transaction_date": "2026-01-01",
            "category_id": category["id"],
        },
        headers=auth_headers,
    )
    response = client.delete(
        f"/api/v1/categories/{category['id']}", headers=auth_headers
    )
    assert response.status_code == 409


def test_cross_user_category_access_rejected(
    client, auth_headers, other_auth_headers
):
    category = client.post(
        "/api/v1/categories",
        json={"name": "Alimentacao", "type": "expense"},
        headers=auth_headers,
    ).json()

    get_response = client.patch(
        f"/api/v1/categories/{category['id']}",
        json={"name": "Hacked"},
        headers=other_auth_headers,
    )
    assert get_response.status_code == 404

    delete_response = client.delete(
        f"/api/v1/categories/{category['id']}", headers=other_auth_headers
    )
    assert delete_response.status_code == 404


def test_listing_scoped_to_owner(client, auth_headers, other_auth_headers):
    client.post(
        "/api/v1/categories",
        json={"name": "Alimentacao", "type": "expense"},
        headers=auth_headers,
    )
    client.post(
        "/api/v1/categories",
        json={"name": "Transporte", "type": "expense"},
        headers=other_auth_headers,
    )

    response = client.get("/api/v1/categories", headers=auth_headers)
    names = [c["name"] for c in response.json()]
    assert names == ["Alimentacao"]
