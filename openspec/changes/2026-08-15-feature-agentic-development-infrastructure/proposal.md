## Why

The repository documents a quality pipeline that does not exist. `.claude/claude.md`,
`docs/standards/BEST_PRACTICES.md` and `.pre-commit-config.yaml` all describe enforcement
through ruff, mypy, flake8, pydocstyle, pre-commit and a `make check` command. An audit of
the actual environment found none of it installed or wired:

- the virtualenv contained only `pytest` and `httpx` — no linter, no type checker, no
  coverage plugin, no pre-commit;
- there is no `Makefile`, so every `make check` instruction in the docs is dead;
- there is no `.github/` directory, so nothing verifies a merge remotely;
- `pyproject.toml` and `.pre-commit-config.yaml` are unmodified copies of generic templates
  (`name = "your-project"`, `target-version = "py38"`) while the code targets Python 3.12 and
  uses `X | None` syntax that a py38 target rejects;
- `.claude/claude.md` is lowercase, so on a case-sensitive filesystem it is not loaded as
  project memory at all.

Measuring the real baseline once the tooling was installed confirmed the cost of that gap:
34 ruff violations, 33 of 55 files needing reformatting, 7 mypy errors, one failing test, and
coverage sitting at exactly 95.00% with no gate to hold it there.

The consequence is that autonomy is unsafe. An agent asked to build a feature today has no
deterministic definition of done, no enforced branch discipline, no protection against
destructive git operations, and no independent verifier. Every guarantee depends on the model
remembering to behave. This change replaces remembered discipline with enforced discipline.

## What Changes

- A root `CLAUDE.md` becomes the project constitution: permanent, universal rules only
  (definition of done, quality gates, git discipline, change classification, spec linkage).
  The tutorial content currently in `.claude/claude.md` moves to skills and docs.
- Five skills carry reusable competence with progressive disclosure, replacing one 639-line
  monolith: the existing `python-best-practices` and `repository-security-audit` are
  restructured and kept; `spec-driven-workflow`, `pocketledger-architecture` and
  `testing-and-coverage` are added.
- Seven subagents provide context isolation and explicit model routing, so that the agent
  which implements a change is never the only agent that verifies it.
- Deterministic hooks enforce what must not depend on model judgement: dangerous shell
  commands and writes outside the repository are blocked before they run, and edited Python
  files are formatted after each edit.
- A single `make quality` command becomes the automated definition of done, running the
  ordered gate: format, lint, types, tests, coverage floor, security scan, secret scan and
  OpenSpec validation.
- Coverage gains a hard floor of 95%.
- Real project configuration replaces the template `pyproject.toml`, and `.flake8` is retired
  in favour of ruff as the single linting authority.
- A GitHub Actions workflow runs the same gate remotely, so a merge never depends solely on
  the agent's own claim that the work is correct.
- The workflow is documented end to end in `docs/agentic-development.md`, including a Mermaid
  diagram of the feature lifecycle.

Explicitly **not** included: fixing the 34 ruff violations, 7 mypy errors and failing test
that this infrastructure exposes. Those are pre-existing defects in application code and are
tracked as a separate change so that infrastructure decisions and debt repayment remain
independently traceable.

## Capabilities

### New Capabilities

- `agentic-workflow`: how a change travels from a feature request to a merged pull request in
  this repository — classification, specification, branch isolation, implementation,
  verification gates, independent review and the human acceptance gate.

### Modified Capabilities

None. No runtime behaviour of the application changes.

## Impact

**Added**

- `CLAUDE.md`, `Makefile`, `docs/agentic-development.md`
- `.claude/settings.json` (versioned team configuration, replacing reliance on the ad-hoc
  personal allowlist in `.claude/settings.local.json`)
- `.claude/agents/` — seven agent definitions
- `.claude/skills/spec-driven-workflow/`, `.claude/skills/pocketledger-architecture/`,
  `.claude/skills/testing-and-coverage/`
- `scripts/quality.sh`, `scripts/dev-db.sh`, `scripts/guard-bash.py`, `scripts/guard-write.py`,
  `scripts/format-python.sh`
- `.github/workflows/quality.yml`
- `tests/test_agentic_infrastructure.py` — behavioural tests for the guard hooks

**Modified**

- `pyproject.toml` — real project metadata, Python 3.12 target, consolidated ruff/mypy/pytest
  /coverage configuration with the 95% floor
- `.pre-commit-config.yaml` — reduced to the repository-protection layer that must hold even
  when Claude is not involved
- `.claude/skills/python-best-practices/` — restructured for progressive disclosure
- `requirements-dev.txt` — declares the quality tooling that the docs already assumed
- `README.md` — a pointer to the agentic development documentation

**Removed**

- `.claude/claude.md` — superseded by `CLAUDE.md`; its tutorial content is redistributed
- `.flake8` — ruff is the single linting authority
- `.claude/scripts/new-change.sh` — writes to `openspec/changes/active/`, a layout OpenSpec
  1.8 does not recognise, producing changes its CLI cannot see
- `.claude/skills/new-development-change/` — depends on the broken script above

**Unchanged by deliberate decision**

- `.claude/skills/openspec-*/` and `.claude/commands/opsx/` are generated by OpenSpec itself
  (`generatedBy: "1.8.0"`) and are regenerated by `openspec update`. They are silenced from
  the model's skill listing via `skillOverrides` rather than deleted.
- No operating-system sandbox is enabled. `socat`, required by the Linux sandbox network
  proxy, is absent, and the test suite depends on reaching Postgres on a locally published
  port. The configuration is documented as an opt-in step instead.
