import jwt

from app.core.config import settings


def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "supersecret123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Alice"
    assert body["email"] == "alice@example.com"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email_rejected(client):
    payload = {"name": "Alice", "email": "alice@example.com", "password": "supersecret123"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


def test_register_weak_password_rejected(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_register_password_missing_letter_rejected(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "12345678"},
    )
    assert response.status_code == 422


def test_register_password_missing_digit_rejected(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "password"},
    )
    assert response.status_code == 422


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "supersecret123"},
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": "alice@example.com", "password": "supersecret123"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    decoded = jwt.decode(
        body["access_token"], settings.jwt_secret, algorithms=[settings.jwt_algorithm]
    )
    assert decoded["sub"] == "1"


def test_login_wrong_password_rejected(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "supersecret123"},
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": "alice@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_login_unknown_email_rejected(client):
    response = client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.com", "password": "whatever123"}
    )
    assert response.status_code == 401


def test_protected_route_rejects_missing_token(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_protected_route_rejects_malformed_token(client):
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_protected_route_rejects_expired_token(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "supersecret123"},
    )
    expired_token = jwt.encode(
        {"sub": "1", "iat": 0, "exp": 1},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401


def test_login_rate_limited_after_threshold(client, monkeypatch):
    monkeypatch.setattr(settings, "rate_limit_max_attempts", 3)
    monkeypatch.setattr(settings, "rate_limit_window_seconds", 60)

    client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "supersecret123"},
    )

    for i in range(settings.rate_limit_max_attempts + 1):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "alice@example.com", "password": "wrongpassword"},
        )
        if i < settings.rate_limit_max_attempts:
            assert response.status_code == 401
        else:
            assert response.status_code == 429
            body = response.json()
            assert body["error"]["code"] == "rate_limited"
