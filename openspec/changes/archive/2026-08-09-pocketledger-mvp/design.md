## Context

Greenfield FastAPI backend (see proposal.md - Why) with PostgreSQL, SQLAlchemy 2.x, Alembic, Pydantic, pytest, and Docker Compose as fixed stack choices, JWT for auth, and a lightweight local observability tier (app + Postgres + Jaeger, no Prometheus/Grafana servers) — all confirmed during discovery. No existing code or specs to integrate with.

## Goals / Non-Goals

**Goals:**
- A simple, conventional layering (API → service/business-rule layer → persistence) that a reader can follow without prior context.
- Enforce every cross-cutting rule (ownership isolation, category/transaction type match, category-in-use deletion block) at the layer best suited to catch it, favoring database constraints where a constraint can express the rule directly.
- Make the observability requirements (structured logs, metrics, tracing, correlation) concrete enough to implement without further design decisions.

**Non-Goals:**
- Horizontal scalability, caching, or performance tuning beyond what a single-instance MVP needs.
- Production-grade secret management, TLS termination, or deployment topology — local Docker Compose only.
- Historical metrics storage/dashboards (no Prometheus server or Grafana in this tier) — the `/metrics` endpoint is scrape-able but nothing scrapes it continuously.

## Decisions

**Layering: API → service → persistence, no async DB layer.**
FastAPI routers hold only request/response translation (Pydantic schemas in/out). A service module per capability (`auth`, `categories`, `transactions`, `summary`) holds business rules and raises typed domain exceptions (`NotFoundError`, `ConflictError`, `ValidationError`). SQLAlchemy 2.x models and a synchronous `Session` (via `psycopg` v3) form the persistence layer, injected per-request through a FastAPI dependency. *Alternative considered*: async SQLAlchemy with `asyncpg`. Rejected for this project's scale — sync sessions in FastAPI's threadpool are simpler to reason about and test, and the MVP has no throughput requirement that would justify the added complexity.

**Money as `Decimal`/`NUMERIC(12,2)` end to end.**
Postgres columns use `NUMERIC(12,2)`; Python code uses `decimal.Decimal` exclusively; Pydantic schemas validate `> 0` and reject values with more than 2 decimal places. `float` never appears on the monetary path, satisfying the "no float for money" consistency rule directly at the type level.

**Category type as a shared Postgres enum, matched in the service layer.**
`transaction_type` is a native Postgres enum (`income`, `expense`) reused by both `categories.type` and `transactions.type`. The rule "a transaction's type must match its category's type" is enforced in the service layer on create and edit, not via a DB trigger. *Alternative considered*: a DB-level trigger or check constraint joining the two tables. Rejected as overengineered for one validation path that already has direct test coverage required by the proposal; noted as a risk below.

**Category-in-use deletion blocked via `ON DELETE RESTRICT`.**
`transactions.category_id` has a foreign key to `categories.id` with `ON DELETE RESTRICT`. The service layer catches the resulting integrity error and translates it into the documented 409-style API error, so the rule holds even against a direct DB write path, not just application code.

**Ownership isolation via mandatory `user_id` filtering, not row-level security.**
Every category and transaction row carries a `user_id` foreign key. Every service-layer query filters by the authenticated user's id extracted from the JWT; there is no code path that queries by primary key alone. *Alternative considered*: Postgres row-level security policies. Rejected — one extra mechanism to maintain for a rule the service layer already enforces uniformly and that tests cover per the proposal's isolation-testing requirement.

**Auth: JWT (HS256), access-token-only, 60-minute expiry.**
`PyJWT` signs/verifies tokens with a single symmetric secret from environment config (Pydantic `Settings`). No refresh token, no revocation list, per the confirmed MVP decision — a user simply logs in again after expiry. Passwords hashed with bcrypt (via `passlib` or the `bcrypt` package directly).

**Pagination and sorting as query parameters.**
Transaction listing accepts `page` (default 1), `page_size` (default 20, max 100), `sort_by` (`date` | `amount`, default `date`), and `order` (`asc` | `desc`, default `desc`), alongside the filter params (`start_date`, `end_date`, `type`, `category_id`). Response includes the page of results plus a total matching count.

**API surface under `/api/v1`, ops endpoints at root.**
Business endpoints (`/api/v1/auth/*`, `/api/v1/users/me`, `/api/v1/categories`, `/api/v1/transactions`, `/api/v1/summary`) are versioned. `/health`, `/ready`, and `/metrics` sit at the root, unversioned, matching common operational convention and keeping them reachable even if the API version changes later.

**Error contract: centralized exception handlers, one JSON envelope.**
A small set of domain exceptions (`NotFoundError`, `ConflictError`, `ValidationError`, `UnauthorizedError`) are raised by services and mapped to HTTP status codes by FastAPI exception handlers registered once, each producing `{"error": {"code", "message", "request_id"}}`. Unhandled exceptions are caught by a catch-all handler that logs at ERROR with a stack trace and returns a generic 500 body with the same envelope shape, never the underlying exception's message.

**Observability implementation choices.**
- *Logging*: Python's standard `logging` module with a JSON formatter; a middleware sets the request's correlation id in a `contextvars.ContextVar`, and a logging filter attaches it (plus the current OpenTelemetry trace id, when present) to every record. Library choice between `structlog` and a JSON formatter library is left open (see Open Questions) since either satisfies the structured-logging requirement identically.
- *Correlation*: middleware reads `X-Request-ID` if present, else generates a UUID4; sets it in context for logging; echoes it back on the same response header; domain exceptions carry it into the error envelope.
- *Metrics*: `prometheus-fastapi-instrumentator` (or `prometheus-client` wired manually) exposes `/metrics` in Prometheus text format, with method/route/status-code labels for HTTP metrics and hand-added counters for business events (transaction created, summary requested). No Prometheus server runs in this tier — the endpoint is scraped ad hoc (`curl`) to satisfy the "identify latency" and "count requests" criteria without adding a service.
- *Tracing*: `opentelemetry-sdk` with the FastAPI and SQLAlchemy auto-instrumentation packages, exporting via OTLP to the Jaeger all-in-one container (OTLP receiver enabled), viewable at its UI port. Trace id is pulled from the active span and injected into logs for correlation.
- *Health/Readiness*: `/health` returns 200 once the process is serving; `/ready` additionally runs a lightweight `SELECT 1` against Postgres and reports 503 if it fails.

**Docker Compose topology: `app`, `db`, `jaeger`.**
`db` is `postgres:16` with a healthcheck; `app` depends on `db` being healthy and runs Alembic migrations (`alembic upgrade head`) as a startup step before serving; `jaeger` is `jaegertracing/all-in-one` with its OTLP HTTP/gRPC receiver enabled. Tests run against the same `db` service using a separate test database/schema, invoked via `docker compose run app pytest`.

## Risks / Trade-offs

- **Category/transaction type matching lives in application code, not a DB constraint** → a bug in the service layer could let a mismatched category slip through on a code path that bypasses the service. Mitigated by the proposal's explicit test-coverage requirement for "relationship between categories and transactions," and by having exactly one service function own both create and edit validation.
- **No refresh token or logout** → a valid access token cannot be invalidated before its 60-minute expiry, even if the user wants to log out. Accepted as a documented MVP limitation per the confirmed auth-strategy decision; short expiry bounds the exposure window.
- **Sync DB session inside FastAPI's async handlers** → each DB-bound request occupies a threadpool worker for the call's duration. Acceptable at the traffic level this project will ever see; would need revisiting (async SQLAlchemy + asyncpg) only if this ever became a real multi-user service.
- **Lightweight observability tier has no metrics history** → `/metrics` reflects only the current process's in-memory counters, with nothing persisting or graphing them over time. Acceptable because the stated observability criteria (correlate a request, find its trace, see its latency, diagnose an error) are all satisfiable by querying Jaeger and scraping `/metrics` directly; a Prometheus/Grafana tier could be added later without any application change, since metrics are already exposed in Prometheus's exposition format.

## Migration Plan

Greenfield project — no production data or prior schema to migrate away from. The first Alembic revision creates the full schema (users, categories, transactions) in one step; `docker compose up` runs migrations automatically before the app starts serving. No rollback strategy beyond `alembic downgrade` is needed at this stage.

## Open Questions

- Exact JSON-logging library (`structlog` vs. a JSON `logging.Formatter`) — either satisfies the structured-logging requirement identically; can be picked during implementation without touching the spec.
- Exact metric and span names — will follow OpenTelemetry semantic conventions where one exists (e.g. `http.server.duration`); naming is an implementation detail that doesn't change what must be observable.
