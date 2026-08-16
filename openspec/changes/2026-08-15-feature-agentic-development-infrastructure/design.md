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

### Decision: constitutions live at `AGENTS.md` and `CLAUDE.md`

**Context.** The existing Claude Code file is lowercase. On this
case-sensitive Linux filesystem it is very likely never loaded as project
memory, which means the project's rules have been decorative. The repository
is also used by Codex, which reads `AGENTS.md` rather than `CLAUDE.md`. The
old file is written as a tutorial — 300 lines of quick-starts, worked examples
and troubleshooting — rather than as a set of rules.

**Alternatives considered.** Renaming in place to `.claude/CLAUDE.md` would
preserve the project's stated convention of keeping Markdown out of the
repository root. Keeping a Claude-only constitution would leave Codex without
the permanent rules; keeping two undocumented constitutions would guarantee
drift between them.

**Trade-off.** The root location contradicts the project's "no Markdown in the root except
README" rule. That rule exists to keep *documentation* organised, and `CLAUDE.md` is
configuration rather than documentation — the same category as `pyproject.toml` or
`Makefile`, which already sit in the root. The root path is also the canonical, unambiguous
location that every Claude Code version discovers.

**Consequence.** `AGENTS.md` and `CLAUDE.md` hold the permanent, universal
rules for Codex and Claude Code. Tutorial content moves to skills, which load
on demand and therefore cost no context when unused. Their coexistence and
the bounded differences between the agent skill roots are tested explicitly.

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

**The limits, named.** "A boundary for an agent doing ordinary work, not a
sandbox against an adversary" is only an honest claim if the gaps are stated
rather than implied. Three are known and accepted:

- a path assembled at runtime (`K=~/.ssh/id_rsa; cat $K`) — the guard sees a
  variable, and the value exists only once the shell runs;
- a path built inside an interpreter's own source (`python -c '…expanduser…'`)
  — the guard would have to parse another language to find it;
- `pkexec`, which is not in the privilege-escalation rule set.

Each is defeated only by writing the command in a way nobody writes it by
accident. The failures worth engineering against are the ones careful work
actually produces — quoting a path variable, searching from `$HOME`, deleting
through `..` — and those are the ones the containment rewrite closes.

### Decision: containment, not pattern-matching, decides a path

**Context.** The first guards matched the text of a command. A deletion was
dangerous if its target *began* with `/`, `~` or `$HOME`; a credential path
was a credential path if it matched one of a list of regular expressions. A
security review of the layer found that this failed on the ordinary case
rather than the exotic one: `rm -rf "$HOME"` is quoted because quoting a path
variable is good shell hygiene, and the quote is exactly what made the token
stop beginning with `$`. The same held for `${HOME}`, `"/etc"`, `..` and
`../*`, and for deleting the repository from its own parent after a `cd ..`.

**Alternatives considered.** Extending the pattern list to cover each observed
spelling is what produced the defect in the first place: every fix is one
spelling behind, and the list grows without ever being complete. It is also
unfalsifiable — nothing tells you which spelling is missing.

**Consequence.** Targets are unquoted, `${VAR}`-normalised, expanded, resolved
and compared against the repository root, so the verdict follows from where a
path *is* rather than how it was written. The credential inventory moved the
same way, from regular expressions to containment over `~/.ssh`, `~/.aws`,
`~/.gnupg`, `~/.kube`, `~/.docker`, `~/.claude`, `~/.config/gcloud`,
`~/.config/gh`, `~/.config/git` and `~/.local/share/keyrings`. The `gh` entry
earns its place beyond its own contents: a readable OAuth token lets an agent
publish through the API and walk past the human acceptance gate that `gh pr *`
sits behind.

**Trade-off.** Resolution costs a filesystem call per candidate token and can
raise on a pathological path. Both are handled — the guards permit and report
on standard error rather than exiting on a traceback — but it is more
machinery than a regular expression, and that machinery is now load-bearing.

### Decision: search containment follows each tool's argument grammar

**Context.** The first containment rewrite treated every non-option argument
to `find`, `grep`, `rg`, `ag`, `ack` and `fd` as a search root. That preserved
the intended refusal of `grep -r AWS ~`, but made ordinary patterns such as
`grep -n "/etc/passwd" README.md` and `rg "~" docs/` look like paths outside
the repository. A guard that blocks routine inspection because a pattern
resembles a path creates friction without improving the boundary.

**Alternatives considered.** Permitting every quoted token would recreate the
quoted-interpreter bypass already repaired by the guard. Maintaining an
exception list for path-shaped patterns would keep the same textual heuristic
that containment was introduced to replace.

**Consequence.** Search roots are parsed by the command's positional grammar:
`grep`-family tools treat the pattern as distinct from subsequent roots,
`find` accepts roots only before its predicates, and `fd` treats its first
positional argument as its pattern. Only those roots are resolved and compared
with the repository boundary. The guard remains conservative when a grammar
cannot be determined, but a query string by itself is never a root. The parser
uses shell tokens rather than whitespace splitting, so a quoted pattern with a
space remains one argument. Modes with no pattern, such as `rg --files`, treat
every positional argument as a root; `find -files0-from` is refused because
the file may name roots the guard cannot inspect before execution.

### Decision: the boundary does not protect itself

**Context.** `scripts/guard-bash.py`, `scripts/guard-write.py`,
`.claude/settings.json` and `.pre-commit-config.yaml` are the boundary.
Nothing stops an agent editing them, which looks at first like the obvious
hole to close.

**Alternatives considered.** Adding them to the write guard's deny list would
be one line. It would also block the work happening in this very change: the
guards are ordinary source, under active review and repair, and every fix to
them is an edit to a protected file. It would stop nobody determined either —
an agent that intends to disarm the boundary can decline to call the tool the
guard is attached to, or edit the file with a shell redirect, so the
protection would be an obstacle to honest work and a speed bump to dishonest
work.

**Trade-off, stated plainly.** The boundary is only as durable as review and
git history make it. That is weaker than a self-protecting configuration would
be in principle, and equal to it in practice, because the mechanism that would
enforce it is the mechanism being edited.

**Consequence.** Guard scripts and hook configuration stay editable. `.git/**`
is protected instead, on a different ground: git configuration and hook
scripts execute commands, so they are machine configuration rather than
project source, and no legitimate task in this repository writes there.

### Decision: ruff is the single linting authority

**Context.** The repository configures ruff, flake8 and pydocstyle simultaneously, with
overlapping and partly contradictory rules, and flake8 duplicates checks ruff already
performs faster.

**Trade-off.** Retiring flake8 loses `mccabe` complexity checking as configured. Ruff's `C901`
rule provides the equivalent and is enabled in its place.

**Consequence.** `.flake8` is deleted; the complexity threshold moves into `pyproject.toml`.
One tool, one configuration file, one source of truth.

### Decision: the guard tests are exempted from two subprocess lint rules

**Context.** Proving the guards end to end means running them as real
processes, which is the only way to exercise the payload parsing, the exit
code and the JSON the hook actually emits. Ruff's `S603` and `S607` fire on
any `subprocess.run` whose argv is not a literal, and these calls cannot be
literal: the script paths are built from a pytest temporary directory and
`git` is resolved from `PATH`.

**Alternatives considered.** A `# noqa` at each call site is forbidden by the
constitution, and rightly — it hides the exemption at the point where it is
easiest to copy. Dropping the subprocess tests would leave `main()` in both
guards unexecuted, which is the defect this repair exists to close.

**Consequence, stated as the relaxation it is.** `S603` and `S607` are added
to the existing `tests/*` per-file ignores, next to the identical exemption
already granted to `scripts/*`. The constitution requires a relaxed gate to
carry its justification in the change that relaxes it, and this is that
justification. The scope is narrow — test files only, where the inputs are
literals written in this repository rather than user data — and the guard
tests themselves are written lint-clean, so nothing depends on the exemption
that could be written without it.

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

### Decision: version shared skills for Codex and Claude Code

**Context.** The repository is worked by both Codex and Claude Code. Codex
loads skills from `.agents/skills/`, whereas Claude Code loads them from
`.claude/skills/`. Keeping only one root would leave one agent without the
project workflow; silently maintaining two copies would make each correction
an opportunity for drift.

**Alternatives considered.** A symlink would avoid duplicate files locally,
but it is less portable across archive, checkout and Windows workflows. A
single root with tool-specific global configuration would make a fresh clone
depend on personal machine setup rather than repository state.

**Consequence.** Both roots are versioned. Common files are byte-identical;
the test allows only two documented differences: the native constitution
pointer in `spec-driven-workflow/SKILL.md`, and Codex-only
`source-command-opsx-*` compatibility wrappers. Any new divergence must be
written into the artifacts and the test before it is accepted.

Codex's seven agent profiles and hook configuration are versioned under
`.codex/`; Claude Code's equivalents remain under `.claude/agents/` and
`.claude/settings.json`. The test checks that both agent roots expose the same
role names and that Codex has its hook configuration, so the dual-runtime
promise holds after a clone rather than only on the machine that configured it.

### Decision: three enforcement layers with distinct jurisdictions

The layers are not redundant because each covers a case the others cannot:

| Layer | Binds | Covers what the others cannot |
|---|---|---|
| Claude Code hooks | the agent, at tool-call time | stops a destructive action *before* it happens |
| pre-commit | any committer, at commit time | holds when Claude is not involved at all |
| CI | the remote, at merge time | holds when local hooks are bypassed or disabled |

To avoid paying for the same check three times, each layer runs the cheapest thing that is
meaningful at its point in time: hooks format only the single file just edited; pre-commit
blocks only what cannot be undone once a commit lands; the full suite with coverage runs only
in the gate and in CI.

**Consequence for an existing specification.** The `code-structure` capability
already carried a requirement stating that pre-commit runs ruff, flake8 and
mypy and blocks the commit when they fail. Removing those hooks makes that
requirement false, so it is modified in this change's delta rather than left
standing: a current spec that describes enforcement the repository does not
perform is worse than no spec, because it is trusted.

**Alternative considered.** Keeping lint, format and type hooks in pre-commit
would have left the requirement true without any spec work. It was rejected
because those three checks already run on every edited file, again in the gate
and again in CI: a fourth copy adds seconds to every commit and buys nothing,
and the predictable response to a slow commit hook is `--no-verify`, which
disables the private-key and `.env` protections that only this layer provides.
The cost of the delta is one modified requirement; the cost of the alternative
is an enforcement layer people learn to switch off.

### Decision: the coverage floor binds entry points, not every run

**Context.** The requirement says the 95% floor applies when the suite is
invoked "through any entry point, including CI". The floor lives in
`[tool.coverage.report] fail_under`, which only takes effect when coverage
actually runs — and coverage runs only when `--cov` is passed. The obvious way
to make that unconditional is to put the coverage flags in pytest `addopts`,
so every invocation measures coverage. That was not done, and the reasoning
existed only as a comment in `pyproject.toml`, where no requirement and no
reviewer could see it.

**Alternatives considered.** Putting `--cov=app --cov-report=term-missing` in
`addopts` makes the floor genuinely unconditional. It also means `pytest
tests/test_auth.py::test_login` measures coverage of the whole application
from a single test, reports something around 20%, and exits non-zero — a red
failure that says nothing about the test just run. The predictable adaptation
is `-p no:cacheprovider`-style workarounds, or `--no-cov`, or simply
distrusting the exit code, and a floor that is routinely overridden stops
being a floor.

**What the distinction actually is.** An *entry point* is a way the project
offers to run its suite: `make test`, `make test-cov`, `make quality` and the
CI workflow. Each of those passes the coverage flags and therefore applies the
floor. A bare `pytest …` typed during an edit loop is not an entry point; it
is a debugging tool, and it is deliberately unmeasured.

**Trade-off.** The guarantee is weaker than "any invocation of pytest anywhere
enforces 95%". It is exactly as strong as it needs to be, because no route by
which work is declared done — the gate, and CI — can skip it. The residual
risk is someone running bare `pytest`, seeing green, and believing the change
is finished; the constitution's definition of done answers that by naming
`make quality`, not `pytest`, as the thing that decides.

**Consequence.** `make test` passes the coverage flags so that the floor
applies there too, rather than being the one project-provided entry point that
silently does not enforce it. Coverage flags stay out of `addopts`. The
requirement's scenario is worded in terms of entry points, and this decision
is what "entry point" means.

### Decision: the session-context hook is specified, not informal

**Context.** `scripts/session-context.sh` is registered as a `SessionStart`
hook and prints the branch, the uncommitted-file count, the open OpenSpec
changes with their task progress, and a restatement of the definition of done.
It was built while implementing this change and initially appeared in no
requirement and no task — which is the failure mode this change exists to
remove, present in the change itself.

**Alternatives considered.** Leaving it unspecified, as ergonomic tooling on
the same footing as a shell alias, was considered and rejected on two grounds.
It is registered in `.claude/settings.json`, so it executes in every session
whether or not anyone remembers it exists; and its output is the first thing a
session reads, so if it silently breaks or drifts — reporting no active change
when one is open, or the wrong branch — the agent begins work from a false
premise. A component that runs unconditionally and shapes what the agent
believes is not convenience tooling. Deleting it was also considered: it is 63
lines that read state and make no network call, and rediscovering the same
facts through conversation costs more than it does.

**Trade-off.** Specifying it means the requirement must be verifiable without
asserting on exact prose, since the wording of the summary will change. The
requirement is therefore stated in terms of the facts reported and the
constraint that the hook only reads state — never runs a gate, starts a
container or makes a network call — which is both testable and the property
that actually matters.

**Consequence.** A `Session Workflow Context` requirement is added to the
`agentic-workflow` delta spec, with a task to cover it by a smoke test and to
add it to the traceability map in `tests/test_agentic_infrastructure.py`.

### Decision: the traceability check reads every delta spec, not one

**Context.** `test_every_requirement_has_a_test` enforces this change's own
traceability requirement by reading `specs/agentic-workflow/spec.md` and
failing when a requirement in it is absent from the test module's map. That
path was hard-coded when the change had exactly one delta spec. Adding the
`code-structure` delta put a requirement *outside* the mechanism built to
guarantee that no requirement escapes a test — the failure the check exists to
catch, occurring in the check itself.

**Alternatives considered.** Adding a second hard-coded path would work until
the third delta spec, and would fail silently rather than loudly when that
happened. Dropping the check for capabilities other than `agentic-workflow`
would make the guarantee depend on which file a requirement happened to land
in.

**Consequence.** The check globs `specs/*/spec.md` under the change directory,
so a new capability is covered the moment its delta exists. The cost is that
adding a requirement now fails the suite until it is mapped and tested, which
is the intended pressure.

### Decision: OpenSpec-generated files are silenced, not deleted

`.claude/skills/openspec-*/` and `.claude/commands/opsx/` are byte-equivalent duplicates of
one another, and both carry `generatedBy: "1.8.0"`. Deleting either would be undone by the
next `openspec update`, and the deletion would look like an unexplained regression. Instead
`skillOverrides` marks the six `openspec-*` skills `user-invocable-only`, which removes them
from the model's skill listing — halving the OpenSpec context cost — while leaving both the
files and the `/openspec-*` slash commands intact.

## Risks / Trade-offs

**The gate failed on first run, by design, and was repaired by a separate
change.** Standing the infrastructure up exposed 38 unformatted files, 14 ruff
violations, 7 mypy errors, one bandit finding and one failing test, all of
them pre-existing and previously unmeasured because none of the tools were
installed. Fixing them here was rejected: bundling the decision to build a
gate with the work of paying down what it found would make the two
indistinguishable in the history. They were fixed instead by
`2026-08-15-refactor-python-quality-baseline`, which is stacked on this branch
and has landed (`30b1b45` formatting, `c5ab5bc` the defects).

That has a consequence for how this change can be evidenced. On this working
tree the gate now passes, so it can no longer demonstrate the failures it was
supposed to expose — the proof that it exposed rather than masked them is
historical, in the follow-up change's own `Why` section, which enumerates each
defect, and in the two commits that fixed them. Reconstructing the original
evidence would mean checking out `5abeeed` and running the gate there. That is
recorded rather than done, because the artifact record already carries the
enumeration and re-running it proves nothing new.

**Coverage has little margin.** The baseline measured 95.00% against a floor
of 95% when this change began. Narrowing the coverage source to `app/` and
adding the infrastructure tests moved it to 96.62%, so there is now roughly a
point and a half of slack — still thin. Any meaningful block of untested code
will fail the build immediately. That is uncomfortable and correct: padding the
floor downward to create room would defeat its purpose.

**The gate depends on Docker.** If Docker is unavailable, the gate cannot run tests at all.
It fails with an explicit diagnostic rather than silently skipping them, because a gate that
silently skips its most important check is worse than one that stops.

**Hooks add latency to every edit.** The `PostToolUse` formatter runs on each Python file
written. It is scoped to the single edited file and to ruff alone, which keeps it in the tens
of milliseconds; running tests there instead would make editing unusable.

**`--force-with-lease` is asked about, not refused.** The force-push rule
excludes it deliberately: it is the safe form, refusing to overwrite work the
local clone has not seen. It still reaches the generic push rule and therefore
still requires human approval, which is the right level of friction for an
operation that is safe but not routine.

**`gh` reports version 0.0.4**, which is not a GitHub CLI version number. Pull-request
creation may therefore not work through it. Since PR creation happens only after explicit
human acceptance, this is verified at that point rather than assumed now.
