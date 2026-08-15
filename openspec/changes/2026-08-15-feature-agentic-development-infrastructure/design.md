## Context

The application itself is in good shape: 2,388 lines across `app/` and `tests/`, a clean
layered architecture (routers → services → models), SQLAlchemy 2.0 typed mappings, consistent
per-user data isolation, and 81 behavioural tests. What is missing is not code quality but
*enforcement* of code quality, and any structure that lets an agent work autonomously without
that autonomy becoming dangerous.

Four environment facts constrain the design and were verified rather than assumed:

1. **Claude Code 2.1.233** supports `permissions.allow/ask/deny`, `defaultMode`, a documented
   hook event set (`PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`, …), `.claude/agents/`
   definitions with per-agent model selection, and `skillOverrides` for controlling which
   skills reach the model's listing.
2. **OpenSpec 1.8.0** owns the `openspec/changes/<name>/` layout and generates both
   `.claude/commands/opsx/*` and `.claude/skills/openspec-*/` itself. Anything this change
   writes into those paths would be overwritten by `openspec update`.
3. **The test suite is not hermetic.** It requires PostgreSQL reachable on `localhost:5433`,
   which the project's own `docker-compose.yml` publishes, plus a `pocketledger_test`
   database that the compose file does not create.
4. **OpenTelemetry export dominates test runtime.** With `OTEL_ENABLED` at its default of
   true and no Jaeger collector listening, the suite takes roughly four minutes and floods
   output with 32-second retry backoffs. With export disabled it takes 43 seconds.

## Goals / Non-Goals

**Goals:**

- One command that constitutes the definition of done, usable identically by a human, by an
  agent and by CI.
- Guarantees that hold without model cooperation: branch discipline, destructive-operation
  blocking, and a repository write boundary.
- Enough context isolation and model routing that a feature request can traverse the whole
  lifecycle without a human in the loop until the acceptance gate.
- A minimal component set. Every skill, agent, hook and script must increase autonomy,
  predictability, safety or traceability; anything that increases none of them is not built.

**Non-Goals:**

- Fixing the pre-existing lint, typing and test failures this infrastructure exposes. That is
  a separate change, kept separate so the two concerns stay independently traceable.
- Enabling an operating-system sandbox in this change.
- Rewriting the application's architecture, or the README, which is already accurate and
  thorough.
- Making the test suite hermetic by moving it off PostgreSQL. The suite deliberately tests
  against the real engine, and swapping it for SQLite would weaken it.

## Decisions

### Decision: the constitution lives at `CLAUDE.md`, not `.claude/claude.md`

**Context.** The existing file is lowercase. On this case-sensitive Linux filesystem it is
very likely never loaded as project memory, which means the project's rules have been
decorative. It is also written as a tutorial — 300 lines of quick-starts, worked examples and
troubleshooting — rather than as a set of rules.

**Alternatives considered.** Renaming in place to `.claude/CLAUDE.md` would preserve the
project's stated convention of keeping Markdown out of the repository root. Keeping both files
would guarantee drift between them.

**Trade-off.** The root location contradicts the project's "no Markdown in the root except
README" rule. That rule exists to keep *documentation* organised, and `CLAUDE.md` is
configuration rather than documentation — the same category as `pyproject.toml` or
`Makefile`, which already sit in the root. The root path is also the canonical, unambiguous
location that every Claude Code version discovers.

**Consequence.** `CLAUDE.md` holds only permanent, universal rules. Tutorial content moves to
skills, which load on demand and therefore cost no context when unused.

### Decision: deterministic guards as the security boundary, not an OS sandbox

**Context.** The requested "LLM jail" wants broad freedom inside the repository and strong
restriction outside it. Claude Code offers two mechanisms: permission rules with hooks, and an
operating-system sandbox built on bubblewrap.

**Alternatives considered.** Enabling `sandbox.enabled` would give kernel-level enforcement.
But `bwrap` is present while `socat` — required by the Linux sandbox network proxy — is not,
and the test suite must reach PostgreSQL on a locally published port. Enabling it blind risks
breaking every test run, which would make the gate unusable and the autonomy worthless.

**Trade-off.** Hooks are enforced by Claude Code rather than by the kernel, so they bind the
agent but not a human typing directly into a terminal. That is an acceptable boundary for the
threat being addressed, which is an autonomous agent taking an irreversible action, not a
malicious local operator.

**Consequence.** The jail is built from `permissions.deny` plus two `PreToolUse` guard
scripts. The sandbox configuration is written down in the documentation as an opt-in step
with its prerequisites stated, to be enabled once it can be validated against the test suite.

### Decision: ruff is the single linting authority

**Context.** The repository configures ruff, flake8 and pydocstyle simultaneously, with
overlapping and partly contradictory rules, and flake8 duplicates checks ruff already
performs faster.

**Trade-off.** Retiring flake8 loses `mccabe` complexity checking as configured. Ruff's `C901`
rule provides the equivalent and is enabled in its place.

**Consequence.** `.flake8` is deleted; the complexity threshold moves into `pyproject.toml`.
One tool, one configuration file, one source of truth.

### Decision: the quality gate establishes its own prerequisites

**Context.** A gate that fails because the developer forgot to start a container is a gate
that gets bypassed. The audit's very first test run produced 81 errors for exactly that
reason.

**Trade-off.** The gate now has a side effect: it starts a Docker container and may create a
database. This makes it slower on a cold start and couples it to Docker. The alternative —
failing with an instruction to run something first — reintroduces the manual step that the
autonomy requirement is trying to remove.

**Consequence.** `scripts/dev-db.sh` is idempotent: it starts the `db` service only if it is
not already healthy, and creates `pocketledger_test` only if it does not exist. It never drops
or truncates anything. The gate also sets `OTEL_ENABLED=false`, turning a four-minute noisy
run into a 43-second quiet one.

### Decision: seven agents, each justified by isolation or specialisation

A separate agent is warranted only when it either protects the orchestrator's context from
bulk output, or brings a genuinely different evaluation criterion. Each of the seven meets one
of those tests: `spec-architect` and `feature-implementer` produce and consume large context;
`test-engineer`, `quality-reviewer`, `security-reviewer` and `documentation-reviewer` apply
distinct criteria; `spec-verifier` exists specifically so that the agent which implemented a
change is never the only agent that approves it.

Model assignment follows cost proportionality: the cheapest model for mechanical inspection
(`quality-reviewer`, `documentation-reviewer`), the middle model for intermediate judgement
(`test-engineer`), and the most capable for architecture, security and final verification
(`spec-architect`, `feature-implementer`, `security-reviewer`, `spec-verifier`). Stable
aliases are used rather than pinned version identifiers so the routing survives model
releases.

### Decision: three enforcement layers with distinct jurisdictions

The layers are not redundant because each covers a case the others cannot:

| Layer | Binds | Covers what the others cannot |
|---|---|---|
| Claude Code hooks | the agent, at tool-call time | stops a destructive action *before* it happens |
| pre-commit | any committer, at commit time | holds when Claude is not involved at all |
| CI | the remote, at merge time | holds when local hooks are bypassed or disabled |

To avoid paying for the same check three times, each layer runs the cheapest thing that is
meaningful at its point in time: hooks format only the single file just edited; pre-commit
runs fast per-file checks and secret detection; the full suite with coverage runs only in the
gate and in CI.

### Decision: OpenSpec-generated files are silenced, not deleted

`.claude/skills/openspec-*/` and `.claude/commands/opsx/` are byte-equivalent duplicates of
one another, and both carry `generatedBy: "1.8.0"`. Deleting either would be undone by the
next `openspec update`, and the deletion would look like an unexplained regression. Instead
`skillOverrides` marks the six `openspec-*` skills `user-invocable-only`, which removes them
from the model's skill listing — halving the OpenSpec context cost — while leaving both the
files and the `/openspec-*` slash commands intact.

## Risks / Trade-offs

**The gate will fail on first run, by design.** The infrastructure exposes 34 ruff
violations, 7 mypy errors and one failing test that already existed. Because debt repayment is
deliberately a separate change, this change's own compliance report will show lint and typing
as failing, annotated as pre-existing and out of scope. The alternative — bundling the fixes —
was rejected because it would make the two concerns indistinguishable in the history.

**Coverage has no margin.** The measured baseline is exactly 95.00% against a floor of 95%.
Any untested line added will fail the build immediately. This is uncomfortable but correct: it
is a real signal, and padding the floor downward to create slack would defeat its purpose.

**The gate depends on Docker.** If Docker is unavailable, the gate cannot run tests at all.
It fails with an explicit diagnostic rather than silently skipping them, because a gate that
silently skips its most important check is worse than one that stops.

**Hooks add latency to every edit.** The `PostToolUse` formatter runs on each Python file
written. It is scoped to the single edited file and to ruff alone, which keeps it in the tens
of milliseconds; running tests there instead would make editing unusable.

**`gh` reports version 0.0.4**, which is not a GitHub CLI version number. Pull-request
creation may therefore not work through it. Since PR creation happens only after explicit
human acceptance, this is verified at that point rather than assumed now.
