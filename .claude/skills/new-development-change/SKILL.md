---
name: new-development-change
description: Create a new development change following the standardized workflow (feature, bugfix, security, refactor, etc.)
allowed-tools: Bash, Read, Write, Edit
license: MIT
compatibility: Bash-based, requires git
metadata:
  author: development-team
  version: "1.0"
  category: workflow
---

# New Development Change

This skill guides you through creating a new change following the PocketLedger standardized development workflow.

## How to Use

Invoke this skill when you want to start a new feature, bugfix, security patch, refactoring, or other change:

```bash
/new-development-change
```

Or specify the type directly:

```bash
/new-development-change feature audit-logging
/new-development-change bugfix rate-limit-persistence
/new-development-change security jwt-hardening
```

## What This Skill Does

1. **Prompts you** for the change type (feature, bugfix, security, refactor, perf, docs, chore)
2. **Creates the directory structure** in `openspec/changes/active/YYYY-MM-DD-{type}-{slug}/`
3. **Copies templates** for `proposal.md`, `design.md`, and `tasks.md`
4. **Creates a feature branch** named `{type}/{slug}`
5. **Stages files** in git
6. **Provides guidance** for the next steps

## Change Types

- **feature** — New functionality
- **bugfix** — Bug fix
- **security** — Security patch
- **refactor** — Code refactoring
- **perf** — Performance improvement
- **docs** — Documentation
- **chore** — Administrative tasks (deps, CI/CD, etc.)

## Workflow After Creation

After this skill completes:

1. **Edit the documentation:**
   - `proposal.md` — Why is this change needed?
   - `design.md` — How will we do it? (skip for docs/chore)
   - `tasks.md` — What are the concrete tasks?

2. **Implement the change** in the feature branch

3. **Commit frequently:**
   ```bash
   git commit -m "feat: add audit logging"
   ```

4. **Update tasks.md** as you complete items

5. **Run tests:**
   ```bash
   docker compose run --rm app-test pytest -v
   ```

6. **Open a draft PR:**
   ```bash
   gh pr create --draft --title "Feature: Audit logging"
   ```

7. **Get approval**, then merge:
   ```bash
   gh pr merge --squash
   ```

8. **Archive the change:**
   ```bash
   mv openspec/changes/active/2026-08-14-feature-audit-logging \
      openspec/changes/archive/2026-08-14-feature-audit-logging
   git add openspec/changes/archive/
   git commit -m "archive: feature-audit-logging"
   git push origin main
   ```

## Files Generated

For each change, you get:

```
openspec/changes/active/YYYY-MM-DD-{type}-{slug}/
├── proposal.md          # Motivation, context, requirements
├── design.md            # Technical decisions (not for docs/chore)
├── tasks.md             # Checklist of work items
└── specs/               # Optional: detailed specifications
```

All templates are pre-filled with guidance comments.

## Naming Conventions

- **Directory:** `YYYY-MM-DD-{type}-{slug}` (e.g., `2026-08-14-feature-audit-logging`)
- **Branch:** `{type}/{slug}` (e.g., `feature/audit-logging`)
- **Commit prefix:** `{type}:` (e.g., `feat:`, `fix:`, `security:`)

## Reviewing Changes

When a change is done, use the documentation to understand:

1. **proposal.md** — Why was this built?
2. **design.md** — What decisions were made and why?
3. **tasks.md** — What was actually implemented?
4. **Git commits** — How was it implemented?

This makes it easy for LLMs, new developers, or future maintainers to understand the full context.

## Reference

See `DEVELOPMENT.md` for the complete workflow guide and conventions.
