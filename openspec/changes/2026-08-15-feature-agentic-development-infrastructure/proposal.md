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

- Root `AGENTS.md` and `CLAUDE.md` become the Codex and Claude Code
  constitutions: permanent, universal rules only (definition of done, quality
  gates, git discipline, change classification, spec linkage). The tutorial
  content currently in `.claude/claude.md` moves to skills and docs.
- Five skills carry reusable competence with progressive disclosure, replacing one 639-line
  monolith: the existing `python-best-practices` and `repository-security-audit` are
  restructured and kept; `spec-driven-workflow`, `pocketledger-architecture` and
  `testing-and-coverage` are added.
- Shared skills are versioned for both supported coding agents: Codex reads
  `.agents/skills/` and Claude Code reads `.claude/skills/`. Their permitted
  differences are documented and verified so a second runtime does not create
  an unreviewed second source of truth.
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
- Pre-commit is reduced to the irreversible-harm layer and no longer runs
  ruff, flake8 or mypy, since those already run on every edited file, in the
  gate and in CI. This narrows an existing requirement of the `code-structure`
  capability, which the delta spec records.
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

- `code-structure`: its **Code quality automation** requirement described
  enforcement that this change removes. It required pre-commit to run ruff,
  flake8 and mypy and to block the commit on failure; flake8 is retired here,
  and lint, format and type checks are deliberately taken out of pre-commit so
  that layer holds only what cannot be undone after a commit lands. Leaving
  the requirement as written would leave a current spec asserting something
  the repository no longer does, so it is modified to describe what actually
  enforces quality now: the single `make quality` gate, the same gate re-run
  in CI, and pre-commit reduced to irreversible-harm protection. The
  requirement's CI and `make check` scenarios are corrected in the same delta
  — CI runs on the default branch and on pull requests targeting it, not on
  every push, and `make check` now resolves as an alias of `make quality`.

No runtime behaviour of the application changes.

## Impact

**Added**

- `AGENTS.md`, `CLAUDE.md`, `Makefile`, `docs/agentic-development.md`
- `.claude/settings.json` (versioned team configuration, replacing reliance on the ad-hoc
  personal allowlist in `.claude/settings.local.json`)
- `.claude/agents/` — seven agent definitions
- `.codex/agents/`, `.codex/hooks.json` — Codex equivalents of the agent
  profiles and hook wiring, versioned so Codex works after clone
- `.agents/skills/` — Codex-facing copy of the shared skills, plus the
  `source-command-opsx-*` compatibility wrappers
- `.claude/skills/spec-driven-workflow/`, `.claude/skills/pocketledger-architecture/`,
  `.claude/skills/testing-and-coverage/`
- `scripts/quality.sh`, `scripts/dev-db.sh`, `scripts/guard-bash.py`,
  `scripts/guard-write.py`, `scripts/format-python.sh`,
  `scripts/scan-secrets.sh`, `scripts/session-context.sh`
- `.github/workflows/quality.yml`
- `tests/test_agentic_infrastructure.py` — behavioural tests for the guard hooks
- `compliance-report.md` — final local verification evidence and accepted
  residual risks

**Modified**

- `pyproject.toml` — real project metadata, Python 3.12 target, consolidated ruff/mypy/pytest
  /coverage configuration with the 95% floor
- `.pre-commit-config.yaml` — reduced to the repository-protection layer that must hold even
  when Claude is not involved
- `.claude/skills/python-best-practices/` — restructured for progressive disclosure, and
  its reference material corrected where it still instructed flake8 and `make check`
- `requirements-dev.txt` — declares the quality tooling that the docs already assumed
- `README.md` — a pointer to the agentic development documentation
- `docs/README.md` — repointed at the current source of truth, since it
  indexed commands and layouts that never existed
- `docs/START-HERE.md` — the entry path aligned with the constitution and the
  real gate
- `docs/standards/BEST_PRACTICES.md` — its command list rewritten: it taught
  `make check`, `make fix-all` and `make type-check`, none of which existed,
  and a "Problemas Atuais" section describing defects the stacked change has
  since fixed
- `docs/reports/QUALITY_REPORT.md` — annotated as a historical record of
  2026-08-13 rather than a current status, with its `.flake8` reference and
  its flake8/mypy command list corrected to the real gate
- `docs/development/CLEAN-CODE-WORKFLOW.md`, `DEVELOPMENT.md`,
  `NEW-FEATURES.md`, `SETUP-WORKFLOW.md`, `WORKFLOW-EXAMPLE.md`,
  `WORKFLOW-QUICK-START.md` — annotated rather than deleted: each instructs at
  least one command or layout that does not work (`make check` without a
  Makefile, uninstalled tools, `.claude/claude.md`,
  `openspec/changes/active/`), while the reasoning in them is still worth
  keeping

**Removed**

- `.claude/claude.md` — superseded by `CLAUDE.md`; its tutorial content is redistributed
- `.flake8` — ruff is the single linting authority
- `.claude/scripts/new-change.sh` — writes to `openspec/changes/active/`, a layout OpenSpec
  1.8 does not recognise, producing changes its CLI cannot see
- `.claude/skills/new-development-change/` — depends on the broken script above
- `.claude/change-types.yaml` — its taxonomy now has a single source of truth in
  `CLAUDE.md` §2 and §4 and in the classification reference; keeping a second,
  drifting copy is the redundancy this change exists to remove
- `.claude/skills/python-best-practices/README.md`, `check-quality.sh` and the four
  `*.example` config files — they instructed copying a Python 3.8 / flake8
  configuration into the project root, contradicting the real configuration

**Unchanged by deliberate decision**

- `.claude/skills/openspec-*/` and `.claude/commands/opsx/` are generated by OpenSpec itself
  (`generatedBy: "1.8.0"`) and are regenerated by `openspec update`. They are silenced from
  the model's skill listing via `skillOverrides` rather than deleted.
- No operating-system sandbox is enabled. `socat`, required by the Linux sandbox network
  proxy, is absent, and the test suite depends on reaching Postgres on a locally published
  port. The configuration is documented as an opt-in step instead.
