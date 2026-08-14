## 1. Project Setup

- [x] 1.1 Initialize Python project structure (FastAPI app package, `pyproject.toml`/`requirements.txt`, dependency pins for FastAPI, SQLAlchemy 2.x, Alembic, Pydantic, PyJWT, bcrypt/passlib, pytest, httpx)
- [x] 1.2 Add Pydantic `Settings` for configuration (DB URL, JWT secret, JWT expiry, environment name, log level) sourced from environment variables
- [x] 1.3 Set up base app module: FastAPI instance, router registration scaffold, dependency wiring for DB session
- [x] 1.4 Write `Dockerfile` for the app image and `docker-compose.yml` with `app`, `db` (postgres:16 + health check), and `jaeger` (jaegertracing/all-in-one, OTLP enabled) services
- [x] 1.5 Wire Alembic (`alembic init`, `env.py` pointed at the app's settings and models) and confirm `alembic upgrade head` runs against the compose `db` service

## 2. Data Model & Migrations

- [x] 2.1 Define `User` model (id, name, email unique, hashed_password, created_at)
- [x] 2.2 Define `transaction_type` Postgres enum (`income`, `expense`) shared by categories and transactions
- [x] 2.3 Define `Category` model (id, user_id FK, name, type, created_at) with a unique constraint on (user_id, name, type)
- [x] 2.4 Define `Transaction` model (id, user_id FK, category_id FK with `ON DELETE RESTRICT`, type, description, amount `NUMERIC(12,2)`, transaction_date, created_at)
- [x] 2.5 Generate and apply the initial Alembic migration creating all tables, enum, and constraints

## 3. Auth Capability (specs/auth)

- [x] 3.1 Implement password hashing/verification helper (bcrypt)
- [x] 3.2 Implement JWT encode/decode helpers (HS256, fixed short expiry, no refresh)
- [x] 3.3 Implement `POST /api/v1/auth/register` (name, email, password) with duplicate-email and min-length validation, never returning the password
- [x] 3.4 Implement `POST /api/v1/auth/login` (email, password) returning an access token, with a uniform 401 for any invalid combination
- [x] 3.5 Implement an auth dependency that validates the bearer token and resolves the current `User`, rejecting missing/expired/malformed tokens with 401
- [x] 3.6 Tests: registration success/duplicate-email/weak-password, login success/invalid-credentials, protected-route rejection for missing/expired/malformed tokens, password never present in any response body

## 4. Users Capability (specs/users)

- [x] 4.1 Implement `GET /api/v1/users/me` returning id, name, email for the authenticated user
- [x] 4.2 Tests: successful profile retrieval, 401 when unauthenticated, confirm no endpoint exists that accepts another user's id

## 5. Categories Capability (specs/categories)

- [x] 5.1 Implement category service: create, rename, delete, list — all scoped to the authenticated user
- [x] 5.2 Enforce name+type uniqueness per user at creation and rename; enforce type immutability after creation
- [x] 5.3 Translate the `ON DELETE RESTRICT` integrity error from deleting an in-use category into the standard error envelope with an appropriate status code
- [x] 5.4 Implement `POST /api/v1/categories`, `GET /api/v1/categories`, `PATCH /api/v1/categories/{id}`, `DELETE /api/v1/categories/{id}`
- [x] 5.5 Tests: creation success/duplicate-name+type/same-name-different-type-allowed, type-immutable-on-edit, rename success/duplicate, delete unused succeeds, delete in-use rejected, cross-user access rejected, listing scoped to owner

## 6. Transactions Capability (specs/transactions)

- [x] 6.1 Implement transaction service: create, edit, delete, get, list — all scoped to the authenticated user
- [x] 6.2 Enforce amount > 0 and 2-decimal-place precision via Pydantic schema validation using `Decimal`
- [x] 6.3 Enforce category/transaction type match and category ownership on both create and edit
- [x] 6.4 Implement filtering (start_date, end_date, type, category_id, all combinable), sorting (date/amount, asc/desc), and pagination (page, page_size, total count) on the list endpoint
- [x] 6.5 Implement `POST /api/v1/transactions`, `GET /api/v1/transactions`, `GET /api/v1/transactions/{id}`, `PATCH /api/v1/transactions/{id}`, `DELETE /api/v1/transactions/{id}`
- [x] 6.6 Tests: creation success/type-mismatch/foreign-category-rejected, amount validation (zero/negative rejected), backdated transaction accepted, edit success/edit-causing-mismatch-rejected, deletion, cross-user isolation, combined filters, sorting by amount and date, pagination defaults and second-page behavior

## 7. Financial Summary Capability (specs/financial-summary)

- [x] 7.1 Implement summary service computing totals, counts, balance, and expense-by-category distribution from transactions for a given date range, scoped to the authenticated user
- [x] 7.2 Implement `GET /api/v1/summary?start_date=&end_date=`
- [x] 7.3 Tests: summary correctness for mixed income/expense data, balance always equals income minus expenses and reflects an immediately-prior create/delete, empty-period returns zeros/empty distribution, another user's transactions never affect the result

## 8. Error Handling

- [x] 8.1 Define domain exceptions: `NotFoundError`, `ConflictError`, `ValidationError`, `UnauthorizedError`
- [x] 8.2 Register centralized FastAPI exception handlers mapping each to its HTTP status and the `{"error": {"code", "message", "request_id"}}` envelope
- [x] 8.3 Add a catch-all handler for unhandled exceptions: log at ERROR with stack trace and request id, return a generic 500 in the same envelope with no internal detail
- [x] 8.4 Tests: each domain exception maps to the right status/envelope, an unhandled error never leaks a stack trace or internal message to the client

## 9. Observability — Logging & Correlation

- [x] 9.1 Configure structured JSON logging (timestamp, level, service name, environment, message) for the whole app, replacing any `print`/unstructured logging
- [x] 9.2 Add request-id middleware: read `X-Request-ID` if present else generate one, propagate via context, echo it on the response header
- [x] 9.3 Attach the request id (and current trace id, once tracing is wired) to every log record produced during a request
- [x] 9.4 Ensure passwords, JWTs, and secrets are never included in any log statement; keep financial log detail to identifiers only, not full transaction payloads
- [x] 9.5 Classify logging: validation/business-rule failures logged below ERROR; unexpected failures logged at ERROR/CRITICAL with context
- [x] 9.6 Tests: request-id generated when absent, preserved when supplied, present in logs and response header; a login attempt's logs contain no password/token; a validation failure logs below ERROR while an unhandled error logs at ERROR with a stack trace

## 10. Observability — Metrics

- [x] 10.1 Expose `/metrics` in Prometheus text format with HTTP request/error counters and latency histograms labeled by method, route, and status code only (no user id, request id, or free-form values)
- [x] 10.2 Add business-operation counters (e.g. transactions created, summaries requested)
- [x] 10.3 Tests: a completed request is reflected in the relevant HTTP metrics; creating a transaction increments its business counter

## 11. Observability — Tracing

- [x] 11.1 Wire OpenTelemetry SDK with FastAPI and SQLAlchemy auto-instrumentation, exporting via OTLP to the `jaeger` compose service
- [x] 11.2 Ensure each request produces a trace with spans for the HTTP entry point, the triggered business operation, and instrumented DB calls
- [x] 11.3 Inject the active trace id into the request's log records for cross-correlation
- [x] 11.4 Tests/manual check: a request's trace is visible in Jaeger and its trace id matches the id present in that request's logs

## 12. Health, Readiness & Ops Endpoints

- [x] 12.1 Implement `GET /health` reporting process liveness
- [x] 12.2 Implement `GET /ready` performing a lightweight DB connectivity check (`SELECT 1`), returning 503 when the database is unreachable
- [x] 12.3 Tests: `/health` reports healthy while running; `/ready` reports not-ready when the DB is down (simulate by pointing at an unreachable DB)

## 13. Docker & Local Environment

- [x] 13.1 Confirm `docker compose up` brings up `app` + `db` + `jaeger`, running migrations automatically before the app serves traffic
- [x] 13.2 Provide a simple way to run the test suite in the compose environment (e.g. `docker compose run app pytest`) against a dedicated test database
- [x] 13.3 Document (in a README or compose comments) how to view logs (`docker compose logs`), query `/metrics`, and open the Jaeger UI

## 14. Final Verification

- [x] 14.1 Run the full pytest suite and confirm all specs' scenarios are covered by at least one test
- [x] 14.2 Manually walk through the observability criteria end to end: make a request, find its logs by request id, find its trace in Jaeger, read its latency from `/metrics`, trigger an internal error and confirm it's investigable while a validation error is not logged as one
- [x] 14.3 Review the full API surface against specs/*.md for any gaps before considering the MVP done
