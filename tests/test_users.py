def test_get_my_profile(client, auth_headers):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Alice"
    assert body["email"] == "alice@example.com"


def test_get_my_profile_requires_auth(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_no_lookup_by_id_endpoint_exists(client, auth_headers):
    # There is no route that accepts another user's id - confirm the closest
    # guesses (a numeric path segment under /users) don't resolve to profile data.
    response = client.get("/api/v1/users/1", headers=auth_headers)
    assert response.status_code == 404
