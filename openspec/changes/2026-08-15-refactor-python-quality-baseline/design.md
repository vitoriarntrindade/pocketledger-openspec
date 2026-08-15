## Context

Every defect here predates the change that found it. The tools that would have
caught them — ruff, mypy, bandit, pytest-cov — were documented across the
repository but were not installed in the virtualenv, so nothing measured this
code until the quality gate was built.

That history shapes how the fixes should be made. A defect that has been latent
for months is not urgent, but it is also not safe to fix carelessly: the tests
that would catch a regression are the same tests that were never being run
under a gate.

## Goals / Non-Goals

**Goals:**

- `make quality` passes end to end, so the definition of done becomes real.
- Every fix addresses the cause. No suppression comments, no widened ignore
  lists, no lowered floor.
- No behaviour changes, so the diff can be reviewed as pure debt repayment.

**Non-Goals:**

- Improving test coverage beyond the existing floor. Coverage is 96% and above
  the threshold; adding tests is separate work.
- Tightening mypy (`disallow_untyped_defs`). That would create new debt inside
  a change whose purpose is to clear debt.
- Refactoring anything for style, readability or structure. The formatter's
  output is not an invitation to rewrite.

## Decisions

### Decision: format everything in one commit, separately from the fixes

**Context.** 38 files need formatting. Mixed with logic changes, that produces
a diff nobody can review — real fixes disappear among reflowed lines.

**Alternatives considered.** Formatting each file as its logic is touched
spreads the noise across every future change instead of containing it, and
leaves the gate red for longer.

**Trade-off.** One large mechanical commit disturbs `git blame` for those
files. That cost is paid once and is recoverable — `git blame
--ignore-rev` exists for exactly this — whereas unreviewable diffs are a
recurring cost.

**Consequence.** Formatting lands as its own commit, containing no logic
change. Every other commit here can then be read on its own.

### Decision: narrow the blind exception rather than suppress the warning

`_current_trace_id` currently wraps its body in `except Exception: pass`. Both
ruff (BLE001) and bandit (B110) flag it, and they are right: if OpenTelemetry
ever raises something unexpected, the failure disappears with no trace.

The suppression route — `# noqa: BLE001` plus a bandit exclusion — would clear
both reports while leaving the actual problem in place. Instead the handler
catches the specific error the call can raise and records the failure at debug
level, so it stays non-fatal but stops being invisible.

**Trade-off.** A narrower catch could let a genuinely unexpected exception
propagate into a log-formatting path. That is the correct outcome: a tracing
lookup failing in a way nobody anticipated is information, and losing it is how
observability code silently stops working.

### Decision: keep the readiness probe's broad catch, and scope the rule instead

Ruff flags `except Exception` in `/ready` as BLE001, the same rule that
correctly flagged `_current_trace_id`. Narrowing it to `SQLAlchemyError` was
tried first and immediately broke `test_ready_endpoint_when_db_unavailable`,
which simulates an unreachable database with a `RuntimeError`.

The failing test was the right signal. A readiness probe answers one question —
can this instance serve traffic? — and any failure reaching that point means
no. Narrowing the catch would let a driver, DNS or configuration error escape
as a 500, which tells an orchestrator less than an orderly 503 does.

The two cases look identical to the linter and are opposite in substance:
`_current_trace_id` swallowed its exception and returned `None`, hiding the
failure forever; `/ready` turns its exception into the response. The first is
the defect BLE001 exists to catch, the second is the intended design.

So BLE001 is scoped off for that one module, with the reasoning recorded in
`pyproject.toml` and in the code. This is a deliberate rule decision rather
than an inline suppression, which is what the constitution requires — and it
keeps this change's promise that no behaviour changes.

### Decision: make the trace test self-contained

`test_current_trace_id_matches_active_span` asserts that `_current_trace_id()`
returns the active span's id. It passes only when the application has installed
a real `TracerProvider`, which happens only when `OTEL_ENABLED` is true.

So the test currently measures an environment variable. With OTEL export
enabled the suite takes four minutes; with it disabled the test fails. Neither
state is acceptable in a gate.

The test now creates its own `TracerProvider` for the duration of the test.
This tests the function's actual contract — given an active recording span,
return its trace id — independently of how the application happens to be
configured.

**Alternative considered.** Forcing `OTEL_ENABLED=true` for the suite would
restore the four-minute runtime and the retry noise, trading a correctness
problem for a usability one.

### Decision: annotate the middleware returns rather than cast them

Four mypy errors are `Returning Any from function declared to return
"Response"`, because `call_next` is untyped in the Starlette stubs. Annotating
the local binding states the contract at the boundary where it is known, which
is more honest than `cast()` and more informative than `# type: ignore`.

## Risks / Trade-offs

**Formatting could change behaviour in principle.** It does not in practice —
`ruff format` is semantics-preserving — but the whole suite runs after it, and
this is precisely why the formatting commit is isolated: if something did
break, the commit that caused it is unambiguous.

**`git blame` noise.** Discussed above; mitigated by keeping the formatting
commit pure and recording its hash here for `--ignore-rev`.

**The coverage floor has almost no margin.** Measured at 96% against a floor of
95%. This change adds no code, so it should not move, but any future change
that adds an untested line will fail immediately. That is the floor working as
intended, not a defect.
