import pytest


@pytest.fixture
def categories(client, auth_headers):
    expense = client.post(
        "/api/v1/categories",
        json={"name": "Alimentacao", "type": "expense"},
        headers=auth_headers,
    ).json()
    income = client.post(
        "/api/v1/categories",
        json={"name": "Salario", "type": "income"},
        headers=auth_headers,
    ).json()
    return {"expense": expense, "income": income}


def _create(client, headers, category, type_, amount, date_="2026-01-15"):
    return client.post(
        "/api/v1/transactions",
        json={
            "type": type_,
            "description": "x",
            "amount": amount,
            "transaction_date": date_,
            "category_id": category["id"],
        },
        headers=headers,
    )


def test_summary_with_mixed_data(client, auth_headers, categories):
    _create(client, auth_headers, categories["income"], "income", "1000.00")
    _create(client, auth_headers, categories["expense"], "expense", "100.00")
    _create(client, auth_headers, categories["expense"], "expense", "50.00")

    response = client.get(
        "/api/v1/summary",
        headers=auth_headers,
        params={"start_date": "2026-01-01", "end_date": "2026-01-31"},
    )
    body = response.json()
    assert body["total_income"] == "1000.00"
    assert body["total_expenses"] == "150.00"
    assert body["balance"] == "850.00"
    assert body["income_count"] == 1
    assert body["expense_count"] == 2
    assert body["expenses_by_category"] == [
        {
            "category_id": categories["expense"]["id"],
            "category_name": "Alimentacao",
            "total": "150.00",
        }
    ]


def test_balance_reflects_immediate_change(client, auth_headers, categories):
    params = {"start_date": "2026-01-01", "end_date": "2026-01-31"}
    before = client.get(
        "/api/v1/summary", headers=auth_headers, params=params
    ).json()
    assert before["balance"] == "0"

    created = _create(
        client, auth_headers, categories["expense"], "expense", "25.00"
    ).json()
    after_create = client.get(
        "/api/v1/summary", headers=auth_headers, params=params
    ).json()
    assert after_create["balance"] == "-25.00"

    client.delete(
        f"/api/v1/transactions/{created['id']}", headers=auth_headers
    )
    after_delete = client.get(
        "/api/v1/summary", headers=auth_headers, params=params
    ).json()
    assert after_delete["balance"] == "0"


def test_empty_period_returns_zeros(client, auth_headers, categories):
    _create(
        client,
        auth_headers,
        categories["expense"],
        "expense",
        "25.00",
        date_="2026-01-15",
    )

    response = client.get(
        "/api/v1/summary",
        headers=auth_headers,
        params={"start_date": "2026-02-01", "end_date": "2026-02-28"},
    )
    body = response.json()
    assert body["total_income"] == "0"
    assert body["total_expenses"] == "0"
    assert body["balance"] == "0"
    assert body["income_count"] == 0
    assert body["expense_count"] == 0
    assert body["expenses_by_category"] == []


def test_other_users_transactions_excluded(
    client, auth_headers, other_auth_headers, categories
):
    other_category = client.post(
        "/api/v1/categories",
        json={"name": "Transporte", "type": "expense"},
        headers=other_auth_headers,
    ).json()
    _create(client, other_auth_headers, other_category, "expense", "999.00")

    response = client.get(
        "/api/v1/summary",
        headers=auth_headers,
        params={"start_date": "2026-01-01", "end_date": "2026-01-31"},
    )
    body = response.json()
    assert body["total_expenses"] == "0"
    assert body["expenses_by_category"] == []
