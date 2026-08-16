## Why

The agentic development infrastructure introduced a quality gate that runs
ruff, mypy, bandit and the test suite with a coverage floor. Running it for the
first time revealed defects that had been present but unmeasured, because none
of those tools were installed:

- **38 files** are not formatted to the project's own 78-character standard;
- **14 lint violations**, including a blind `except Exception: pass` that
  silently swallows failures;
- **7 mypy errors**, four of them the same unchecked `Any` return in middleware;
- **1 failing test** — `test_current_trace_id_matches_active_span` depends on
  the application's global OpenTelemetry provider, so it passes or fails
  according to an environment variable rather than according to the code;
- **1 bandit finding** (B110, low) on the same swallowed exception.

These are not new. They are what the repository looked like all along, now
visible. They are kept separate from the infrastructure change deliberately, so
that the decision to build the gate and the work of paying down what it found
remain independently traceable in the history.

Until this lands, `make quality` cannot pass, which means the definition of
done cannot actually be met and the gate has no teeth.

## What Changes

- Every Python file is formatted with `ruff format`, applying the project's
  existing 78-character standard uniformly for the first time.
- The 14 lint violations are fixed at their cause. The blind exception handler
  in `_current_trace_id` is narrowed and its failure is no longer silent.
- The 7 mypy errors are fixed by annotating what was inferred as `Any`, rather
  than by suppressing the check.
- `test_current_trace_id_matches_active_span` establishes its own
  `TracerProvider` instead of depending on the application's global tracing
  configuration, so it tests the code rather than the environment.
- The bandit B110 finding is resolved by the same exception-handling fix.

Every existing test still passes, unchanged in intent, and no endpoint, schema,
model or service behaviour changes.

**One deliberate exception to that**, in `app/core/logging.py`: removing the
blind exception handler means an unexpected OpenTelemetry failure now
propagates out of the logging filter instead of being silently swallowed, and
the module now fails at import if `opentelemetry` is missing rather than
degrading quietly. Both are intended — hiding its own failures is precisely how
observability code stops working unnoticed, and OpenTelemetry is a hard
dependency, so its absence is a broken installation. The reasoning, and the
narrower fix that was tried first and abandoned, are recorded in `design.md`.

## Capabilities

### New Capabilities

None. This change adds no behaviour.

### Modified Capabilities

None. The `code-structure` capability already requires PEP 8 compliance, type
safety and the 78-character limit. This change makes the code satisfy
requirements that were already specified — it does not alter them.

## Impact

**Modified**

- 38 Python files across `app/`, `tests/` and `alembic/` — formatting only
- `app/core/logging.py` — exception handling narrowed
- `app/api/middleware.py` — return type annotations
- `app/schemas/transaction.py` — type annotation on the validator
- `tests/test_observability.py` — the trace test made self-contained

**Unchanged**

- No endpoint, schema, model or service behaviour
- No configuration defaults
- No dependency versions
