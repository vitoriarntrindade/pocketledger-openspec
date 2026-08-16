# PocketLedger — project constitution

These are the permanent rules of this repository. They apply to every change,
without exception, and they are the only thing in this file. Anything that is a
tutorial, a worked example or a "how do I…" belongs in a skill or in `docs/`,
where it loads on demand instead of occupying context on every turn.

> This file is configuration, not documentation. It sits in the repository root
> alongside `pyproject.toml` and `Makefile` because that is the location Claude
> Code discovers reliably. The project rule that Markdown belongs in `docs/`
> still holds for everything else.

---

## 1. The definition of done

A change is finished when `make quality` exits zero. Not before, and not
because it looks finished.

That command is the whole gate: formatting, linting, type checking, the test
suite, the coverage floor, the security scan, the secret scan and OpenSpec
validation. It is the same command a human runs, an agent runs, and CI runs.

**A failing gate is never resolved by weakening the gate.** Deleting a test,
adding a blanket `# noqa`, loosening a rule or lowering the coverage floor are
all ways of reporting success while delivering failure. Diagnose the cause, fix
the cause, run it again.

If a gate genuinely must be relaxed, that is a change to the project's
standards: it needs its own justification, written down, in the change that
does it.

## 2. Every change is classified before it is built

| Tier | Examples | Process |
|---|---|---|
| **TRIVIAL** | typo, comment, docstring wording | no OpenSpec change needed |
| **SMALL** | one validation rule, a narrow endpoint tweak | branch + commit traceability |
| **STANDARD** | a new feature that is not cross-cutting | full spec-driven workflow |
| **COMPLEX** | auth, schema, external integration, cross-cutting | full workflow + security and architecture review |
| **CRITICAL** | destructive migration, secrets, payments, central auth | full workflow + explicit human authorisation before any irreversible step |

When a request sits between two tiers, take the higher one.

## 3. Specification precedes implementation

For STANDARD, COMPLEX and CRITICAL changes, the work originates from an
OpenSpec change under `openspec/changes/<name>/` containing a proposal, delta
specs, a design and tasks.

**Behaviour that exists only in conversation does not exist.** When a
behavioural decision is reached while discussing an active change, write it
into that change's artifacts before continuing to implement.

Requirements are written in verifiable language, and scenarios in
`WHEN` / `THEN` form so that each one maps onto a test. Every requirement needs
at least one test; the verifier checks that mapping and reports any requirement
without one.

Use the OpenSpec CLI (`openspec new change`, `openspec validate`,
`openspec status`). Changes live in `openspec/changes/<name>/` — there is no
`active/` subdirectory.

## 4. Git discipline

- **Never implement on `main`.** Create the branch before the first edit.
- Branch naming follows `{type}/{slug}`, matching the commit prefix:
  `feature/`, `bugfix/`, `security/`, `refactor/`, `perf/`, `docs/`, `chore/`.
- Commit messages use `{prefix}: {summary}`, in the imperative, explaining
  *why* rather than restating the diff.
- Commits are coherent: one logical change each, and no unrelated files.
- **Never force push. Never rewrite shared history. Never merge.** Merging is
  always a human decision.

## 5. The human gate

Investigate, specify, branch, implement, refactor, test, fix, document, verify
and commit locally — all of that is autonomous, and small recoverable failures
are fixed without asking.

Then stop. Produce the final compliance report and wait.

**No push and no pull request before explicit human acceptance.** Nothing is
merged, ever.

## 6. Code standards

The full guidance lives in the `python-best-practices` skill. The
non-negotiable parts:

- Type hints on every function signature.
- Maximum 78 characters per line.
- Google-style docstrings on public functions, classes and modules — where
  they explain *why*, since the code already says what.
- Exception chaining: `raise ... from err`.
- Routers return Pydantic schemas, never ORM models.
- Money is `Decimal` / `NUMERIC(12,2)`, never `float`.
- Every query is scoped to the authenticated user. There is no code path that
  reads another user's data.

Architecture is layered: **routers → services → models**. Routers handle HTTP
and validation; services hold business logic; models hold persistence. A router
containing business logic, or a service importing FastAPI, is a defect.

## 7. Tests

- New behaviour ships with tests. A bug fix ships with a regression test.
- Tests assert behaviour, not implementation.
- Coverage floor is **95%**, enforced by the build. Coverage is a floor, not a
  goal: tests written only to raise the number are worse than no tests, because
  they make the number lie.
- The suite runs against real PostgreSQL. `make test` starts it for you.

## 8. Documentation moves with the code

A change updates the documentation it invalidates — README, API docs,
architecture notes, configuration, environment variables, migration notes. It
does not touch documentation unrelated to it.

Architectural decisions worth persisting are recorded with their context,
alternatives, trade-offs and consequences. Trivial decisions are not.

## 9. Secrets

Never commit real credentials. Never read `~/.ssh`, cloud credentials or
tokens. `.env.example` holds variable names with placeholder values; the real
`.env` is never tracked.

## 10. Cost discipline

Prefer the cheapest mechanism that can answer correctly:

> deterministic script → cheapest model → mid model → most capable model

If `ruff`, `mypy`, `pytest`, `coverage` or `git` can answer a question, they
answer it. A language model is for judgement, not for restating what a tool
already decided.

---

## Where things live

| Path | What |
|---|---|
| `app/` | application code (`api/`, `services/`, `models/`, `schemas/`, `core/`, `infrastructure/`) |
| `tests/` | test suite |
| `openspec/specs/` | current system specifications |
| `openspec/changes/` | in-flight changes; `archive/` holds completed ones |
| `scripts/` | deterministic workflow tooling and guards |
| `.claude/agents/` | specialised subagents and their model routing |
| `.codex/agents/` | Codex subagent profiles and hook configuration |
| `.claude/skills/` | canonical shared skills |
| `.agents/skills/` | Codex link to the canonical shared skills |
| `docs/agentic-development.md` | how this whole workflow fits together |

## Commands

```
make quality     the definition of done — run before reporting anything complete
make fast        static checks only, for the edit loop
make fix         apply safe autofixes, then the full gate
make test        run the suite with coverage (starts the database)
make db          start PostgreSQL and create the test database
```
