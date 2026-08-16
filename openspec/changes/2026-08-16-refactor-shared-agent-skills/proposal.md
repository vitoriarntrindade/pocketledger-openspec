## Why

Codex and Claude Code currently carry physical copies of the same skills. A
byte-comparison test detects drift only after two files have already required
manual maintenance. The workflow needs one versioned source of truth that both
runtimes load and that both gates validate.

## What Changes

- Make `.claude/skills/` the canonical shared-skill directory.
- Replace `.agents/skills/` with a relative Git symlink to that canonical
  directory and remove redundant Codex command wrappers.
- Make the shared workflow skill refer to the runtime-native constitution
  without requiring distinct copies.
- Update documentation and infrastructure tests to describe and enforce the
  single-source layout.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agentic-workflow`: Cross-LLM skill compatibility changes from checked
  duplicate files to one canonical skill tree consumed by both runtimes.

## Impact

- `.agents/skills` becomes a relative symbolic link to `.claude/skills`.
- `.claude/skills/spec-driven-workflow/SKILL.md`, `AGENTS.md`, `CLAUDE.md`,
  `docs/agentic-development.md` and `docs/START-HERE.md` describe the shared
  source of truth.
- `tests/test_agentic_infrastructure.py` verifies the symbolic-link contract.
- `compliance-report.md` records the local gate and documentation-review
  evidence.

No application API, dependency or database behavior changes.
