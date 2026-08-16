## MODIFIED Requirements

### Requirement: Cross-LLM Skill Compatibility

The system SHALL version one canonical project skill tree under
`.claude/skills/` and expose that exact tree to Codex through the relative
symbolic link `.agents/skills`. It SHALL version the seven agent profiles and
guard wiring needed by each runtime, and SHALL detect a layout that restores
physical skill copies.

#### Scenario: Both coding agents receive the shared workflow
- **WHEN** a developer clones the repository for either Codex or Claude Code
- **THEN** both runtimes resolve the same versioned skill files without relying
  on personal machine configuration

#### Scenario: One canonical skill tree is maintained
- **WHEN** the infrastructure compatibility test runs
- **THEN** `.agents/skills` is a relative symbolic link resolving to
  `.claude/skills`
- **AND** no separate Codex-only skill copy or command wrapper is present

#### Scenario: Both runtimes carry their agent configuration
- **WHEN** the compatibility test inspects the versioned configuration
- **THEN** Codex has its `hooks.json` and the same seven role names under
  `.codex/agents/` that Claude Code has under `.claude/agents/`
- **AND** no agent requires personal machine configuration to find the
  workflow's specialised review roles
- **AND** Codex hook commands are resolved from the repository root rather
  than through Claude Code environment variables
