#!/usr/bin/env bash
#
# SessionStart hook: state the workflow situation once, at the top of a session.
#
# This is the observability layer for the workflow itself. Without it, a new
# session starts blind to whether work is already in flight — which branch is
# checked out, whether an OpenSpec change is open, whether its tasks are
# finished. Every one of those facts is cheap to read from disk and expensive
# to rediscover through conversation.
#
# It reads state only. It runs no gate, starts no container and makes no
# network call, so it stays well under a second.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 0

branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
dirty_count="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"

changes=""
if [[ -d openspec/changes ]]; then
  changes="$(find openspec/changes -maxdepth 1 -mindepth 1 -type d \
    -not -name archive -printf '%f\n' 2>/dev/null | sort)"
fi

context="Workflow state
  branch: ${branch}"

if [[ "$branch" == "main" || "$branch" == "master" ]]; then
  context+="  (protected - create a feature branch before implementing)"
fi

context+="
  uncommitted files: ${dirty_count}"

if [[ -n "$changes" ]]; then
  context+="
  active OpenSpec changes:"
  while IFS= read -r change; do
    [[ -n "$change" ]] || continue
    # grep -c prints 0 and exits 1 when nothing matches, so a `|| echo 0`
    # fallback would emit the count twice. Take the first line instead.
    tasks_file="openspec/changes/${change}/tasks.md"
    total="$(grep -c '^- \[' "$tasks_file" 2>/dev/null | head -1)"
    done_n="$(grep -c '^- \[x\]' "$tasks_file" 2>/dev/null | head -1)"
    context+="
    - ${change} (tasks ${done_n}/${total})"
  done <<< "$changes"
else
  context+="
  active OpenSpec changes: none"
fi

context+="

The definition of done is 'make quality'. It must pass before any change is
reported complete, and no pull request is opened before human acceptance."

jq -n --arg ctx "$context" \
  '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$ctx}}' \
  2>/dev/null || true
