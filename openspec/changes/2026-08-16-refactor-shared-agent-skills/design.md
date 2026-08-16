## Context

See `proposal.md` for motivation. The repository currently stores one physical
skill tree for Claude Code and another for Codex, then compares their contents
in the test suite. This detects drift but does not remove the duplicated edit
cost.

## Goals / Non-Goals

**Goals:**

- Maintain each shared skill in exactly one versioned file.
- Keep both runtimes able to discover their native configuration after clone.
- Fail the infrastructure test when a physical Codex skill copy reappears.

**Non-Goals:**

- Unify native agent-profile formats; Codex TOML and Claude Code Markdown have
  different runtime contracts.
- Replace the single repository gate with runtime-specific gate commands.
- Support filesystems that intentionally disable Git symbolic links.

## Decisions

### Decision: use a relative Git symlink for the Codex skill root

`.agents/skills` will point to `../.claude/skills`. The relative target works
from any clone location, keeps one canonical source visible in ordinary Git
history, and lets both runtimes execute the same skill instructions.

**Alternative considered: generated mirror.** A sync script would avoid manual
copying, but still writes two trees, creates generated-file churn on every
skill edit and needs another check to prove the mirror was refreshed.

**Alternative considered: keep duplicate files and compare bytes.** This is
the current design. It catches accidental divergence but spends context and
review effort on every deliberate edit.

### Decision: make shared skill language runtime-neutral

The workflow skill will instruct Codex to read `AGENTS.md` and Claude Code to
read `CLAUDE.md`. It will not encode a runtime-specific pointer, so the symlink
does not hide an intentional content difference.

### Decision: retain one shared deterministic gate

Both runtimes invoke `make quality`, which delegates to the same scripts and
configuration. Native hooks remain lightweight adapters; they do not fork the
quality rules.

## Risks / Trade-offs

- [Clone on a filesystem without symlink support] -> Git materializes or warns
  according to that client's policy; supported development environments must
  preserve symbolic links.
- [A runtime cannot follow a directory symlink] -> the compatibility test and
  a fresh-clone smoke check expose it before acceptance.
