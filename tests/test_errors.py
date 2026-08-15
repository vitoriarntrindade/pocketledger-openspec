from app.services import category_service


def test_not_found_maps_to_404(client, auth_headers):
    response = client.get("/api/v1/transactions/99999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_conflict_maps_to_409(client, auth_headers):
    payload = {"name": "Alimentacao", "type": "expense"}
    client.post("/api/v1/categories", json=payload, headers=auth_headers)
    response = client.post(
        "/api/v1/categories", json=payload, headers=auth_headers
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_domain_validation_error_maps_to_400(client, auth_headers):
    expense = client.post(
        "/api/v1/categories",
        json={"name": "Alimentacao", "type": "expense"},
        headers=auth_headers,
    ).json()
    response = client.post(
        "/api/v1/transactions",
        json={
            "type": "income",
            "description": "x",
            "amount": "10.00",
            "transaction_date": "2026-01-01",
            "category_id": expense["id"],
        },
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "validation_error"


def test_request_validation_error_returns_safe_consistent_envelope(
    client, auth_headers
):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alice",
            "email": "not-an-email",
            "password": "supersecret123",
        },
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["request_id"] == response.headers["x-request-id"]
    # Generic, safe message - no leaked Pydantic internals (field paths, type names, etc).
    assert "not-an-email" not in response.text
    assert "email_validator" not in response.text


def test_unauthorized_maps_to_401(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_all_domain_error_responses_carry_request_id(client, auth_headers):
    response = client.get("/api/v1/transactions/99999", headers=auth_headers)
    body = response.json()
    assert body["error"]["request_id"] == response.headers["x-request-id"]
    assert body["error"]["request_id"] != ""


def test_unhandled_exception_returns_generic_500_without_leaking_detail(
    client, auth_headers, monkeypatch
):
    def _boom(*args, **kwargs):
        raise RuntimeError("something went very wrong internally")

    monkeypatch.setattr(category_service, "list_categories", _boom)

    response = client.get("/api/v1/categories", headers=auth_headers)
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "internal_error"
    assert "something went very wrong internally" not in response.text
    assert "RuntimeError" not in response.text
    assert "Traceback" not in response.text
    assert response.headers["x-request-id"] == body["error"]["request_id"]
