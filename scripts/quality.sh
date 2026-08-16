#!/usr/bin/env bash
#
# The automated definition of done.
#
# One command, run identically by a human, by an agent and by CI. A change is
# not finished until this exits zero. Nothing here may be satisfied by deleting
# a test, relaxing a rule or lowering the coverage floor.
#
# Every gate below is deterministic: ruff, mypy, pytest, coverage, bandit,
# openspec and git decide facts. No language model is invoked to restate what
# these tools already answer definitively.
#
# Usage:
#   scripts/quality.sh            full gate
#   scripts/quality.sh --fast     static checks only, no tests (edit loop)
#   scripts/quality.sh --fix      apply safe autofixes first, then full gate

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PY="${PY:-$REPO_ROOT/.venv/bin/python}"
[[ -x "$PY" ]] || PY="$(command -v python3)"

MODE="full"
case "${1:-}" in
  --fast) MODE="fast" ;;
  --fix)  MODE="fix" ;;
  "")     ;;
  *)      echo "unknown option: $1" >&2; exit 2 ;;
esac

BOLD=$'\033[1m'; RED=$'\033[0;31m'; GREEN=$'\033[0;32m'
YELLOW=$'\033[0;33m'; DIM=$'\033[2m'; NC=$'\033[0m'

RESULTS=()
FAILED=0

# Run one gate, record its verdict, keep going so a single run surfaces every
# problem at once rather than one per invocation.
gate() {
  local name="$1" mandatory="$2"; shift 2
  printf '%s\n' "${BOLD}── ${name}${NC}"
  if "$@"; then
    RESULTS+=("PASS|${name}")
    printf '%s\n\n' "${GREEN}✓ ${name}${NC}"
  elif [[ "$mandatory" == "advisory" ]]; then
    RESULTS+=("WARN|${name}")
    printf '%s\n\n' "${YELLOW}! ${name} (advisory, does not block)${NC}"
  else
    RESULTS+=("FAIL|${name}")
    FAILED=1
    printf '%s\n\n' "${RED}✗ ${name}${NC}"
  fi
}

# --- secret scan -----------------------------------------------------------
# Implemented in its own script so CI runs byte-for-byte the same check.
scan_secrets() {
  scripts/scan-secrets.sh
}

run_tests() {
  scripts/dev-db.sh --quiet || return 1
  # OTEL export is disabled for the gate on purpose. With it enabled and no
  # collector listening, the suite takes ~4 minutes and buries the result under
  # 32-second retry backoffs; disabled it takes ~43 seconds.
  OTEL_ENABLED=false \
  ENVIRONMENT=test \
  JWT_SECRET=test-only-secret-not-used-outside-tests \
    "$PY" -m pytest --cov=app --cov-report=term-missing --cov-report=xml
}

printf '%s\n\n' "${BOLD}PocketLedger quality gate${NC} ${DIM}(mode: ${MODE})${NC}"

if [[ "$MODE" == "fix" ]]; then
  printf '%s\n' "${BOLD}── applying safe autofixes${NC}"
  "$PY" -m ruff format .
  "$PY" -m ruff check --fix .
  echo
  MODE="full"
fi

gate "formatting"      mandatory "$PY" -m ruff format --check .
gate "lint"            mandatory "$PY" -m ruff check .
gate "type checking"   mandatory "$PY" -m mypy app
gate "secret scan"     mandatory scan_secrets
gate "openspec"        mandatory openspec validate --all --strict

if [[ "$MODE" == "full" ]]; then
  gate "security scan"  mandatory "$PY" -m bandit -c pyproject.toml -q -r app
  gate "tests+coverage" mandatory run_tests
  # Advisory: needs network access, and a newly disclosed CVE in a pinned
  # transitive dependency should not block an unrelated change mid-flight.
  gate "dependency audit" advisory "$PY" -m pip_audit --progress-spinner off
fi

printf '%s\n' "${BOLD}── summary${NC}"
for r in "${RESULTS[@]}"; do
  status="${r%%|*}"; name="${r#*|}"
  case "$status" in
    PASS) printf '  %s  %s\n' "${GREEN}PASS${NC}" "$name" ;;
    WARN) printf '  %s  %s\n' "${YELLOW}WARN${NC}" "$name" ;;
    FAIL) printf '  %s  %s\n' "${RED}FAIL${NC}" "$name" ;;
  esac
done
echo

if [[ "$FAILED" -eq 1 ]]; then
  printf '%s\n' "${RED}${BOLD}Quality gate FAILED.${NC} Diagnose, fix, re-run."
  printf '%s\n' "${DIM}Do not resolve a failure by deleting a test, relaxing a rule"
  printf '%s\n' "or lowering the coverage floor.${NC}"
  exit 1
fi

printf '%s\n' "${GREEN}${BOLD}Quality gate PASSED.${NC}"
