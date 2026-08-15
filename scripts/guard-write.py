#!/usr/bin/env python3
"""Deterministic PreToolUse guard for file writes.

This draws the repository boundary for Edit, Write and NotebookEdit: broad
freedom inside the working directory, refusal outside it. It is the
filesystem half of the same principle the shell guard applies to commands —
autonomy is worth having only if its blast radius is known.

Two things are refused:

* writing to a path outside the repository, which is how an agent would
  reach configuration, credentials or another project by accident;
* writing to real secret material.

The secret check is written to distinguish, rather than to pattern-match on
the word "env". ``.env.example`` is the documented template that every
contributor needs, and test fixtures legitimately contain credential-shaped
strings. Blocking those would teach people to work around the guard, so the
rule targets real secrets only.

Input arrives as hook JSON on stdin; the verdict is written to stdout.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

# Real credential material, as opposed to templates and fixtures.
SECRET_FILENAMES = (
    ".env",
    ".env.local",
    ".env.production",
    ".env.prod",
    ".netrc",
    ".pypirc",
    "credentials",
    "id_rsa",
    "id_ed25519",
)

SECRET_SUFFIXES = (".pem", ".key", ".p12", ".pfx", ".keystore", ".jks")

# Templates and fixtures that must stay writable even though their names
# resemble secret material.
SAFE_PATTERN = re.compile(
    r"(\.example$|\.sample$|\.template$|/fixtures?/|/tests?/)",
)


def repo_root() -> str:
    """Return the repository root, preferring the value Claude Code sets."""
    env_root = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_root:
        return os.path.realpath(env_root)
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if out.returncode == 0:
            return os.path.realpath(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return os.path.realpath(os.getcwd())


def is_secret(path: str) -> bool:
    """Report whether a path denotes real credential material."""
    if SAFE_PATTERN.search(path):
        return False
    name = os.path.basename(path)
    if name in SECRET_FILENAMES:
        return True
    return any(name.endswith(suffix) for suffix in SECRET_SUFFIXES)


def decide(path: str, root: str) -> tuple[str, str] | None:
    """Return ``(verdict, reason)`` for a target path, or ``None`` to allow."""
    if not path:
        return None

    resolved = os.path.realpath(
        path if os.path.isabs(path) else os.path.join(root, path)
    )

    if resolved != root and not resolved.startswith(root + os.sep):
        return (
            "deny",
            (
                f"'{path}' is outside the repository. The agent "
                f"works only within {root}."
            ),
        )

    if is_secret(resolved):
        return (
            "deny",
            (
                f"'{os.path.basename(resolved)}' holds real credential "
                "material. Put variable names in .env.example with "
                "placeholder values instead."
            ),
        )

    return None


def main() -> int:
    """Read the hook payload, emit a verdict, and exit."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # never block on a malformed payload

    tool_input = payload.get("tool_input", {})
    path = (
        tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    )

    verdict = decide(path, repo_root())
    if verdict is None:
        return 0

    decision, reason = verdict
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decision,
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
