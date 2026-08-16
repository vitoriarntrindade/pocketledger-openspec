---
name: spec-driven-workflow
description: Run a change through the full lifecycle in this repository — classify it, specify it, branch, implement, verify with the gate, review it with the right specialist, and stop at the human acceptance gate. Use whenever a feature, fix, refactor or security change is requested and it is not obviously trivial.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
---

# Spec-driven workflow

This is the orchestration competence: given a request like *"add support for
transfers between accounts"*, decide what process it needs, run that process,
and know when to stop.

`CLAUDE.md` states the rules. This skill is how you apply them.

## 1. Classify first

Classification decides the process, so it happens before anything else. When a
request sits between two tiers, take the higher one — the cost of over-process
is some extra writing, the cost of under-process is unspecified behaviour in
production.

| Tier | Signals | Process |
|---|---|---|
| **TRIVIAL** | typo, comment, docstring wording; no behaviour change | fix it, run `make fast`, done |
| **SMALL** | one validation rule, a narrow endpoint tweak, a local refactor | branch, implement, `make quality`, brief report |
| **STANDARD** | new user-visible behaviour, contained in one or two layers | full workflow below |
| **COMPLEX** | auth, schema, external integration, cross-cutting, migrations | full workflow + `security-reviewer` + architecture review |
| **CRITICAL** | destructive migration, secrets, payments, central auth, infrastructure | full workflow + explicit human authorisation before any irreversible step |

Say the classification out loud before proceeding, so it can be challenged
early rather than after the work is done.

## 2. The lifecycle

```
classify → investigate → specify → branch → implement → gate → review → verify → report → STOP
```

**Investigate.** Read the relevant specs in `openspec/specs/`, the code in the
layers involved, and the existing tests. Prior changes in
`openspec/changes/archive/` show what was already decided.

**Specify.** For STANDARD and above, delegate to `spec-architect`. It produces
the proposal, delta specs, design and tasks, and validates them. Nothing is
implemented in this step.

**Branch.** Before the first edit: `git checkout -b {type}/{slug}`. Never
implement on `main` — a guard blocks the push, but by then the work is already
in the wrong place.

**Implement.** Either directly, or via `feature-implementer` when the change is
large enough that its output would crowd out your context. Follow the tasks in
order, write tests alongside the code, and keep strictly to the specified
scope. Tick tasks in `tasks.md` as you go.

**Gate.** `make quality`. When it fails: read the real error, hypothesise the
cause, fix the cause, re-run. Never weaken a gate to pass it.

**Review.** Choose specialists by what the change actually touches — running
all of them on every change is waste:

| The change touches | Run |
|---|---|
| any code | `quality-reviewer` |
| tests, or coverage moved | `test-engineer` |
| auth, data access, user input, config, external calls | `security-reviewer` |
| documented behaviour | `documentation-reviewer` |

**Verify.** For STANDARD and above, delegate to `spec-verifier` — always, and
never to whoever implemented it. An implementer confirming their own work
verifies nothing.

**Report.** Produce the compliance report (below) and stop.

## 3. When something fails

Fix it and continue. Do not interrupt the human for anything you can diagnose.

But do not loop blindly either. If the same gate fails three times, the retry
is not the problem — your model of the problem is. Stop, re-read the
requirement, and check whether the specification and the implementation
actually disagree. That disagreement is usually the real bug.

Escalate rather than repeat: a cheap model that has failed twice gets replaced
by a stronger one, carrying what the failed attempts learned. Each attempt must
use information the previous one produced; an identical retry is just a slower
failure.

Stop and ask only when the answer is a product decision you cannot infer, or
when the fix requires an operation outside the sandbox. Then present the
problem, the options, the trade-offs, and your recommendation.

## 4. The human gate

You may investigate, specify, branch, implement, refactor, test, fix, document,
verify and commit locally — all without asking.

Then stop. **No push, no pull request, before explicit acceptance.** Never
merge.

Present the report, and wait for the human to say so.

## 5. The compliance report

Report facts you actually collected, not what you expect the gate would say.
An unrun check is `N/A`, never `PASS`.

```
Change            <name>
Branch            <type>/<slug>
Classification    <tier>

OpenSpec          PASS / FAIL
Requirements      X / X implemented
Scenarios         X / X covered
Tests             PASS / FAIL   (N passed, N failed)
Coverage          XX.XX%
Lint              PASS / FAIL
Formatting        PASS / FAIL
Type checking     PASS / FAIL / N/A
Security review   PASS / FINDINGS / N/A
Documentation     PASS / FAIL
Spec compliance   PASS / FAIL

Files changed     <summary>
Trade-offs        <what was accepted, and why>
Known limitations <what it does not do>
Remaining risks   <what could still go wrong>

Recommendation    READY FOR HUMAN ACCEPTANCE / NOT READY
```

## 6. After acceptance

Only once the human has explicitly accepted: push the branch and open the pull
request with the sections in `references/pr-template.md`. Then stop again —
merging is never yours.

Archive the change only when it is genuinely complete and accepted, using
`openspec archive`. Archiving early destroys the record of what is still in
flight.

## Reference

- `references/classification.md` — worked examples of each tier, and the
  borderline cases that are easy to get wrong
- `references/pr-template.md` — the pull request structure
