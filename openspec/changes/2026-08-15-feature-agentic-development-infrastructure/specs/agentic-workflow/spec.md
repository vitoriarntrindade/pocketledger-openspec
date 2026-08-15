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
- **WHEN** the test suite is invoked through any entry point, including CI
- **THEN** the 95 percent floor is applied from project configuration

### Requirement: Deterministic Protection Of Dangerous Operations

The system SHALL block irreversible or out-of-scope operations before they execute, using
deterministic checks rather than model judgement, covering at minimum destructive git
operations, privilege escalation, recursive deletion outside the repository, and access to
credential material.

#### Scenario: A destructive history rewrite is blocked
- **WHEN** `git reset --hard` or a comparable destructive history operation is attempted
- **THEN** the command is blocked before execution

#### Scenario: Privilege escalation is blocked
- **WHEN** a command invoking `sudo` is attempted
- **THEN** the command is blocked before execution

#### Scenario: Writing outside the repository is blocked
- **WHEN** a file write targets a path outside the repository working directory
- **THEN** the write is blocked before it occurs

#### Scenario: Reading private credentials is blocked
- **WHEN** a command or file read targets SSH keys, cloud credentials, or a real environment file
- **THEN** the operation is blocked before it occurs

#### Scenario: Safe example files remain accessible
- **GIVEN** a file is an example or fixture rather than real credential material
- **WHEN** `.env.example` is read or written
- **THEN** the operation is permitted

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
