import pytest


@pytest.fixture
def expense_category(client, auth_headers):
    return client.post(
        "/api/v1/categories", json={"name": "Alimentacao", "type": "expense"}, headers=auth_headers
    ).json()


@pytest.fixture
def income_category(client, auth_headers):
    return client.post(
        "/api/v1/categories", json={"name": "Salario", "type": "income"}, headers=auth_headers
    ).json()


def _create(client, headers, category, **overrides):
    payload = {
        "type": "expense",
        "description": "Almoco",
        "amount": "45.50",
        "transaction_date": "2026-01-15",
        "category_id": category["id"],
    }
    payload.update(overrides)
    return client.post("/api/v1/transactions", json=payload, headers=headers)


def test_create_transaction_success(client, auth_headers, expense_category):
    response = _create(client, auth_headers, expense_category)
    assert response.status_code == 201
    body = response.json()
    assert body["amount"] == "45.50"
    assert body["category_id"] == expense_category["id"]


def test_create_type_mismatch_rejected(client, auth_headers, expense_category):
    response = _create(client, auth_headers, expense_category, type="income")
    assert response.status_code == 400


def test_create_foreign_category_rejected(client, auth_headers, other_auth_headers, expense_category):
    response = _create(client, other_auth_headers, expense_category)
    assert response.status_code == 404


def test_zero_amount_rejected(client, auth_headers, expense_category):
    response = _create(client, auth_headers, expense_category, amount="0")
    assert response.status_code == 422


def test_negative_amount_rejected(client, auth_headers, expense_category):
    response = _create(client, auth_headers, expense_category, amount="-5.00")
    assert response.status_code == 422


def test_invalid_type_rejected(client, auth_headers, expense_category):
    response = _create(client, auth_headers, expense_category, type="refund")
    assert response.status_code == 422


def test_missing_type_rejected(client, auth_headers, expense_category):
    payload = {
        "description": "Almoco",
        "amount": "10.00",
        "transaction_date": "2026-01-15",
        "category_id": expense_category["id"],
    }
    response = client.post("/api/v1/transactions", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_more_than_two_decimal_places_rejected(client, auth_headers, expense_category):
    response = _create(client, auth_headers, expense_category, amount="5.123")
    assert response.status_code == 422


def test_backdated_transaction_accepted(client, auth_headers, expense_category):
    response = _create(client, auth_headers, expense_category, transaction_date="2020-01-01")
    assert response.status_code == 201
    assert response.json()["transaction_date"] == "2020-01-01"


def test_edit_success(client, auth_headers, expense_category):
    created = _create(client, auth_headers, expense_category).json()
    response = client.patch(
        f"/api/v1/transactions/{created['id']}",
        json={"description": "Jantar", "amount": "30.00"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["description"] == "Jantar"
    assert body["amount"] == "30.00"


def test_edit_causing_type_mismatch_rejected(client, auth_headers, expense_category, income_category):
    created = _create(client, auth_headers, expense_category).json()
    response = client.patch(
        f"/api/v1/transactions/{created['id']}",
        json={"category_id": income_category["id"]},
        headers=auth_headers,
    )
    assert response.status_code == 400

    unchanged = client.get(f"/api/v1/transactions/{created['id']}", headers=auth_headers).json()
    assert unchanged["category_id"] == expense_category["id"]
    assert unchanged["description"] == created["description"]


def test_deletion(client, auth_headers, expense_category):
    created = _create(client, auth_headers, expense_category).json()
    response = client.delete(f"/api/v1/transactions/{created['id']}", headers=auth_headers)
    assert response.status_code == 204
    assert client.get(f"/api/v1/transactions/{created['id']}", headers=auth_headers).status_code == 404


def test_cross_user_isolation(client, auth_headers, other_auth_headers, expense_category):
    created = _create(client, auth_headers, expense_category).json()

    assert (
        client.get(f"/api/v1/transactions/{created['id']}", headers=other_auth_headers).status_code
        == 404
    )
    assert (
        client.patch(
            f"/api/v1/transactions/{created['id']}",
            json={"description": "hacked"},
            headers=other_auth_headers,
        ).status_code
        == 404
    )
    assert (
        client.delete(
            f"/api/v1/transactions/{created['id']}", headers=other_auth_headers
        ).status_code
        == 404
    )


def test_combined_filters(client, auth_headers, expense_category, income_category):
    _create(client, auth_headers, expense_category, transaction_date="2026-01-05", amount="10.00")
    _create(client, auth_headers, expense_category, transaction_date="2026-02-05", amount="20.00")
    _create(
        client,
        auth_headers,
        income_category,
        type="income",
        transaction_date="2026-01-10",
        amount="500.00",
    )

    response = client.get(
        "/api/v1/transactions",
        headers=auth_headers,
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "type": "expense",
            "category_id": expense_category["id"],
        },
    )
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["amount"] == "10.00"


def test_sort_by_amount_descending(client, auth_headers, expense_category):
    _create(client, auth_headers, expense_category, amount="5.00", description="small")
    _create(client, auth_headers, expense_category, amount="99.00", description="big")
    _create(client, auth_headers, expense_category, amount="42.00", description="medium")

    response = client.get(
        "/api/v1/transactions",
        headers=auth_headers,
        params={"sort_by": "amount", "order": "desc"},
    )
    amounts = [item["amount"] for item in response.json()["items"]]
    assert amounts == ["99.00", "42.00", "5.00"]


def test_pagination_defaults(client, auth_headers, expense_category):
    for i in range(3):
        _create(client, auth_headers, expense_category, amount=f"{i + 1}.00")

    response = client.get("/api/v1/transactions", headers=auth_headers)
    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert body["total"] == 3
    assert len(body["items"]) == 3


def test_pagination_second_page(client, auth_headers, expense_category):
    for i in range(5):
        _create(client, auth_headers, expense_category, amount=f"{i + 1}.00")

    response = client.get(
        "/api/v1/transactions",
        headers=auth_headers,
        params={"page": 2, "page_size": 2, "sort_by": "amount", "order": "asc"},
    )
    body = response.json()
    assert body["total"] == 5
    assert body["page"] == 2
    amounts = [item["amount"] for item in body["items"]]
    assert amounts == ["3.00", "4.00"]
