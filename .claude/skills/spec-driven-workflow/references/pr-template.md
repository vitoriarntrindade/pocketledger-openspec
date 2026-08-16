# Pull request structure

Used **only after explicit human acceptance**. Opening a pull request before
that point violates the human gate.

The pull request is where a reviewer decides whether to trust the change. Write
it for someone who was not present while it was built.

```markdown
## Summary

What was implemented, in two or three sentences. What the system can do now
that it could not before.

## Motivation

Why this was needed. The problem, not the solution.

## OpenSpec change

`openspec/changes/<name>/` — link the proposal and delta specs.
Requirements: X. Scenarios: X.

## Implementation

The main decisions and how the pieces fit. Point at the files a reviewer
should read first, and say what to look at in them.

## Architecture

Which layers were touched, and whether any boundary moved. State explicitly if
none did.

## Tests

What is covered, and how the requirements map onto tests. Name the tests that
carry the important guarantees, especially cross-user isolation.

## Coverage

Final percentage, and the change from the baseline.

## Quality gates

| Gate | Result |
|---|---|
| Formatting | |
| Lint | |
| Type checking | |
| Tests | |
| Coverage | |
| Security scan | |
| OpenSpec validation | |

## Security

What the change exposes, and what was checked. State plainly when there is no
meaningful security surface — that is a finding too.

## Documentation

Files updated, and why each one needed it.

## Trade-offs

What was accepted and what was given up. A reviewer who disagrees with a
trade-off needs to see that it was a decision rather than an oversight.

## Risks

What could still go wrong, and how it would show up.

## Breaking changes

Any. If none, say none.

## Migration

Steps required to deploy, if any.

## Verification

How to check this manually — the exact commands, and what correct output looks
like.
```

## Rules

- Open as a **draft**.
- Never merge. Merging is always the human's decision.
- Do not paste the whole diff into the body. The diff is already there; the
  body exists to explain it.
