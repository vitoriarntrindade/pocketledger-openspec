## Purpose

Defines how a change travels from a feature request to a merged pull request in this
repository: how it is classified, why it must originate from a specification, where it may be
implemented, which gates it must pass, who verifies it, and at which point a human decides.
The capability exists so that autonomy rests on enforced guarantees rather than on the agent
remembering to behave.

## ADDED Requirements

### Requirement: Change Classification

The system SHALL classify every incoming change request into exactly one of five
complexity tiers — TRIVIAL, SMALL, STANDARD, COMPLEX or CRITICAL — before any
implementation work begins, and SHALL apply the process obligations of that tier.

#### Scenario: A typo correction is classified TRIVIAL
- **WHEN** a request only corrects spelling, a comment, or a docstring without altering behaviour
- **THEN** the change is classified TRIVIAL
- **AND** it may proceed without a full OpenSpec change

#### Scenario: A localised validation change is classified SMALL
- **WHEN** a request adds a single validation rule or a narrowly scoped endpoint change
- **THEN** the change is classified SMALL
- **AND** it follows a reduced process that still records traceability

#### Scenario: A new feature is classified STANDARD
- **WHEN** a request introduces new user-visible behaviour that is not cross-cutting
- **THEN** the change is classified STANDARD
- **AND** it follows the full specification-driven workflow

#### Scenario: An authentication or schema change is classified at least COMPLEX
- **WHEN** a request touches authentication, authorisation, the database schema, an external
  integration, or spans multiple architectural layers
- **THEN** the change is classified COMPLEX or higher
- **AND** specialised security and architecture review are required

#### Scenario: A destructive data operation is classified CRITICAL
- **WHEN** a request involves a destructive migration, secret material, payment handling, or
  central authentication
- **THEN** the change is classified CRITICAL
- **AND** no irreversible operation is executed without explicit human authorisation

### Requirement: Specification Precedes Implementation

The system SHALL require that every change classified STANDARD, COMPLEX or CRITICAL
originates from an OpenSpec change containing, at minimum, a proposal, delta specs, a design
and a task list, and SHALL NOT accept behaviour that exists only in conversation.

#### Scenario: Implementation without a specification is refused
- **WHEN** implementation is requested for a STANDARD or higher change that has no
  corresponding directory under `openspec/changes/`
- **THEN** the specification is authored first
- **AND** implementation begins only once the planning artifacts exist

#### Scenario: Specification artifacts are machine-validated
- **WHEN** the quality gate runs
- **THEN** `openspec validate --all --strict` is executed
- **AND** the gate fails if any change or spec is invalid

#### Scenario: Behaviour agreed in conversation is written to the spec
- **WHEN** a behavioural decision is reached while discussing an active change
- **THEN** the decision is recorded in that change's artifacts before implementation continues

### Requirement: Feature Branch Isolation

The system SHALL require that all implementation work occurs on a dedicated branch named
`{type}/{slug}`, and SHALL prevent commits and pushes that would place work directly on the
default branch.

#### Scenario: A branch is created before implementation
- **WHEN** implementation of a classified change begins
- **THEN** a branch matching the project naming convention exists and is checked out
- **AND** the branch was created before the first implementation commit

#### Scenario: A push to the default branch is blocked
- **GIVEN** the current branch is `main`
- **WHEN** a `git push` targeting `main` is attempted
- **THEN** the operation is blocked deterministically before it runs
- **AND** the reason is reported to the operator

#### Scenario: A force push is blocked
- **WHEN** a `git push` carrying `--force` or `-f` is attempted against any branch
- **THEN** the operation is blocked deterministically before it runs

### Requirement: Single Automated Definition of Done

The system SHALL provide one command that executes every mandatory gate in order —
formatting, linting, type checking, tests, coverage floor, security scan, secret scan and
specification validation — and SHALL report a change as complete only when that command
succeeds.

#### Scenario: The gate runs every mandatory check
- **WHEN** the quality command is invoked
- **THEN** formatting, linting, type checking, tests, coverage, security scanning, secret
  scanning and OpenSpec validation each execute
- **AND** the command exits non-zero if any of them fails

#### Scenario: A failing gate blocks completion
- **WHEN** any mandatory gate fails
- **THEN** the change is not reported as done
- **AND** the failure is diagnosed and fixed rather than suppressed

#### Scenario: The secret scan runs at two breadths
- **WHEN** the secret scan runs over the tracked files
- **THEN** issued key material — a private key block, a forge token, an AWS
  access key id — is matched case-insensitively in every file, Markdown and
  `openspec/` artifacts included, since those are the largest agent-written
  surface and a pasted token lands there
- **AND** credential assignments and connection strings carrying an inline
  password are matched in source, where prose that legitimately describes an
  assignment is exempt
- **AND** a tracked `.env` file fails the scan whatever it contains
- **AND** a placeholder, a fixture and a local development credential pointing
  at the container database do not fail it, because a scanner that cries wolf
  is one people learn to ignore

#### Scenario: Gate prerequisites are established automatically
- **GIVEN** the test database is not running
- **WHEN** the quality command is invoked
- **THEN** the command starts the database and creates the test schema before running tests
- **AND** it does not require manual setup steps

### Requirement: Coverage Floor

The system SHALL enforce a minimum global test coverage of 95 percent as a build-failing
threshold, and SHALL NOT satisfy that threshold by lowering it or by deleting tests.

#### Scenario: Coverage below the floor fails the build
- **WHEN** the test suite finishes with total coverage below 95 percent
- **THEN** the test command exits non-zero
- **AND** the quality gate fails

#### Scenario: The threshold is enforced by configuration, not by convention
- **WHEN** the test suite is invoked through a project entry point — the
  `make` test targets, the quality gate or CI
- **THEN** the 95 percent floor is applied from project configuration
- **AND** no entry point passes a flag that lowers or disables it

#### Scenario: An ad-hoc single-test run is not measured against the floor
- **GIVEN** a single test is invoked directly with pytest during an edit loop
- **WHEN** that invocation finishes
- **THEN** coverage is not measured and the floor is not applied, so the run
  reports the test's own result rather than a coverage failure
- **AND** the change is still not reportable as done until the gate, which
  does apply the floor, passes

### Requirement: Deterministic Protection Of Dangerous Operations

The system SHALL block irreversible or out-of-scope operations before they
execute, using deterministic checks rather than model judgement, covering at
minimum destructive git operations, privilege escalation, recursive deletion
outside the repository, tree-walking search rooted outside it, writes into the
repository's own git directory, and access to credential material.

Those checks SHALL decide by where a path resolves, not by how it is spelled:
a target is unquoted, `${VAR}`-normalised, expanded, resolved and then
compared against the repository root. Quoting, git global options and trailing
comments SHALL NOT change a verdict.

#### Scenario: A destructive history rewrite is blocked
- **WHEN** `git reset --hard` or a comparable destructive history operation is
  attempted
- **THEN** the command is blocked before execution

#### Scenario: Privilege escalation is blocked
- **WHEN** a command invoking `sudo` or `doas` is attempted, including behind
  environment assignments (`FOO=bar sudo …`) or a wrapper (`xargs sudo …`)
- **THEN** the command is blocked before execution
- **AND** the same word appearing inside prose or a search pattern is not
  treated as an invocation

#### Scenario: Recursive deletion is judged by where the target resolves
- **WHEN** a recursive deletion targets a path outside the repository, however
  it is spelled — `"$HOME"`, `${HOME}`, `"/etc"`, `..`, `../*`, or the
  repository itself reached from its parent as in `cd .. && rm -rf
  <repository>`
- **THEN** the command is blocked before execution
- **AND** recursive deletion of a path that resolves inside the repository is
  permitted, since that is ordinary work

#### Scenario: A deletion target only the shell can resolve is refused
- **GIVEN** the value of a deletion target is not knowable before the shell
  runs it
- **WHEN** the deletion is attempted
- **THEN** it is refused rather than guessed at

#### Scenario: Search rooted outside the repository is blocked
- **WHEN** a tree-walking tool — `find`, `grep`, `rg`, `ag`, `ack` or `fd` —
  is rooted at a path outside the repository, with or without `-exec` or
  `-delete`, through an executable path, or through a mode with no pattern
  such as `rg --files`
- **THEN** the command is blocked before execution
- **AND** the block holds even though those tools are in the permission
  allowlist, since a search rooted at `$HOME` is a credential read with extra
  steps
- **AND** `find -files0-from` is refused because its roots cannot be known
  without reading another file before the command runs

#### Scenario: A search pattern is not treated as a search root
- **WHEN** a tree-walking search has a pattern that resembles an outside path,
  such as `grep -n "/etc/passwd" README.md`, `rg "~" docs/` or
  `grep -r "foo /etc" docs/`, while every positional search root resolves
  inside the repository
- **THEN** the command is permitted
- **AND** the guard identifies search roots according to the invoked tool's
  argument grammar and shell quoting rather than treating every non-option
  argument as a path

#### Scenario: Writing outside the repository is blocked
- **WHEN** a file write targets a path outside the repository working
  directory
- **THEN** the write is blocked before it occurs

#### Scenario: Writing inside the git directory is blocked
- **WHEN** a write targets a path inside `.git/`
- **THEN** the write is blocked before it occurs
- **AND** the reason given is that git configuration and hooks execute
  commands, so they are machine configuration rather than project source

#### Scenario: Reading private credentials is blocked
- **WHEN** a command or file read targets a path that resolves inside a
  credential directory — `~/.ssh`, `~/.aws`, `~/.gnupg`, `~/.kube`,
  `~/.docker`, `~/.claude`, `~/.config/gcloud`, `~/.config/gh`,
  `~/.config/git`, `~/.local/share/keyrings` — or a known credential file, or
  a real environment file
- **THEN** the operation is blocked before it occurs
- **AND** the spelling of the path does not change the verdict: `~/.aws`,
  `$HOME/.aws`, `${HOME}/.aws`, the quoted form and the absolute form are one
  rule
- **AND** a stored forge token is treated as credential material in its own
  right, because reading it would let an agent publish through the API and
  walk past the human acceptance gate that `gh pr *` sits behind

#### Scenario: Quoting does not bypass a rule
- **WHEN** a command hides a blocked operation behind quotes, a git global
  option or a trailing comment — `gh pr 'merge' 1`, `git -c user.name=x push
  origin main`, `pip install requests # uses .venv`
- **THEN** the rules are evaluated against a view of the command with quotes
  removed, git global options folded away and trailing comments stripped
- **AND** the verdict is the same as for the unadorned form

#### Scenario: A command that switches branch is judged on where it lands
- **GIVEN** a command changes branch before committing or pushing, as in `git
  switch main && git commit -m x`
- **WHEN** the guard evaluates it
- **THEN** the verdict is taken from the branch the work would land on, not
  the branch checked out when the command was submitted

#### Scenario: Safe example files remain accessible
- **GIVEN** a file is a template or fixture rather than real credential
  material
- **WHEN** `.env.example` or another template suffix is read or written, or
  the documented first setup step copies that template to `.env`
- **THEN** the operation is permitted
- **AND** a real environment file is still recognised by shape rather than by
  an enumerated list, so `.env.dev` and `.env.secret` are blocked

#### Scenario: An unreadable payload leaves the operator's work alone
- **GIVEN** the guard receives a payload it cannot parse, or a path that
  cannot be resolved
- **WHEN** it decides
- **THEN** it permits the operation deliberately and reports the reason on
  standard error
- **AND** it does not exit on an unhandled traceback, which would disable the
  boundary while looking like an ordinary permit

#### Scenario: The guards run without the project virtualenv
- **GIVEN** a fresh clone on which `make install` has not yet run
- **WHEN** a guarded tool call is made
- **THEN** the guard executes, because the hook invokes the system interpreter
  rather than the virtualenv one
- **AND** the boundary is never silently inert

### Requirement: Independent Verification

The system SHALL require that the final verification of a change is performed by an agent
whose context differs from the agent that implemented it, and that verification SHALL compare
the specification against the implementation rather than restating the implementer's claims.

#### Scenario: The implementer does not self-approve
- **WHEN** implementation of a STANDARD or higher change completes
- **THEN** verification is delegated to a separate agent
- **AND** that agent receives the specification, the diff, the test results and the gate output

#### Scenario: Unimplemented requirements are detected
- **GIVEN** a requirement in the change's delta spec has no corresponding implementation
- **WHEN** verification runs
- **THEN** the verifier reports the requirement as unmet
- **AND** the change is not reported as ready

#### Scenario: Out-of-scope changes are detected
- **WHEN** the diff contains changes not traceable to any requirement in the change
- **THEN** the verifier reports them as out of scope

### Requirement: Requirement To Test Traceability

The system SHALL maintain a traceable path from each requirement through its scenarios to the
tests that verify it and the code that implements it, and verification SHALL report any
requirement lacking a corresponding test.

#### Scenario: Each requirement maps to at least one test
- **WHEN** verification runs for a change
- **THEN** every requirement in the change's delta specs is mapped to at least one test
- **AND** requirements without a test are reported

#### Scenario: The mapping is reported explicitly
- **WHEN** the final compliance report is produced
- **THEN** it states how many requirements and scenarios were implemented and covered

### Requirement: Human Acceptance Gate

The system SHALL complete investigation, specification, implementation, correction,
documentation, verification and local commits autonomously, and SHALL NOT create or push a
pull request, nor merge, until a human has explicitly accepted the change.

#### Scenario: Work proceeds without interruption for recoverable failures
- **WHEN** a gate fails for a reason the agent can diagnose and fix
- **THEN** the agent corrects it and re-runs the gate without asking for intervention

#### Scenario: A compliance report precedes the request for acceptance
- **WHEN** all mandatory gates pass
- **THEN** a final compliance report is presented stating gate results, coverage, trade-offs,
  known limitations and remaining risks
- **AND** the agent waits for explicit human acceptance

#### Scenario: A pull request is not opened before acceptance
- **GIVEN** the human has not yet accepted the change
- **WHEN** the change is otherwise complete
- **THEN** no pull request is created and nothing is pushed to the remote

#### Scenario: Merging is never automatic
- **WHEN** a pull request exists
- **THEN** the agent does not merge it under any circumstance

### Requirement: Session Workflow Context

The system SHALL report the workflow state at the start of every session — the
checked-out branch, whether that branch is protected, the number of
uncommitted files, and every open OpenSpec change with its completed and total
task counts — and that report SHALL read state only, running no gate, starting
no container and making no network call.

#### Scenario: A session begins with the workflow state stated
- **WHEN** a session starts
- **THEN** the branch, the uncommitted-file count and each open OpenSpec
  change with its task progress are reported before the first action is taken
- **AND** the report restates that the definition of done is the quality gate
  and that no pull request is opened before human acceptance

#### Scenario: Starting on the default branch is flagged
- **GIVEN** the checked-out branch is `main` or `master`
- **WHEN** a session starts
- **THEN** the report marks the branch as protected
- **AND** it states that a feature branch is created before any implementation

#### Scenario: The absence of open changes is stated explicitly
- **GIVEN** `openspec/changes/` contains no change directory other than
  `archive`
- **WHEN** a session starts
- **THEN** the report states that there are no active changes
- **AND** the absence is reported rather than left as silence, which is
  indistinguishable from the report having failed

#### Scenario: The report reads state and nothing else
- **WHEN** the session-start report runs
- **THEN** it executes no quality gate, starts no container and makes no
  network call
- **AND** it does not modify the working tree

#### Scenario: A failure to report does not block the session
- **GIVEN** a command the report depends on is unavailable or returns an error
- **WHEN** a session starts
- **THEN** the report exits without failing the session
- **AND** the session proceeds

### Requirement: Cost-Proportional Model Routing

The system SHALL route work to the least capable mechanism sufficient for it, preferring
deterministic tooling over a language model, and SHALL reserve the most capable model for
architecture, security, cross-cutting change and final verification.

#### Scenario: A verifiable fact is answered by tooling, not a model
- **WHEN** a question can be decided by ruff, mypy, pytest, coverage or git
- **THEN** that tool decides it
- **AND** no model is invoked to restate the result

#### Scenario: Mechanical review runs on the cheapest model
- **WHEN** review concerns formatting, naming, docstring presence or other mechanical checks
- **THEN** it is routed to the cheapest configured model

#### Scenario: Security and architecture run on the most capable model
- **WHEN** work concerns security surface, architectural decisions or final specification
  verification
- **THEN** it is routed to the most capable configured model

#### Scenario: A failed attempt escalates rather than repeats
- **GIVEN** an attempt at a task has failed
- **WHEN** the task is retried
- **THEN** the retry uses information obtained from the failed attempt
- **AND** repeated failure escalates to a more capable model rather than looping unchanged

### Requirement: Cross-LLM Skill Compatibility

The system SHALL version the shared project skills for both Codex under
`.agents/skills/` and Claude Code under `.claude/skills/`, and SHALL detect an
unrecorded divergence between their common files. It SHALL version the seven
agent profiles and guard wiring needed by each runtime.

#### Scenario: Both coding agents receive the shared workflow
- **WHEN** a developer clones the repository for either Codex or Claude Code
- **THEN** that agent finds the project's shared skills in its native skill
  root without relying on personal machine configuration

#### Scenario: Intentional differences are bounded and documented
- **WHEN** the compatibility test compares both skill roots
- **THEN** common files are byte-identical except the native constitution
  pointer in `spec-driven-workflow/SKILL.md`
- **AND** Codex-only `source-command-opsx-*` wrappers are the only files that
  exist exclusively under `.agents/skills/`

#### Scenario: Both runtimes carry their agent configuration
- **WHEN** the compatibility test inspects the versioned configuration
- **THEN** Codex has its `hooks.json` and the same seven role names under
  `.codex/agents/` that Claude Code has under `.claude/agents/`
- **AND** no agent requires personal machine configuration to find the
  workflow's specialised review roles
- **AND** Codex hook commands are resolved from the repository root rather
  than through Claude Code environment variables
