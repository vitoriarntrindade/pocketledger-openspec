## Why

PocketLedger is a small personal finance tracker built specifically to practice Spec-Driven Development end-to-end with OpenSpec: discovery, specification, design, and task planning ahead of implementation. The domain is intentionally small but has enough real business rules — money precision, per-user data isolation, category/transaction consistency, derived balances — to make the practice meaningful without ballooning into a production system.

## What Changes

- Introduce user registration and JWT-based authentication (access token only, no refresh/logout for MVP).
- Introduce per-user categories with a mandatory type (income or expense) that must match the transactions that use them; categories in use cannot be deleted.
- Introduce income/expense transactions with monetary amounts stored as fixed-precision decimals, owned by exactly one user, filterable by date range/type/category, sortable (needed to answer "what were my biggest expenses"), and paginated.
- Introduce a financial summary endpoint that derives totals, counts, balance, and expense-by-category distribution from transactions for a given period — no stored/cached balance.
- Introduce baseline observability: structured JSON logs correlated by a `request_id`, HTTP/business metrics in Prometheus format, OpenTelemetry tracing, and health/readiness endpoints — using a lightweight local stack (app + Postgres + Jaeger; no Prometheus/Grafana servers running locally).
- Introduce a consistent error-response contract (JSON envelope with `request_id`, no internal detail leakage) applied across all endpoints.

## Capabilities

### New Capabilities
- `auth`: User registration and JWT login/verification. Access-token-only strategy (no refresh tokens, no server-side revocation) per MVP scope decision.
- `users`: Authenticated user's own profile (id, name, email) — no admin roles, no profile editing, no account deletion.
- `categories`: Per-user categories with a mandatory type (income/expense) enforced against transactions; rename supported; deletion blocked while in use.
- `transactions`: Per-user income/expense records with amount, description, date, category; create/edit/delete; filter by date range, type, category; sort by date or amount; paginated listing.
- `financial-summary`: Derived financial summary for a period — total income, total expenses, balance, counts, and expense distribution by category — scoped to the authenticated user, computed on read (never stored).
- `observability`: Structured logging with request correlation, HTTP/business metrics, OpenTelemetry tracing, health/readiness endpoints, and a consistent error-response contract, applied across all the above capabilities.

### Modified Capabilities
_None — this is a greenfield system with no pre-existing specs._

## Impact

- New FastAPI backend service (no frontend).
- New PostgreSQL schema, versioned via Alembic migrations, enforcing ownership and referential-integrity rules (e.g. `ON DELETE RESTRICT` for categories in use) at the database level where appropriate.
- New Docker Compose environment for local development: FastAPI app, PostgreSQL, and Jaeger (tracing UI); logs via `docker compose logs`, metrics exposed on a `/metrics` endpoint without a running Prometheus/Grafana server.
- New pytest suite covering business rules, auth/authorization, per-user data isolation, validation, category/transaction relationships, summary calculation, filtering, pagination, and category-deletion-in-use behavior.
- No existing code, specs, or systems affected.
