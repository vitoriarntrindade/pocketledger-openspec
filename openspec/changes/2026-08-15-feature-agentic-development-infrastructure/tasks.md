## 1. Project configuration baseline

- [x] 1.1 Rewrite `pyproject.toml` with real project metadata, Python 3.12
      target, and consolidated ruff, mypy, pytest and coverage configuration
      including the 95% floor
- [x] 1.2 Delete `.flake8` and move the complexity threshold to ruff `C901`
- [x] 1.3 Declare the quality tooling in `requirements-dev.txt`
- [x] 1.4 Reduce `.pre-commit-config.yaml` to the repository-protection layer,
      on current hook versions and current `stages` syntax

## 2. Deterministic gate and scripts

- [x] 2.1 Write `scripts/dev-db.sh`: idempotently start the `db` service and
      create the test database, never dropping or truncating
- [x] 2.2 Write `scripts/quality.sh`: ordered gate over format, lint, types,
      tests, coverage, security, secrets and OpenSpec validation, with a
      `--fast` subset
- [x] 2.3 Write `Makefile` targets wrapping the gate, so the `make check`
      referenced across existing documentation resolves
- [x] 2.4 Record the pre-existing failures the gate surfaced on its first run,
      so they can be told apart from anything this change introduced. The
      enumeration lives in
      `2026-08-15-refactor-python-quality-baseline/proposal.md` and was fixed
      by commits `30b1b45` and `c5ab5bc`. It can no longer be reproduced on
      this working tree, because that stacked change has already repaired it;
      re-observing it would mean checking out `5abeeed` and running the gate
      there, which is not done

## 3. Guard hooks

- [x] 3.1 Write `scripts/guard-bash.py` blocking pushes to the default branch,
      force pushes, destructive resets, `sudo`, recursive deletion outside the
      repository, and credential access
- [x] 3.2 Write `scripts/guard-write.py` blocking writes outside the
      repository and to secret files, while permitting `.env.example` and
      fixtures
- [x] 3.3 Write `scripts/format-python.sh` formatting only the single edited
      file
- [x] 3.4 Prove each guard end to end by piping a synthetic hook payload into
      the script as Claude Code invokes it, and asserting the emitted
      decision, so the payload parsing, the exit code and the JSON the hook
      actually returns are verified rather than assumed
- [x] 3.5 Write `scripts/session-context.sh`: report branch, uncommitted-file
      count and open OpenSpec changes with task progress at session start,
      reading state only
- [x] 3.6 Cover the session-start report with a smoke test, and add the
      `Session Workflow Context` requirement to the traceability map in the
      test module's docstring, which `test_every_requirement_has_a_test` reads

## 4. Claude Code configuration

- [x] 4.1 Write `.claude/settings.json` with `defaultMode`, permission
      allow/ask/deny lists, hook registrations and `skillOverrides`
- [x] 4.2 Validate the settings JSON structure and hook wiring with `jq`
- [x] 4.3 Document the deferred sandbox configuration and its prerequisites

## 5. Constitution and skills

- [x] 5.1 Write root `CLAUDE.md` containing only permanent, universal rules
- [x] 5.2 Remove `.claude/claude.md`, redistributing its tutorial content
- [x] 5.3 Restructure `python-best-practices` for progressive disclosure and
      current tooling
- [x] 5.4 Write the `spec-driven-workflow` skill covering classification and
      lifecycle
- [x] 5.5 Write the `pocketledger-architecture` skill covering layer rules and
      templates
- [x] 5.6 Write the `testing-and-coverage` skill covering fixtures, the
      database requirement and coverage strategy
- [x] 5.7 Remove `.claude/scripts/new-change.sh` and the
      `new-development-change` skill that depends on its unrecognised change
      layout

## 6. Subagents

- [x] 6.1 Write `spec-architect`, `feature-implementer` and `spec-verifier`
      definitions
- [x] 6.2 Write `test-engineer`, `quality-reviewer`, `security-reviewer` and
      `documentation-reviewer` definitions
- [x] 6.3 Confirm each definition declares its model and a minimal tool set

## 7. Infrastructure tests

- [x] 7.1 Write `tests/test_agentic_infrastructure.py` asserting guard
      behaviour for blocked and permitted operations
- [x] 7.2 Confirm the tests pass and are non-destructive

## 8. CI and documentation

- [x] 8.1 Write `.github/workflows/quality.yml` running the same gates
      remotely
- [x] 8.2 Write `docs/agentic-development.md` with the Mermaid lifecycle
      diagram
- [x] 8.3 Reconcile the existing workflow documents with the new single source
      of truth
- [x] 8.4 Add the pointer to the agentic documentation in `README.md`

## 9. Verification

- [x] 9.1 Run the full gate and record each result
- [x] 9.2 Delegate independent verification of spec compliance to
      `spec-verifier`
- [x] 9.3 Produce the final compliance report and stop for human acceptance
- [x] 9.4 Open the follow-up change for the pre-existing quality debt —
      `openspec/changes/2026-08-15-refactor-python-quality-baseline/`, planned
      in `14abb3d`

## 10. Repairs from independent verification

The `spec-verifier` audit found defects in the guards, gaps between the
artifacts and the repository, and one current spec this change had invalidated
without saying so. Each is tracked here so the repair is as traceable as the
original work.

- [x] 10.1 Block a push that reaches a protected branch through a refspec
      (`git push origin HEAD:main`), which the space-anchored pattern missed
- [x] 10.2 Block privilege escalation prefixed by environment assignments
      (`FOO=bar sudo …`, `env FOO=bar sudo …`)
- [x] 10.3 Block reads of a real environment file named without a path prefix
      (`cat .env`), while continuing to permit `.env.example`
- [x] 10.4 Split command tokens on redirection as well as whitespace and
      separators, so a credential path reached through `<` is not missed
- [x] 10.5 Extract the secret scan into `scripts/scan-secrets.sh` and call it
      from both the gate and CI, so the two cannot drift from each other
- [x] 10.6 Apply the coverage floor at `make test`, keeping the coverage flags
      out of pytest `addopts` so a single-test run is not measured against it
- [x] 10.7 Close the remaining guard findings from the audit, each with a test
      that fails before the fix and passes after it
- [x] 10.8 Modify the `code-structure` capability's quality-automation
      requirement, which this change invalidated by retiring flake8 and
      removing the lint, format and type hooks from pre-commit, and declare
      the modified capability in the proposal
- [x] 10.9 Record the coverage-floor entry-point distinction as a design
      decision, rather than leaving it in a comment in `pyproject.toml`
- [x] 10.10 Give `scripts/session-context.sh` a requirement, a task and a
      recorded decision, instead of a retroactive line in the impact list
- [x] 10.11 Correct the statements in this change's own artifacts that time
      has made false: the compliance-report expectation in `design.md`, and
      the documentation files missing from the proposal's impact list. The
      list is reconciled against `git status` rather than against its own
      earlier contents, which is what let two files stay missing through the
      first pass
- [x] 10.12 Justify, in `design.md`, the `S603`/`S607` per-file ignore the
      guard subprocess tests required, since the constitution allows a gate to
      be relaxed only by a change that writes down why
- [x] 10.13 Align `scripts/guard-write.py` with the Bash guard on what counts
      as a real environment file, and assert the two agree in a test, so the
      boundary cannot develop a hole shaped like a name one guard forgot
- [x] 10.14 Reflow the lines over 78 characters that the formatter cannot
      break, since `E501` is ignored on the grounds that the formatter
      enforces width — which it does not do inside comments and docstrings
- [x] 10.15 Block credential access behind a quoted interpreter invocation
      (`sh -c "cat ~/.ssh/id_rsa"`), a regression introduced by the
      quote-stripping that removed an unrelated false positive: the stripped
      token no longer starts with `~`, so the path check skips it
- [x] 10.16 Block recursive deletion that leaves the repository by a relative
      path (`rm -rf ../../etc`), which the absolute-path check does not see
- [x] 10.17 Block sending a real environment file as request data
      (`curl -d @.env`, `--data-binary @.env`), which reads the file without
      naming it as a command argument the credential check inspects
- [x] 10.18 Match credential paths containing spaces, which token splitting
      breaks into fragments that match nothing
- [x] 10.19 Inspect every push in a command rather than the first, so a second
      `git push` after `&&` or `;` is not reached unexamined
- [x] 10.20 Close the delta-spec traceability gap: have
      `test_every_requirement_has_a_test` read every `specs/*/spec.md` in the
      change directory rather than the `agentic-workflow` path alone, and
      cover the `code-structure` scenarios that no test yet exercises —
      pre-commit holding only the repository-protection hooks, ruff as the
      single linting authority with no `.flake8`, and `make check` resolving
      to the gate

## 11. Security review of the guard layer

A dedicated security review of the boundary followed the verifier's audit and
was probed independently across 36 cases. The repairs below are built and
verified; the two accepted trade-offs are recorded in `design.md` rather than
fixed, because they are choices rather than defects.

- [x] 11.1 Rewrite the deletion rule from pattern-matching to containment:
      unquote the target, normalise `${VAR}`, expand, resolve, and compare
      against the repository root. The old rule required the token to *begin*
      with `/`, `~` or `$HOME`, so `rm -rf "$HOME"`, `${HOME}`, `"/etc"`,
      `..`, `../*` and `cd .. && rm -rf pocketledger-openspec` were all
      permitted — quoting a path variable is good shell hygiene, which is why
      this was the case ordinary careful work would reach
- [x] 11.2 Deny tree-walking search rooted outside the repository — `find`,
      `grep`, `rg`, `ag`, `ack`, `fd` — including `-exec` and `-delete`. These
      tools are in the settings allowlist, so `find / -name id_rsa -exec cat
      {} +` printed key material with no prompt at all
- [x] 11.3 Move the credential inventory from regular expressions to
      containment over `~/.ssh`, `~/.aws`, `~/.gnupg`, `~/.kube`, `~/.docker`,
      `~/.claude`, `~/.config/gcloud`, `~/.config/gh`, `~/.config/git` and
      `~/.local/share/keyrings`, plus the individual credential files. The
      `gh` entry matters beyond its own contents: a readable OAuth token lets
      an agent publish through the API and walk past the human acceptance gate
      that `gh pr *` sits behind
- [x] 11.4 Evaluate the rules against a code view — quotes removed, git global
      options folded away, trailing comments stripped — so that
      `gh pr 'merge' 1`, `git -c user.name=x push origin main` and
      `pip install requests # uses .venv` are no longer permitted by their
      punctuation
- [x] 11.5 Judge a command that changes branch on the branch it would end on
      (`git switch main && git commit -m x`), not on the branch checked out
      when the command was submitted
- [x] 11.6 Recognise a real environment file by shape in both guards, so
      `.env.dev` and `.env.secret` are covered and the two guards cannot
      develop a hole shaped like a name one of them forgot
- [x] 11.7 Deny writes inside `.git/`, where `core.pager` and the hook scripts
      execute commands
- [x] 11.8 Make both guards fail deliberately rather than incidentally on an
      unexpected payload shape, reporting on standard error instead of exiting
      on a traceback that reads to Claude Code as an ordinary permit
- [x] 11.9 Invoke the guards with `python3` rather than the virtualenv
      interpreter. On a fresh clone, before `make install`, the hooks could not
      spawn at all: both guards were silently inert, with no warning that the
      boundary was absent
- [x] 11.10 Widen `scripts/scan-secrets.sh`: case-insensitive, in two tiers —
      issued key material in every file including `*.md` and `openspec/`,
      inline-password URLs and secret assignments in source only. Verified
      against a sandbox repository holding six realistic secrets, of which the
      previous pattern caught none
- [x] 11.11 Run `pre-commit run --all-files` in CI, so `detect-private-key`
      binds remotely and not only for a developer who ran `pre-commit install`
- [x] 11.12 Record the two accepted trade-offs in `design.md`: that the
      boundary deliberately does not protect its own scripts and hook
      configuration, and the specific gaps it does not cover — a path
      assembled at runtime, a path built inside an interpreter's own source,
      and `pkexec`
- [x] 11.13 Strengthen the `Deterministic Protection Of Dangerous Operations`
      scenarios to describe containment rather than pattern-matching, and add
      the behaviours the review built that no scenario named

## 12. Guard usability repair

- [x] 12.1 Parse search roots according to each supported tool's argument
      grammar, so a pattern that resembles `/etc/passwd` or `~` is not treated
      as an outside-repository root; add regression tests while keeping real
      outside roots blocked
- [x] 12.2 Repair and format the Python examples bundled with the active skill
      copies, so the quality gate validates the teaching material as well as
      the application code without weakening the lint configuration
- [x] 12.3 Version the shared skills for Codex and Claude Code, document the
      bounded compatibility differences, and test that the two roots cannot
      silently drift; version and verify the agent and hook configuration for
      both runtimes too, with Codex hook commands resolved without a Claude
      Code environment variable
- [x] 12.4 Reconcile entry-point documentation and the change artifacts with
      the dual constitutions, so Codex is not told to rely on `CLAUDE.md`
- [x] 12.5 Close the search-parser findings from independent security review:
      preserve quoted arguments, recognise executable paths and no-pattern
      modes, and refuse `find -files0-from`, with regression tests for each
