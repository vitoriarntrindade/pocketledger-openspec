## 1. Formatting

- [ ] 1.1 Run `ruff format` across the project and commit the result on its own,
      with no logic change mixed in
- [ ] 1.2 Confirm the full suite still passes after formatting
- [ ] 1.3 Record the formatting commit hash in `design.md` for `git blame --ignore-rev`

## 2. Lint violations

- [ ] 2.1 Narrow the blind exception handler in `app/core/logging.py` and make its
      failure visible at debug level, resolving both BLE001 and bandit B110
- [ ] 2.2 Fix the remaining lint violations at their cause, without suppression
      comments or widened ignore lists
- [ ] 2.3 Confirm `ruff check .` is clean

## 3. Type errors

- [ ] 3.1 Annotate the four `call_next` returns in `app/api/middleware.py`
- [ ] 3.2 Fix the validator typing in `app/schemas/transaction.py`
- [ ] 3.3 Confirm `mypy app` is clean

## 4. The failing test

- [ ] 4.1 Give `test_current_trace_id_matches_active_span` its own `TracerProvider`
      so it no longer depends on the application's global tracing configuration
- [ ] 4.2 Confirm it passes with `OTEL_ENABLED=false`, which is how the gate runs

## 5. Verification

- [ ] 5.1 Run the full gate and confirm every mandatory check passes
- [ ] 5.2 Confirm no behaviour changed: the same tests pass, with the same intent
- [ ] 5.3 Confirm coverage is still at or above the floor
