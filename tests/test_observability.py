import json
import logging

from opentelemetry import trace

from app.context import request_id_ctx_var
from app.core.logging import (
    JSONFormatter,
    RequestContextFilter,
    _current_trace_id,
)
from app.services import category_service


def _make_record(message="hello", level=logging.INFO):
    return logging.LogRecord(
        name="test", level=level, pathname=__file__, lineno=1, msg=message, args=None, exc_info=None
    )


def test_json_formatter_includes_required_fields():
    payload = json.loads(JSONFormatter().format(_make_record()))
    for field in ("timestamp", "level", "service", "environment", "message"):
        assert field in payload


def test_request_context_filter_attaches_request_id():
    token = request_id_ctx_var.set("test-request-id")
    try:
        record = _make_record()
        RequestContextFilter().filter(record)
        assert record.request_id == "test-request-id"
    finally:
        request_id_ctx_var.reset(token)


def test_current_trace_id_matches_active_span():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("test-span") as span:
        expected = format(span.get_span_context().trace_id, "032x")
        assert _current_trace_id() == expected


def test_current_trace_id_is_none_without_active_span():
    assert _current_trace_id() is None


def test_request_id_generated_when_absent(client):
    response = client.get("/health")
    assert len(response.headers.get("x-request-id", "")) > 0


def test_request_id_preserved_when_supplied(client):
    response = client.get("/health", headers={"X-Request-ID": "my-custom-id"})
    assert response.headers["x-request-id"] == "my-custom-id"


def test_login_does_not_leak_credentials(client, caplog):
    caplog.set_level(logging.DEBUG)
    client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "supersecret123"},
    )
    caplog.clear()
    client.post(
        "/api/v1/auth/login", json={"email": "alice@example.com", "password": "supersecret123"}
    )
    for record in caplog.records:
        assert "supersecret123" not in record.getMessage()


def test_validation_failure_logged_below_error(client, auth_headers, caplog):
    caplog.set_level(logging.DEBUG)
    category = client.post(
        "/api/v1/categories", json={"name": "Alimentacao", "type": "expense"}, headers=auth_headers
    ).json()
    caplog.clear()
    client.post(
        "/api/v1/transactions",
        json={
            "type": "income",
            "description": "x",
            "amount": "10.00",
            "transaction_date": "2026-01-01",
            "category_id": category["id"],
        },
        headers=auth_headers,
    )
    domain_error_records = [r for r in caplog.records if r.name == "app.api.error_handlers"]
    assert domain_error_records
    assert all(r.levelno < logging.ERROR for r in domain_error_records)


def test_unhandled_error_logged_at_error_with_stack_trace(client, auth_headers, caplog, monkeypatch):
    caplog.set_level(logging.DEBUG)

    def _boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(category_service, "list_categories", _boom)
    caplog.clear()
    client.get("/api/v1/categories", headers=auth_headers)

    error_records = [r for r in caplog.records if r.name == "app.unhandled"]
    assert error_records
    assert error_records[0].levelno == logging.ERROR
    assert error_records[0].exc_info is not None


def test_failed_login_logs_client_ip(client, caplog):
    caplog.set_level(logging.DEBUG)
    client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "supersecret123"},
    )
    caplog.clear()
    client.post(
        "/api/v1/auth/login", json={"email": "alice@example.com", "password": "wrongpassword"}
    )
    auth_failed_records = [r for r in caplog.records if r.getMessage() == "auth_failed"]
    assert auth_failed_records
    record = auth_failed_records[0]
    assert hasattr(record, "client_ip")
    assert record.client_ip is not None
    assert hasattr(record, "path")
    assert record.path == "/api/v1/auth/login"
