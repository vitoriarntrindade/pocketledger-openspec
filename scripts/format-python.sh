#!/usr/bin/env bash
#
# PostToolUse formatter: format the single Python file that was just edited.
#
# Scope is the whole point. This runs after every Write and Edit, so it has to
# stay in the tens of milliseconds. It formats one file with ruff and applies
# ruff's safe autofixes to that file only. It never runs the test suite, mypy,
# or a project-wide pass — those belong to `make quality`, which runs once per
# change rather than once per keystroke.
#
# Failures are swallowed deliberately: a file mid-edit may not parse yet, and
# an editing loop that errors on every intermediate state is unusable. The
# quality gate is what actually enforces formatting.
#
# Reads hook JSON on stdin.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${REPO_ROOT}/.venv/bin/python"
[[ -x "$PY" ]] || exit 0

file="$(jq -r '.tool_input.file_path // .tool_response.filePath // empty' 2>/dev/null)"
[[ -n "$file" && -f "$file" && "$file" == *.py ]] || exit 0

# Only touch files inside the repository.
case "$(realpath "$file" 2>/dev/null)" in
  "$REPO_ROOT"/*) ;;
  *) exit 0 ;;
esac

"$PY" -m ruff format --quiet "$file" >/dev/null 2>&1 || true
"$PY" -m ruff check --fix --quiet "$file" >/dev/null 2>&1 || true
exit 0
