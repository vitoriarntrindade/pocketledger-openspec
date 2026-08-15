## 1. Project configuration baseline

- [ ] 1.1 Rewrite `pyproject.toml` with real project metadata, Python 3.12 target, and
      consolidated ruff, mypy, pytest and coverage configuration including the 95% floor
- [ ] 1.2 Delete `.flake8` and move the complexity threshold to ruff `C901`
- [ ] 1.3 Declare the quality tooling in `requirements-dev.txt`
- [ ] 1.4 Reduce `.pre-commit-config.yaml` to the repository-protection layer, on current
      hook versions and current `stages` syntax

## 2. Deterministic gate and scripts

- [ ] 2.1 Write `scripts/dev-db.sh`: idempotently start the `db` service and create the test
      database, never dropping or truncating
- [ ] 2.2 Write `scripts/quality.sh`: ordered gate over format, lint, types, tests, coverage,
      security, secrets and OpenSpec validation, with a `--fast` subset
- [ ] 2.3 Write `Makefile` targets wrapping the gate, so the `make check` referenced across
      existing documentation resolves
- [ ] 2.4 Verify the gate reports the known pre-existing failures rather than masking them

## 3. Guard hooks

- [ ] 3.1 Write `scripts/guard-bash.py` blocking pushes to the default branch, force pushes,
      destructive resets, `sudo`, recursive deletion outside the repository, and credential access
- [ ] 3.2 Write `scripts/guard-write.py` blocking writes outside the repository and to secret
      files, while permitting `.env.example` and fixtures
- [ ] 3.3 Write `scripts/format-python.sh` formatting only the single edited file
- [ ] 3.4 Prove each guard by piping a synthetic hook payload and asserting the decision

## 4. Claude Code configuration

- [ ] 4.1 Write `.claude/settings.json` with `defaultMode`, permission allow/ask/deny lists,
      hook registrations and `skillOverrides`
- [ ] 4.2 Validate the settings JSON structure and hook wiring with `jq`
- [ ] 4.3 Document the deferred sandbox configuration and its prerequisites

## 5. Constitution and skills

- [ ] 5.1 Write root `CLAUDE.md` containing only permanent, universal rules
- [ ] 5.2 Remove `.claude/claude.md`, redistributing its tutorial content
- [ ] 5.3 Restructure `python-best-practices` for progressive disclosure and current tooling
- [ ] 5.4 Write the `spec-driven-workflow` skill covering classification and lifecycle
- [ ] 5.5 Write the `pocketledger-architecture` skill covering layer rules and templates
- [ ] 5.6 Write the `testing-and-coverage` skill covering fixtures, the database requirement
      and coverage strategy
- [ ] 5.7 Remove `.claude/scripts/new-change.sh` and the `new-development-change` skill that
      depends on its unrecognised change layout

## 6. Subagents

- [ ] 6.1 Write `spec-architect`, `feature-implementer` and `spec-verifier` definitions
- [ ] 6.2 Write `test-engineer`, `quality-reviewer`, `security-reviewer` and
      `documentation-reviewer` definitions
- [ ] 6.3 Confirm each definition declares its model and a minimal tool set

## 7. Infrastructure tests

- [ ] 7.1 Write `tests/test_agentic_infrastructure.py` asserting guard behaviour for blocked
      and permitted operations
- [ ] 7.2 Confirm the tests pass and are non-destructive

## 8. CI and documentation

- [ ] 8.1 Write `.github/workflows/quality.yml` running the same gates remotely
- [ ] 8.2 Write `docs/agentic-development.md` with the Mermaid lifecycle diagram
- [ ] 8.3 Reconcile the existing workflow documents with the new single source of truth
- [ ] 8.4 Add the pointer to the agentic documentation in `README.md`

## 9. Verification

- [ ] 9.1 Run the full gate and record each result
- [ ] 9.2 Delegate independent verification of spec compliance to `spec-verifier`
- [ ] 9.3 Produce the final compliance report and stop for human acceptance
- [ ] 9.4 Open the follow-up change for the pre-existing quality debt
