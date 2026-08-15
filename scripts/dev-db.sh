#!/usr/bin/env bash
#
# Ensure the PostgreSQL instance the test suite needs is running and that the
# test database exists.
#
# The test suite is deliberately not hermetic: it runs against the real
# PostgreSQL engine so that NUMERIC precision, referential integrity and
# per-user isolation are tested against the database that actually enforces
# them. That makes a running database a prerequisite of the quality gate, and a
# gate that fails because someone forgot to start a container is a gate that
# gets bypassed. This script removes that manual step.
#
# It is strictly additive and idempotent:
#   - it starts the compose `db` service only if it is not already healthy;
#   - it creates the test database only if it does not already exist;
#   - it never drops, truncates or resets anything.
#
# Usage: scripts/dev-db.sh [--quiet]

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DB_USER="${DB_USER:-pocketledger}"
DB_NAME="${DB_NAME:-pocketledger}"
TEST_DB_NAME="${TEST_DB_NAME:-${DB_NAME}_test}"
READY_TIMEOUT="${READY_TIMEOUT:-60}"

QUIET=0
[[ "${1:-}" == "--quiet" ]] && QUIET=1

log() { [[ "$QUIET" -eq 1 ]] || echo "$@"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

command -v docker >/dev/null 2>&1 \
  || fail "docker is not available, and the test suite requires PostgreSQL.
       Start a PostgreSQL 16 instance reachable at localhost:5433 with user
       '$DB_USER', or install Docker and re-run."

db_is_ready() {
  docker compose exec -T db pg_isready -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1
}

if db_is_ready; then
  log "database already running"
else
  log "starting database..."
  docker compose up -d db >/dev/null 2>&1 \
    || fail "could not start the 'db' compose service"

  for _ in $(seq 1 "$READY_TIMEOUT"); do
    db_is_ready && break
    sleep 1
  done

  db_is_ready || fail "database did not become ready within ${READY_TIMEOUT}s"
  log "database ready"
fi

# Create the test database if absent. docker-compose.yml creates only the
# primary database, so this gap would otherwise surface as 81 connection
# errors at the first test run.
exists="$(docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -tAc \
  "SELECT 1 FROM pg_database WHERE datname='${TEST_DB_NAME}'" 2>/dev/null || true)"

if [[ "$exists" == "1" ]]; then
  log "test database '${TEST_DB_NAME}' present"
else
  log "creating test database '${TEST_DB_NAME}'..."
  docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" \
    -c "CREATE DATABASE ${TEST_DB_NAME}" >/dev/null \
    || fail "could not create test database '${TEST_DB_NAME}'"
  log "test database created"
fi
