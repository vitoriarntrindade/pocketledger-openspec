---
name: pocketledger-architecture
description: The layering rules, module conventions and domain invariants of this FastAPI codebase — where each kind of code belongs, how ownership scoping works, and how to add a new resource without breaking the pattern. Use before writing or reviewing any application code.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# PocketLedger architecture

Read this before the first edit to `app/`. Inferring the conventions from one
file usually reproduces that file's accidents rather than the pattern.

## The layers

```
HTTP request
   │
   ▼
app/api/routers/       HTTP shape, status codes, validation, auth dependency
   │                   → returns Pydantic schemas, never ORM models
   ▼
app/services/          business logic, invariants, ownership scoping
   │                   → returns ORM models, raises domain errors
   ▼
app/models/            SQLAlchemy 2.0 typed mappings, constraints
   │
   ▼
PostgreSQL
```

Two rules make the layering real rather than decorative:

**A router contains no business logic.** It unpacks the request, calls one
service function, and converts the result to a schema. If a router branches on
domain state, that branch belongs in the service.

**A service imports nothing from FastAPI.** Services take a `Session` and a
`User` and raise domain errors from `app.core.errors`. The moment a service
knows about HTTP, it can no longer be tested or reused without HTTP.

Supporting modules:

| Path | Holds |
|---|---|
| `app/schemas/` | Pydantic request and response models |
| `app/core/config.py` | settings, and the production readiness guard |
| `app/core/errors.py` | domain errors, mapped to HTTP by `api/error_handlers.py` |
| `app/core/security.py` | password hashing, JWT encode and decode |
| `app/api/deps.py` | `get_current_user` and other request dependencies |
| `app/api/middleware.py` | request id, security headers, auth rate limiting |
| `app/infrastructure/` | database engine, metrics, tracing |

## The invariant that governs everything

**Every query is scoped to the authenticated user.** There is no code path that
reads another user's data, and adding one is the most serious defect possible
in this codebase.

In practice this means a service never looks a resource up by id alone:

```python
# Correct: ownership is part of the lookup, so a foreign id is simply not found.
def get_owned_category(db: Session, user: User, category_id: int) -> Category:
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user.id)
        .first()
    )
    if category is None:
        raise NotFoundError("Category not found.")
    return category
```

```python
# Wrong: returns another user's row, and an ownership check bolted on
# afterwards leaks existence through a different error message.
category = db.get(Category, category_id)
```

The error says "not found" for a resource that exists but belongs to someone
else. That is deliberate — distinguishing the two would leak whether the row
exists.

## Domain invariants

These are properties of the product, not implementation details. Breaking one
is a bug even if every test passes.

- **Money is `Decimal`, stored as `NUMERIC(12, 2)`.** Never `float`. A rounding
  error in a ledger is a correctness failure, not an approximation.
- **Balance is always computed, never stored.** It is
  `total_income - total_expenses`, derived at query time from real
  transactions. A stored balance can disagree with its own history.
- **A transaction's type must match its category's type.** Validate before
  mutating anything, so a rejected edit leaves the row untouched.
- **A category's type is immutable** once created.
- **A category in use cannot be deleted.** The database enforces this too.

## Adding a new resource

Follow the existing shape rather than inventing one. Templates live in
`.claude/templates/`:

1. `app/models/<name>.py` — SQLAlchemy model with a `user_id` foreign key.
2. Alembic migration — `alembic revision --autogenerate`, then **read what it
   generated**. Autogenerate misses constraint and index changes regularly.
3. `app/schemas/<name>.py` — `Create`, `Update`, `Out`, with
   `from_attributes=True` on the output schema.
4. `app/services/<name>_service.py` — module-level functions taking
   `(db, user, ...)`. Include a `get_owned_<name>` helper and use it everywhere.
5. `app/api/routers/<name>.py` — thin router from the template.
6. Register in `app/main.py`.
7. Tests in `tests/test_<name>.py`, including cross-user isolation.

`.claude/scripts/generate-component.sh router <name>` and
`... service <name>` scaffold steps 4 and 5 from the templates.

## Errors

Raise domain errors from services; never `HTTPException`. The mapping to
status codes lives in `app/api/error_handlers.py`, which also produces the
error envelope every response shares.

| Raise | Becomes |
|---|---|
| `NotFoundError` | 404 |
| `ValidationError` | 422 |
| `ConflictError` | 409 |
| `UnauthorizedError` | 401 |

Every response carries `X-Request-ID`, correlating logs, metrics and traces.
When adding a log statement, use the structured `extra` fields rather than
formatting values into the message, and never log credentials.

## Reference

- `references/conventions.md` — naming, module layout and import ordering
- `references/observability.md` — logging, metrics and tracing conventions
