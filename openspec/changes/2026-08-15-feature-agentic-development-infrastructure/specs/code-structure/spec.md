# Code Structure & Quality

## MODIFIED Requirements

### Requirement: Code quality automation

The system SHALL enforce quality standards through automated formatting,
linting and type checking executed by a single command that a developer, an
agent and CI all run identically, and SHALL restrict commit-time enforcement
to the defects that cannot be undone once a commit lands.

Ruff SHALL be the only linter. The system SHALL NOT rely on pre-commit hooks
to run linting, formatting or type checking, because a check that is cheap in
the gate and in CI becomes, at commit time, an incentive to bypass the hook
entirely.

#### Scenario: One command executes every quality check
- **WHEN** a developer or an agent runs `make quality`
- **THEN** the target delegates to `scripts/quality.sh`, which runs
  formatting, lint, type checking, the security scan, the secret scan,
  specification validation, and the test suite with its coverage floor
- **AND** the command exits non-zero if any of them fails
- **AND** the summary reports every check as `PASS`, `WARN` or `FAIL`

#### Scenario: Pre-commit hooks prevent non-compliant code
- **WHEN** a developer attempts to commit a private key, a real `.env` file,
  an oversized file, or unresolved merge-conflict markers
- **THEN** a pre-commit hook registered for that purpose blocks the commit,
  those hooks being `detect-private-key`, `check-added-large-files`,
  `check-merge-conflict` and a local hook matching `^\.env$`
- **AND** "non-compliant" at this layer means only what cannot be undone once
  the commit lands, the rest being enforced by the gate and by CI

#### Scenario: Pre-commit does not duplicate the lint and type gates
- **WHEN** a developer commits code carrying lint, formatting or typing
  defects and no irreversible harm
- **THEN** no pre-commit hook blocks it, the configuration registering no
  ruff, flake8, black, isort or mypy hook
- **AND** those defects are still caught by `make quality` before the change
  may be reported done, and by CI before it may be merged

#### Scenario: Ruff is the single linting authority
- **WHEN** linting runs in any layer — the post-edit hook, the gate, or CI
- **THEN** ruff is the only linter invoked by each of them
- **AND** no `.flake8` file exists in the repository
- **AND** the complexity threshold flake8 previously enforced is configured as
  ruff's `C90` mccabe rules with `max-complexity` set in `pyproject.toml`

#### Scenario: CI/CD validates code quality
- **WHEN** code is pushed to the default branch, or a pull request targets it
- **THEN** the CI workflow runs formatting, lint, type checking, the security
  scan, the secret scan, the tests with the coverage floor, and specification
  validation
- **AND** the workflow triggers on exactly those two events, not on a push to
  any branch
- **AND** it also runs `pre-commit run --all-files`, so the irreversibility
  hooks bind remotely rather than only for a developer who ran
  `pre-commit install`
- **AND** the build fails if any check fails

#### Scenario: Developers can verify locally
- **WHEN** a developer runs `make check`
- **THEN** the same gate CI runs executes locally, the `Makefile` defining
  `check` as an alias of `quality` so that the command named across the older
  documentation still resolves
- **AND** the report shows pass/fail status for every check

#### Scenario: A failing check is not resolved by weakening the gate
- **WHEN** any quality check fails
- **THEN** the gate exits non-zero and states that the failure must not be
  resolved by deleting a test, relaxing a rule or lowering the coverage floor
- **AND** the coverage floor stays at 95 and no blanket suppression is added
  in its place

The last scenario is only partly mechanisable: that a *cause* was fixed rather
than concealed is a judgement, made by review and by the constitution's first
rule. What a test can assert is the observable half — that the gate refuses to
pass, that it says so, and that the floor and the rule set were not lowered to
make it pass.
