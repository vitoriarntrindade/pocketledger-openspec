## 1. Formatting

- [x] 1.1 Run `ruff format` across the project and commit the result on its own,
      with no logic change mixed in
- [x] 1.2 Confirm the full suite still passes after formatting
- [x] 1.3 Record the formatting commit hash in `design.md` for `git blame --ignore-rev`

## 2. Lint violations

- [x] 2.1 Remove the blind exception handler in `app/core/logging.py`, resolving
      both BLE001 and bandit B110. Narrowing it and logging at debug level was
      the original plan; it was abandoned because the function runs inside a
      logging filter, where logging its own failure risks recursion. See the
      design decision for the behaviour this changes.
- [x] 2.2 Fix the remaining lint violations at their cause, without suppression
      comments or widened ignore lists
- [x] 2.3 Confirm `ruff check .` is clean

## 3. Type errors

- [x] 3.1 Annotate the four `call_next` returns in `app/api/middleware.py`
- [x] 3.2 Fix the validator typing in `app/schemas/transaction.py`
- [x] 3.3 Confirm `mypy app` is clean

## 4. The failing test

- [x] 4.1 Give `test_current_trace_id_matches_active_span` its own `TracerProvider`
      so it no longer depends on the application's global tracing configuration
- [x] 4.2 Confirm it passes with `OTEL_ENABLED=false`, which is how the gate runs

## 5. Verification

- [x] 5.1 Run the full gate and confirm every mandatory check passes
- [x] 5.2 Confirm no behaviour changed: the same tests pass, with the same intent
- [x] 5.3 Confirm coverage is still at or above the floor
