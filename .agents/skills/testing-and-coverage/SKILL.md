---
name: testing-and-coverage
description: How the test suite works in this project — its PostgreSQL requirement, its fixtures, how to derive tests from specification scenarios, which edge cases matter here, and how to treat the 95% coverage floor honestly. Use when writing, fixing or reviewing tests.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# Testing and coverage

## The suite is not hermetic, on purpose

Tests run against **real PostgreSQL**, not SQLite. Money precision
(`NUMERIC(12,2)`), referential integrity and the constraints that stop a
category in use from being deleted are enforced by the database — testing them
against a different engine would test something the product does not use.

The cost is a prerequisite:

```
make test        starts PostgreSQL, creates the test database, runs the suite
make db          just the database part
```

`scripts/dev-db.sh` is idempotent and additive: it starts the container only if
it is not already healthy and creates `pocketledger_test` only if it is
missing. It never drops or truncates anything.

Running `pytest` directly without the database produces 81 collection errors,
all of them the same missing connection.

## Always disable OTEL export in tests

```bash
OTEL_ENABLED=false ENVIRONMENT=test JWT_SECRET=test-only pytest
```

Without it, the OTLP exporter retries against a collector that is not there,
with backoff up to 32 seconds. The suite goes from about 43 seconds to roughly
four minutes, and the result is buried in retry warnings. `make test` and
`make quality` set this for you; a bare `pytest` does not.

A test that genuinely needs a live tracer must build its own `TracerProvider`
rather than depending on the application's global configuration — otherwise it
passes or fails according to an environment variable, which is not a test.

## Fixtures

Defined in `tests/conftest.py`:

| Fixture | Gives you |
|---|---|
| `client` | `TestClient` with `get_db` overridden to the test session |
| `auth_headers` | a registered, logged-in user's bearer header |
| `other_auth_headers` | a **second** user, for isolation tests |

Two autouse fixtures keep tests independent: one truncates all tables after
each test, the other clears the in-memory rate limiter. Forgetting that second
one is how a suite starts failing only when run in full — the auth rate limiter
is process-global, so five earlier logins will 429 the sixth.

`other_auth_headers` exists specifically so that cross-user isolation is easy
to test. Use it.

## Derive tests from scenarios

Each `WHEN` / `THEN` scenario in a change's delta spec becomes a test: the
`WHEN` is the arrangement, the `THEN` is the assertion. Keeping that mapping
visible is what makes requirement-to-test traceability real rather than
claimed.

Name tests so a failure reads as a statement about the system:

```python
def test_other_users_transactions_excluded(client, auth_headers, other_auth_headers):
def test_more_than_two_decimal_places_rejected(client, auth_headers):
```

Not `test_list_2`. A failing test name is the first thing anyone reads.

## The edge cases that matter here

- **Cross-user isolation** — for every endpoint that reads data. Highest value
  test in this codebase.
- **Money precision** — three decimal places, zero, negative, very large.
- **Type matching** — a transaction whose type disagrees with its category.
- **Referential integrity** — deleting a category that is in use.
- **Auth** — missing, malformed and expired tokens.
- **Pagination and ordering** — first page, last page, past the end, ties.
- **Empty results** — a summary over a period with no transactions.

## Coverage

The floor is **95%**, enforced by `[tool.coverage.report] fail_under`. It
applies wherever coverage runs, including CI.

Treat an uncovered line as a question — *what behaviour is unverified here?*
The answer is sometimes a missing test and sometimes dead code that should be
deleted.

**Never write a test just to move the number.** A test with no meaningful
assertion makes the metric lie, and a lying metric is worse than no metric
because people still trust it. If the floor cannot be reached honestly, say
which lines are genuinely untestable and why.

Coverage flags are deliberately not in `addopts`: that would make every
single-test run compute coverage and fail the floor. Use `make test-cov` or
`make quality` when you want the number.

## Running a subset while working

```bash
OTEL_ENABLED=false ENVIRONMENT=test JWT_SECRET=t .venv/bin/pytest tests/test_transactions.py -q
OTEL_ENABLED=false ENVIRONMENT=test JWT_SECRET=t .venv/bin/pytest -k isolation -q
```

Then `make quality` before reporting anything complete.
