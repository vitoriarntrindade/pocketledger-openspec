from app.infrastructure.metrics import (
    summaries_requested_total,
    transactions_created_total,
)


def test_metrics_endpoint_reflects_business_counters(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "pocketledger_transactions_created_total" in response.text
    assert "pocketledger_summaries_requested_total" in response.text


def test_completed_request_reflected_in_http_metrics(client):
    client.get("/health")

    metrics_text = client.get("/metrics").text
    assert 'handler="/health"' in metrics_text
    assert 'method="GET"' in metrics_text
    assert 'status="2xx"' in metrics_text
    # No high-cardinality labels such as user id or request id.
    assert "user_id" not in metrics_text
    assert "request_id" not in metrics_text


def test_transaction_created_increments_business_counter(
    client, auth_headers
):
    category = client.post(
        "/api/v1/categories",
        json={"name": "Alimentacao", "type": "expense"},
        headers=auth_headers,
    ).json()
    before = transactions_created_total._value.get()

    client.post(
        "/api/v1/transactions",
        json={
            "type": "expense",
            "description": "x",
            "amount": "10.00",
            "transaction_date": "2026-01-01",
            "category_id": category["id"],
        },
        headers=auth_headers,
    )

    assert transactions_created_total._value.get() == before + 1


def test_summary_requested_increments_business_counter(client, auth_headers):
    before = summaries_requested_total._value.get()

    client.get(
        "/api/v1/summary",
        headers=auth_headers,
        params={"start_date": "2026-01-01", "end_date": "2026-01-31"},
    )

    assert summaries_requested_total._value.get() == before + 1
