#!/usr/bin/env bash
#
# Secret scan over tracked files.
#
# This lives in its own script so that the local gate and CI run exactly the
# same check. When it was a shell function inside quality.sh, CI could not
# call it, and the workflow claimed to run "the same gates" while quietly
# omitting this one.
#
# The scan runs at two breadths, because the two kinds of file fail
# differently.
#
# Source files get the full set: a private key block, a credential
# assignment, a connection string carrying a password. The match is
# case-insensitive, since AWS_SECRET_ACCESS_KEY is how the variable is
# actually written.
#
# Markdown and OpenSpec artifacts used to be skipped entirely. They are the
# largest agent-written surface in the repository and a pasted token is
# exactly what lands there, so they get the high-confidence patterns — the
# ones that cannot plausibly be prose — while staying exempt from the
# assignment patterns that documentation legitimately contains.
#
# Fixtures and tests stay exempt: credential-shaped strings are their job.
#
# Exits non-zero if anything is found.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Issued credential material. None of these shapes occurs by accident, so
# they are searched in every file, prose included.
KEY_MATERIAL='(BEGIN [A-Z ]*PRIVATE KEY'
KEY_MATERIAL+='|(ghp|gho|ghs|ghu|ghr)_[A-Za-z0-9]{30,}'
KEY_MATERIAL+='|github_pat_[A-Za-z0-9_]{20,}'
KEY_MATERIAL+='|xox[abposr]-[A-Za-z0-9-]{10,}'
KEY_MATERIAL+='|sk-[A-Za-z0-9]{30,}'
KEY_MATERIAL+='|AKIA[0-9A-Z]{16})'

# A connection string carrying an inline password.
INLINE_PASSWORD='://[^:@/[:space:]]+:[^@/[:space:]]+@'

# ...which this project writes on purpose, pointing at the local database.
# A development credential for a container on localhost is not a secret,
# and flagging it every run is how a scanner gets ignored.
LOCAL_TARGET='@(localhost|127\.0\.0\.1|0\.0\.0\.0|db|postgres'
LOCAL_TARGET+='|host\.docker\.internal)[:/]|\$\{|\$[A-Z_]'

# A secret being assigned a value. `jwt_secret` matters most: the
# application defaults it to a placeholder, and a real value committed in
# its place is precisely the leak the production guard exists to prevent.
# `password` is deliberately absent — in this codebase it names ORM columns
# and function parameters far more often than values.
ASSIGNMENT='((aws_)?secret_access_key|jwt_secret|secret_key|client_secret'
ASSIGNMENT+='|api_key|auth_token|refresh_token)'
ASSIGNMENT+='[[:space:]]*[:=][[:space:]]*.?[^[:space:]"'"'"',;{}$()<]{12,}'

# Values that announce themselves as not being real.
PLACEHOLDER='(example|placeholder|change-?me|dummy|sample|your[-_]|xxx'
PLACEHOLDER+='|redacted|test|dev|local|fake|not[-_]used|todo|str\b|Field\('
PLACEHOLDER+='|getenv|environ|\$\{|<[a-z])'

hits=0

report() {
  echo "  potential secret in: $1"
  hits=1
}

# Report only lines that survive an exclusion, so that a file may hold both
# a documented placeholder and, one day, a real value.
surviving() {
  local file="$1" pattern="$2" exclusion="$3"
  grep -IiE "$pattern" "$file" 2>/dev/null | grep -qivE "$exclusion"
}

while IFS= read -r file; do
  [[ -f "$file" ]] || continue
  case "$file" in
    */fixtures/* | tests/*) continue ;;
    *.example | *.sample | *.template) continue ;;
  esac

  if grep -qIiE "$KEY_MATERIAL" "$file" 2>/dev/null; then
    report "$file"
    continue
  fi
  if surviving "$file" "$INLINE_PASSWORD" "$LOCAL_TARGET"; then
    report "$file"
    continue
  fi

  # Prose may describe an assignment; source may not carry one.
  case "$file" in
    *.md | openspec/*) continue ;;
  esac
  if surviving "$file" "$ASSIGNMENT" "$PLACEHOLDER"; then
    report "$file"
  fi
done < <(git ls-files)

# A tracked .env is a leak regardless of its contents.
if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  echo "  a real .env file is tracked by git"
  hits=1
fi

exit "$hits"
