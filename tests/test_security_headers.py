def test_security_headers_present(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"


def test_security_headers_on_error_response(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"


def test_cors_default_deny_all_origins(client):
    response = client.get("/health", headers={"Origin": "http://example.com"})
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response.headers
