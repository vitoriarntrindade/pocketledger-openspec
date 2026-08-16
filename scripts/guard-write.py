#!/usr/bin/env python3
"""Deterministic PreToolUse guard for file writes.

This draws the repository boundary for Edit, Write and NotebookEdit: broad
freedom inside the working directory, refusal outside it. It is the
filesystem half of the same principle the shell guard applies to commands —
autonomy is worth having only if its blast radius is known.

Three things are refused:

* writing to a path outside the repository, which is how an agent would
  reach configuration, credentials or another project by accident;
* writing to real secret material;
* writing inside `.git`, where configuration and hooks are executable in
  everything but name.

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
    ".netrc",
    ".pypirc",
    ".npmrc",
    ".pgpass",
    ".git-credentials",
    "credentials",
    "credentials.json",
    "service-account.json",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
)

# Matched against every dotted component after the first, because a backup
# of a private key is still a private key: `server.pem.bak` slipped past a
# check that only looked at the final suffix.
SECRET_SUFFIXES = frozenset(
    {"pem", "key", "p12", "pfx", "ppk", "p8", "jks", "keystore", "asc", "gpg"}
)

# A real environment file is any `.env`, with or without a suffix, that is
# not a template. Enumerating the suffixes left `.env.dev` and `.env.secret`
# writable, and the set of names people invent is open-ended. The Bash guard
# applies the same rule to reads, and a test holds the two to one answer.
ENV_FILE = re.compile(r"^\.env(?:\.[\w.-]+)?$")
ENV_TEMPLATE_SUFFIXES = (".example", ".sample", ".template", ".dist")

# Templates and fixtures that must stay writable even though their names
# resemble secret material.
SAFE_PATTERN = re.compile(
    r"(\.example$|\.sample$|\.template$|/fixtures?/|/tests?/)",
)

# git's own directory. Writing here is not editing the project: `core.pager`
# and the hook scripts both execute arbitrary commands, so a write to
# `.git/config` is a write to the machine.
#
# The guard scripts, settings.json and .pre-commit-config.yaml are
# deliberately *not* protected this way. They are ordinary source — they
# are being edited as reviewed work right now, and they land in a diff a
# human reads — so a mechanical self-write ban would block legitimate work
# while stopping nobody who simply chose not to call the tool. What holds
# them is review and git history, recorded here so the choice is visible
# rather than assumed.
GIT_DIRECTORY = os.sep + ".git" + os.sep


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


def is_env_file(name: str) -> bool:
    """Report whether a filename denotes a real environment file."""
    if not ENV_FILE.match(name):
        return False
    return not name.endswith(ENV_TEMPLATE_SUFFIXES)


def is_secret(path: str) -> bool:
    """Report whether a path denotes real credential material."""
    if SAFE_PATTERN.search(path):
        return False
    name = os.path.basename(path)
    if is_env_file(name) or name in SECRET_FILENAMES:
        return True
    return any(
        part in SECRET_SUFFIXES for part in name.lower().split(".")[1:]
    )


def decide(path: str, root: str) -> tuple[str, str] | None:
    """Return ``(verdict, reason)`` for a path, or ``None`` to allow it."""
    if not path:
        return None

    resolved = os.path.realpath(
        path if os.path.isabs(path) else os.path.join(root, path)
    )

    if GIT_DIRECTORY in resolved + os.sep:
        return (
            "deny",
            (
                "'.git' holds the repository's own configuration and hooks, "
                "both of which execute commands. Change the working tree "
                "and let git record it."
            ),
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
    if not isinstance(path, str):
        return 0

    # Failing open on a payload the guard cannot read is deliberate; failing
    # open on a traceback is not the same thing. An unexpected path — an
    # embedded NUL, a name longer than the filesystem allows — used to exit
    # 1, which Claude Code treats as "carry on", so an odd input disabled
    # the boundary instead of the tool call.
    try:
        verdict = decide(path, repo_root())
    except (OSError, ValueError) as err:
        print(f"guard-write could not decide: {err}", file=sys.stderr)
        return 0

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
