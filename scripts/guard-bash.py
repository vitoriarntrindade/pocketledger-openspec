#!/usr/bin/env python3
"""Deterministic PreToolUse guard for shell commands.

This runs before every Bash tool call and decides, without invoking a
language model, whether the command may proceed. It exists because some
operations are irreversible, and a guarantee that depends on the model
remembering to be careful is not a guarantee.

Three verdicts are possible:

``deny``
    The operation is irreversible or leaves the repository boundary. It is
    refused outright: destroying history, escalating privilege, deleting
    outside the repository, reading credential material, dropping data,
    or merging a pull request.

``ask``
    The operation is legitimate but outward-facing, so a human decides.
    Pushing to a remote and opening a pull request both fall here: the
    workflow reserves those for after human acceptance.

``allow`` (expressed by staying silent)
    Everything else. Ordinary development inside the repository is not
    interrupted, which is the entire point of drawing the boundary
    precisely rather than broadly.

Input arrives as hook JSON on stdin; the verdict is written to stdout.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

PROTECTED_BRANCHES = ("main", "master")

# Credential material. Reading any of this is refused even when a plausible
# reason exists, because the agent never needs real secrets to do its work.
CREDENTIAL_PATHS = (
    r"~/\.ssh",
    r"\$HOME/\.ssh",
    r"/\.ssh/",
    r"~/\.aws",
    r"/\.aws/credentials",
    r"~/\.config/gcloud",
    r"~/\.kube/config",
    r"~/\.docker/config\.json",
    r"~/\.netrc",
    r"~/\.gnupg",
    r"~/\.claude\.json",
    r"\.pypirc",
    r"id_rsa",
    r"id_ed25519",
)

# Each rule is (verdict, compiled pattern, reason).
RULES: list[tuple[str, re.Pattern[str], str]] = [
    # --- irreversible git ---------------------------------------------
    (
        "deny",
        re.compile(
            r"\bgit\s+push\b.*(--force(?!-with-lease)\b|(?<![\w-])-f\b)"
        ),
        (
            "Force push rewrites published history. Use --force-with-lease "
            "only after explicit human instruction."
        ),
    ),
    (
        "deny",
        re.compile(r"\bgit\s+push\b[^|;&]*\s(main|master)\b"),
        (
            "Direct push to a protected branch. All work goes through a "
            "feature branch and a pull request."
        ),
    ),
    (
        "deny",
        re.compile(r"\bgit\s+reset\s+(--hard|--merge)\b"),
        (
            "Destructive reset discards uncommitted work irrecoverably. "
            "Use 'git restore' or 'git stash' instead."
        ),
    ),
    (
        "deny",
        re.compile(r"\bgit\s+clean\b.*-[a-z]*[fx]"),
        (
            "git clean permanently deletes untracked files, including any "
            "not yet staged."
        ),
    ),
    (
        "deny",
        re.compile(
            r"\bgit\s+(branch\s+(-D|--delete\s+--force)|update-ref\s+-d)"
        ),
        "Force-deleting a branch or ref can orphan unmerged commits.",
    ),
    (
        "deny",
        re.compile(
            r"\bgit\s+filter-(branch|repo)\b|\bgit\s+rebase\b.*\bmain\b"
        ),
        "Rewriting or rebasing shared history is not done autonomously.",
    ),
    # --- merge and release --------------------------------------------
    (
        "deny",
        re.compile(r"\bgh\s+pr\s+merge\b|\bgit\s+merge\b.*\b(main|master)\b"),
        "Merging is always a human decision. The agent never merges.",
    ),
    (
        "deny",
        re.compile(r"\bgh\s+release\b|\btwine\s+upload\b|\bnpm\s+publish\b"),
        (
            "Publishing is an outward-facing release action and is out of "
            "scope for autonomous work."
        ),
    ),
    # --- privilege and system -----------------------------------------
    (
        "deny",
        re.compile(r"(^|[|;&]\s*)(sudo|doas|su)\s"),
        "Privilege escalation is outside the repository sandbox.",
    ),
    (
        "deny",
        re.compile(
            r"\b(apt|apt-get|yum|dnf|pacman|brew)\s+(install|remove)\b"
        ),
        "System package management changes the machine, not the repository.",
    ),
    (
        "deny",
        re.compile(r"\bpip\s+install\b(?!.*(-r\s|\.venv|--python))"),
        (
            "Install into the project virtualenv (.venv/bin/pip or "
            "'uv pip install --python .venv/bin/python'), never globally."
        ),
    ),
    # --- data loss ------------------------------------------------------
    (
        "deny",
        re.compile(r"\bdocker\s+compose\s+down\b.*(-v\b|--volumes\b)"),
        "This deletes the database volume and every row in it.",
    ),
    (
        "deny",
        re.compile(r"\bdrop(db|\s+database)\b", re.IGNORECASE),
        "Dropping a database is destructive and irreversible.",
    ),
    (
        "deny",
        re.compile(r"\bTRUNCATE\b(?!.*_test\b)", re.IGNORECASE),
        (
            "TRUNCATE against a non-test database destroys data. The test "
            "fixtures already truncate the test database safely."
        ),
    ),
    # --- remote-facing, human decides ----------------------------------
    (
        "ask",
        re.compile(r"\bgit\s+push\b"),
        (
            "Pushing publishes work. The workflow reserves this for after "
            "human acceptance of the compliance report."
        ),
    ),
    (
        "ask",
        re.compile(r"\bgh\s+pr\s+create\b"),
        (
            "Opening a pull request happens only after explicit human "
            "acceptance."
        ),
    ),
]


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


def current_branch() -> str:
    """Return the checked-out branch name, or an empty string."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def credential_access(command: str) -> str | None:
    """Return a reason if the command reads credential material.

    The check is deliberately positional rather than a substring search over
    the whole command. Matching anywhere flags any command that merely
    *mentions* a credential path — writing a permission rule, documenting the
    sandbox, editing a config file — and a guard that fires on documentation
    is one people learn to route around.

    So a credential pattern only counts when it appears inside a token that
    actually looks like a filesystem path: one starting with ``/``, ``~``,
    ``$HOME`` or ``./``. That blocks the direct access this guard exists to
    stop (``cat ~/.ssh/id_rsa``, ``cp ~/.aws/credentials .``, ``scp``) while
    leaving text that talks about those paths alone.

    The trade-off is deliberate: a credential path buried inside an
    interpreter's inline source is not caught here. That case is covered by
    the tool-level ``Read`` deny rules in settings.json, which Claude Code
    enforces natively, and this guard is a boundary for an agent doing
    ordinary work rather than a defence against an adversarial one.
    """
    for token in re.split(r"[\s;|&]+", command):
        stripped = token.strip("\"'")
        if not stripped.startswith(("/", "~", "$HOME", "./")):
            continue
        for pattern in CREDENTIAL_PATHS:
            if re.search(pattern, stripped):
                return (
                    "This reads private credential material. The agent "
                    "works with .env.example and fixtures, never real "
                    "secrets."
                )
    return None


def dangerous_deletion(command: str, root: str) -> str | None:
    """Return a reason if a recursive delete escapes the repository.

    Recursive deletion inside the repository is ordinary housekeeping.
    Recursive deletion anywhere else, or against a bare path such as ``/``
    or ``~``, is refused.
    """
    if not re.search(
        r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)", command
    ):
        return None

    targets = re.findall(r"(?:^|\s)((?:/|~|\$HOME)[^\s;|&]*)", command)
    for target in targets:
        expanded = os.path.realpath(
            os.path.expanduser(target.replace("$HOME", "~"))
        )
        if expanded == "/" or not expanded.startswith(root + os.sep):
            return (
                f"Recursive delete targets '{target}', which is outside "
                "the repository."
            )
    if re.search(r"\brm\s+-[a-zA-Z]*[rf][a-zA-Z]*\s+(/|~|\*)\s*$", command):
        return "Recursive delete of a root or home path."
    return None


def push_to_current_protected_branch(command: str) -> str | None:
    """Refuse a bare ``git push`` while a protected branch is checked out."""
    if not re.search(r"\bgit\s+push\b", command):
        return None
    if re.search(r"\bgit\s+push\b[^|;&]*\s\S+\s+\S+", command):
        return None  # an explicit refspec is handled by the rule table
    if current_branch() in PROTECTED_BRANCHES:
        return (
            "The checked-out branch is protected, so a bare 'git push' "
            "would publish directly to it. Create a feature branch first."
        )
    return None


def decide(command: str, root: str) -> tuple[str, str] | None:
    """Return ``(verdict, reason)`` for a command, or ``None`` to allow."""
    reason = credential_access(command)
    if reason:
        return "deny", reason

    reason = dangerous_deletion(command, root)
    if reason:
        return "deny", reason

    reason = push_to_current_protected_branch(command)
    if reason:
        return "deny", reason

    for verdict, pattern, rule_reason in RULES:
        if pattern.search(command):
            return verdict, rule_reason
    return None


def main() -> int:
    """Read the hook payload, emit a verdict, and exit."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # never block on a malformed payload

    command = payload.get("tool_input", {}).get("command", "")
    if not command:
        return 0

    verdict = decide(command, repo_root())
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
