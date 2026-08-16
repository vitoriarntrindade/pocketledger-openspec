#!/usr/bin/env python3
"""Deterministic PreToolUse guard for shell commands.

This runs before every Bash tool call and decides, without invoking a
language model, whether the command may proceed. It exists because some
operations are irreversible, and a guarantee that depends on the model
remembering to be careful is not a guarantee.

Three verdicts are possible:

``deny``
    The operation is irreversible or leaves the repository boundary. It is
    refused outright: destroying history, committing or pushing onto the
    default branch, escalating privilege, deleting or searching outside
    the repository, reading credential material, dropping data, or
    merging.

``ask``
    The operation is legitimate but outward-facing, so a human decides.
    Pushing to a remote and opening a pull request both fall here: the
    workflow reserves those for after human acceptance.

``allow`` (expressed by staying silent)
    Everything else. Ordinary development inside the repository is not
    interrupted, which is the entire point of drawing the boundary
    precisely rather than broadly.

Two ideas do most of the work:

*Containment, not patterns.* A path is dangerous because of where it
resolves, not because of how it is spelled. Deletion and search targets are
expanded, resolved and compared against the repository root, so `"$HOME"`,
`${HOME}`, `..` and `cd .. && rm -rf pocketledger-openspec` are all caught
by the same rule that catches `/etc`.

*Prose, not quoting.* A quoted span that is a message or a search pattern
is prose and must not fire the guard; a quoted span handed to `sh -c`,
`eval` or `| bash` is code and must be analysed like any other command.
Discarding all quoted text would turn every interpreter argument into a
blind spot.

What this guard does not cover, deliberately: a path assembled at runtime
(`K=~/.ssh/id_rsa; cat $K`), a path built inside an interpreter's own
source (`python -c '...expanduser...'`), and command substitution used to
name a file to read. This is a boundary for an agent doing ordinary work,
not a sandbox against an adversary; the irreversible cases it does cover
are the ones ordinary work reaches by accident.

Input arrives as hook JSON on stdin; the verdict is written to stdout.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys

# Branches that are protected whatever the remote says. The repository's
# real default branch is discovered at runtime and added to these, but the
# static pair still matters: a clone with no remote, or a remote whose HEAD
# is unset, must not silently lose the protection.
PROTECTED_BRANCHES = ("main", "master")

# Directories under $HOME that hold credential material. Containment is
# checked after the path is resolved, so `~/.aws`, `$HOME/.aws` and the
# absolute form are one rule rather than three patterns.
HOME_CREDENTIAL_DIRS = (
    ".ssh",
    ".aws",
    ".gnupg",
    ".kube",
    ".docker",
    ".claude",
    ".config/gcloud",
    ".config/gh",
    ".config/git",
    ".local/share/keyrings",
)

# Individual credential files, matched against the resolved path. The gh
# and git entries matter beyond their own contents: a readable OAuth token
# would let an agent publish through the API and walk straight past the
# human acceptance gate that `gh pr *` is behind.
CREDENTIAL_FILE_PATTERNS = (
    r"/id_(?:rsa|dsa|ecdsa|ed25519)",
    r"/\.netrc$",
    r"/\.pgpass$",
    r"/\.npmrc$",
    r"/\.pypirc$",
    r"/\.git-credentials$",
    r"/\.claude\.json$",
    r"/credentials(?:\.json)?$",
    r"/service-account\.json$",
    r"^/proc/(?:self|\d+)/environ$",
    r"\.(?:pem|key|p12|pfx|ppk|p8|jks|keystore|asc|gpg)$",
)

# Templates and fixtures whose names resemble credential material. Blocking
# these would teach people to route around the guard rather than respect it.
SAFE_MATERIAL = re.compile(
    r"\.example$|\.sample$|\.template$|/fixtures?/|/tests?/"
)

# A real environment file is any `.env`, with or without a suffix, that is
# not a template. Enumerating the suffixes let `.env.dev` and `.env.secret`
# through, and the set of names people invent is open-ended.
ENV_FILE = re.compile(r"^\.env(?:\.[\w.-]+)?$")
ENV_TEMPLATE_SUFFIXES = (".example", ".sample", ".template", ".dist")

# Creating a real environment file *from the template* is the documented
# first setup step, so it is exempt from the rule above. Reading an existing
# one is not: the exemption requires the template to be the source.
ENV_TEMPLATE_COPY = re.compile(
    r"\b(?:cp|install)\s[^<>]*?\.env\.(?:example|sample|template)\s+"
    r"[^\s<>]*\.env(?:\.[\w-]+)?(?![\w.])"
)

# Tools that walk a directory tree and print what they find. Rooted outside
# the repository they are a credential read with extra steps, and they are
# in the settings allowlist, so `find ~ -name id_rsa -exec cat {} +` would
# otherwise print key material with no prompt at all.
SEARCH_TOOLS = ("find", "grep", "rg", "ag", "ack", "fd", "fdfind")

# Options that consume the following word. Those words are configuration, not
# a query or a root. The parsers deliberately cover the shared, path-bearing
# options rather than modelling every display-only flag each tool supports.
SEARCH_OPTION_VALUES = {
    "grep": {
        "-A",
        "-B",
        "-C",
        "-e",
        "-f",
        "-m",
        "--after-context",
        "--before-context",
        "--binary-files",
        "--color",
        "--context",
        "--exclude",
        "--exclude-dir",
        "--exclude-from",
        "--file",
        "--include",
        "--label",
        "--max-count",
        "--regexp",
    },
    "rg": {
        "-A",
        "-B",
        "-C",
        "-e",
        "-f",
        "-g",
        "-j",
        "-m",
        "-r",
        "-t",
        "-T",
        "--after-context",
        "--before-context",
        "--context",
        "--encoding",
        "--engine",
        "--file",
        "--glob",
        "--iglob",
        "--max-count",
        "--max-depth",
        "--path-separator",
        "--pre",
        "--pre-glob",
        "--regexp",
        "--replace",
        "--sort",
        "--sortr",
        "--threads",
        "--type",
        "--type-not",
    },
    "ag": {"-e", "-f", "-g", "--file-search-regex", "--ignore-dir"},
    "ack": {"--ignore-dir", "--ignore-file", "--type", "--type-add"},
    "fd": {
        "-d",
        "-e",
        "-E",
        "-j",
        "-S",
        "-t",
        "--changed-after",
        "--changed-before",
        "--exclude",
        "--extension",
        "--glob",
        "--max-depth",
        "--owner",
        "--size",
        "--threads",
        "--type",
    },
    "fdfind": {
        "-d",
        "-e",
        "-E",
        "-j",
        "-S",
        "-t",
        "--changed-after",
        "--changed-before",
        "--exclude",
        "--extension",
        "--glob",
        "--max-depth",
        "--owner",
        "--size",
        "--threads",
        "--type",
    },
}

PATTERN_OPTIONS = {
    "grep": {"-e", "--regexp", "-f", "--file"},
    "rg": {"-e", "--regexp", "-f", "--file"},
    "ag": {"-e", "--file-search-regex"},
    "ack": set(),
}

# A quoted span containing whitespace is prose — a commit message, a grep
# pattern — unless an interpreter is going to run it, in which case it is
# code and every rule must see it.
QUOTED_PHRASE = re.compile(r"""(['"])([^'"]*\s[^'"]*)\1""")
INTERPRETED = re.compile(
    r"\b(?:ba|z|k|da)?sh\s+(?:-\w+\s+)*-c\b"
    r"|\|\s*(?:\S*/)?(?:ba|z|k|da)?sh\b"
    r"|\beval\b"
)

# `scp host:/root/.ssh/id_rsa .` carries the path behind a host prefix, and
# `curl -d @.env` behind an `@`, so both have to be unwrapped before the
# token looks like a path at all.
REMOTE_HOST_PREFIX = re.compile(r"^[\w.@-]+:(?=[/~])")

# Full ref paths name the same branch as their short form.
REF_PREFIX = re.compile(r"^refs/(?:heads|remotes/[^/]+)/")

# git's global options sit between `git` and the subcommand, so a rule that
# keys on `git push` never sees `git -c user.name=x push origin main`.
GIT_GLOBAL_OPTION = re.compile(
    r"\bgit\s+(?:(?:-c|-C|--git-dir|--work-tree|--namespace|--exec-path)"
    r"(?:=\S+|\s+\S+)|--no-pager|--paginate|--bare|--no-replace-objects"
    r"|--literal-pathspecs|-p)\s+"
)

# A command may move to another branch before it commits or pushes, so the
# branch at hook time is not necessarily the branch the work lands on.
BRANCH_SWITCH = re.compile(
    r"\bgit\s+(?:checkout|switch)\s+(?:-\w+\s+)*([\w./-]+)"
)

# `sudo` and `doas` are matched wherever they appear as a command word,
# which is what catches wrappers such as `xargs sudo rm`. The trailing
# whitespace requirement keeps `grep -rn 'sudo' docs/` out of the rule.
# `su` is not distinctive: it occurs inside ordinary prose and arguments,
# so it stays anchored to the start of a command.
SUDO = re.compile(r"(?<![\w-])(?:sudo|doas)(?=\s)")
SU_AS_COMMAND = re.compile(r"(?:^|[|;&]\s*)(?:env\s+)?(?:\w+=\S*\s+)*su\s")

# A target whose value is only known once the shell runs it cannot be
# checked for containment, and a recursive delete is not the place to
# guess.
UNRESOLVABLE = re.compile(r"\$\(|`|\$\w+|\$\{")

# Each rule is (verdict, compiled pattern, reason). They are matched
# against the code view of the command: quote characters removed, git
# global options folded away, trailing comments dropped.
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
    #
    # `git merge-base`, `merge-tree` and `merge-file` are read-only
    # plumbing that an agent needs while inspecting history, so the rule
    # stops at the exact subcommand rather than at a word boundary, where
    # a hyphen would have made every one of them look like a merge.
    (
        "deny",
        re.compile(r"\bgh\s+pr\s+merge\b|\bgit\s+merge(?![\w-])"),
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


# --- text views -------------------------------------------------------


def unquote(text: str) -> str:
    """Remove quote characters so a rule sees the command bash will run.

    `gh pr 'merge' 1` is the same command as `gh pr merge 1`, and a rule
    matching the raw string sees two different ones.
    """
    return text.replace('"', "").replace("'", "")


def strip_comment(text: str) -> str:
    """Drop a trailing shell comment.

    Without this, `pip install requests # uses .venv` satisfies a lookahead
    that was meant to describe the arguments, not the prose after them.
    """
    return re.sub(r"(?:^|\s)#.*$", "", text)


def normalise_git(text: str) -> str:
    """Fold away git's global options so the subcommand is visible."""
    previous = None
    while previous != text:
        previous = text
        text = GIT_GLOBAL_OPTION.sub("git ", text)
    return text


def code_view(command: str) -> str:
    """Return the command as the rule table should see it."""
    return strip_comment(normalise_git(unquote(command)))


def prose_filtered(command: str) -> str:
    """Return the command with prose removed, but code kept.

    A quoted phrase is a message or a pattern until an interpreter is
    handed it. `bash -c "cat .env"` and `echo "cat .env" | bash` are
    commands, not documentation, so nothing is discarded from them.
    """
    if INTERPRETED.search(command):
        return command
    return QUOTED_PHRASE.sub(" ", command)


# --- paths ------------------------------------------------------------


def token_path(token: str) -> str:
    """Return the filesystem path a shell word refers to, unexpanded."""
    text = unquote(token)
    text = re.sub(r"\$\{(\w+)\}", r"$\1", text)
    text = text.replace("$HOME", "~")
    text = text.lstrip("@")
    return REMOTE_HOST_PREFIX.sub("", text)


def resolve(token: str, base: str) -> str:
    """Resolve a shell word to an absolute path, relative to ``base``."""
    path = os.path.expanduser(token_path(token))
    if not os.path.isabs(path):
        path = os.path.join(base, path)
    return os.path.realpath(path)


def escapes(path: str, root: str) -> bool:
    """Report whether a resolved path lies outside the repository."""
    return path != root and not path.startswith(root + os.sep)


def arguments(segment: str, command_word: str) -> list[str]:
    """Return the non-option arguments a command was given."""
    match = re.search(rf"\b{command_word}\s+(.*)", segment)
    if match is None:
        return []
    return [w for w in match.group(1).split() if not w.startswith("-")]


def search_positionals(words: list[str], tool: str) -> tuple[list[str], bool]:
    """Return positional words and whether an option supplied a query."""
    positionals: list[str] = []
    pattern_option = False
    options_done = False
    index = 0
    value_options = SEARCH_OPTION_VALUES.get(tool, set())
    pattern_options = PATTERN_OPTIONS.get(tool, set())

    while index < len(words):
        word = words[index]
        if not options_done and word == "--":
            options_done = True
        elif not options_done and word in value_options:
            pattern_option = pattern_option or word in pattern_options
            index += 1
        elif not options_done and any(
            word.startswith(option + "=") for option in value_options
        ):
            option = word.split("=", 1)[0]
            pattern_option = pattern_option or option in pattern_options
        elif not options_done and any(
            option.startswith("-")
            and not option.startswith("--")
            and word.startswith(option)
            and word != option
            for option in value_options
        ):
            pattern_option = pattern_option or any(
                word.startswith(option) for option in pattern_options
            )
        elif not options_done and word.startswith("-"):
            pass
        else:
            positionals.append(word)
        index += 1
    return positionals, pattern_option


def find_roots(words: list[str]) -> list[str]:
    """Return the roots before the first find predicate."""
    roots: list[str] = []
    index = 0
    while index < len(words):
        word = words[index]
        if word == "-D":
            index += 1
        elif word in {"-H", "-L", "-P"}:
            pass
        elif word.startswith(("-", "!", "(")):
            break
        else:
            roots.append(word)
        index += 1
    return roots


def search_roots(words: list[str], tool: str) -> list[str]:
    """Return the path roots for a supported tree-walking search tool."""
    if tool == "find":
        return find_roots(words)

    positionals, pattern_option = search_positionals(words, tool)
    if tool == "rg" and "--files" in words:
        return positionals
    if tool in {"fd", "fdfind"}:
        return positionals[1:]
    if pattern_option:
        return positionals
    return positionals[1:]


# --- repository state -------------------------------------------------


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


def default_branch() -> str:
    """Return the repository's default branch, or an empty string.

    The remote's HEAD is the only authoritative statement of which branch
    is the default one, so it is asked first. Everything here fails soft:
    a repository with no remote, no commits or no git binary at all must
    still get a decision, because a guard that raises blocks every command
    rather than the dangerous ones.
    """
    try:
        out = subprocess.run(
            ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if out.returncode != 0:
        return ""
    return out.stdout.strip().rpartition("/")[2]


def protected_branches() -> frozenset[str]:
    """Return the branches that work may not be placed on directly.

    The discovered default branch is unioned with the static pair rather
    than replacing it, so a repository whose remote HEAD cannot be read
    still protects `main` and `master`.
    """
    discovered = default_branch()
    names = set(PROTECTED_BRANCHES)
    if discovered:
        names.add(discovered)
    return frozenset(names)


def effective_branch(command: str) -> str:
    """Return the branch the command would end on.

    `git switch main && git commit -m x` commits to main even though the
    branch at hook time is a feature branch, so the checkout inside the
    command counts for more than the current state does.
    """
    switches = BRANCH_SWITCH.findall(command)
    return switches[-1] if switches else current_branch()


# --- git destinations -------------------------------------------------


def branch_from_refspec(token: str) -> str:
    """Return the branch a push refspec ultimately writes to.

    `HEAD:refs/heads/main`, `+main` and `main` all reach the same branch;
    only the destination half of a colon-separated refspec matters.
    """
    ref = unquote(token).lstrip("+")
    ref = ref.rpartition(":")[2]
    return REF_PREFIX.sub("", ref)


def push_targets(command: str) -> list[str] | None:
    """Return the branches every ``git push`` in the command writes to.

    ``None`` means the command contains no push. Each bare word is treated
    as a possible destination, including the one that is usually the
    remote: `git push --repo=origin main` puts the branch in that
    position, and a remote actually named `main` is not a thing anyone
    has. A push naming no refspec publishes the branch the command ends
    on, so that branch is part of the answer too.
    """
    pushes = re.findall(r"\bgit\s+push\b([^|;&]*)", command)
    if not pushes:
        return None

    branch = effective_branch(command)
    targets: list[str] = []
    for push in pushes:
        words = [w for w in push.split() if not w.startswith("-")]
        if len(words) <= 1:
            targets.append(branch)
        for word in words:
            name = branch_from_refspec(word)
            targets.append(branch if name == "HEAD" else name)
    return targets


def push_to_protected_branch(command: str) -> str | None:
    """Return a reason if a push would land on a protected branch."""
    targets = push_targets(command)
    if targets is None:
        return None

    # `--mirror` and `--all` name no refspec yet publish every branch,
    # which includes the protected one.
    if re.search(r"\bgit\s+push\b[^|;&]*--(?:mirror|all)\b", command):
        return (
            "A --mirror or --all push publishes every branch, including "
            "the protected one."
        )

    protected = protected_branches()
    for target in targets:
        if target in protected:
            return (
                f"This push writes to '{target}', which is protected. All "
                "work goes through a feature branch and a pull request."
            )
    return None


def commit_to_protected_branch(command: str) -> str | None:
    """Return a reason if a commit would land on a protected branch.

    Blocking only the push leaves the work already sitting on the default
    branch by the time anyone notices, and moving it off again is manual
    recovery. The branch is created before the first commit, so the commit
    is where the rule belongs.
    """
    if not re.search(r"\bgit\s+commit(?![\w-])", command):
        return None
    branch = effective_branch(command)
    if branch and branch in protected_branches():
        return (
            f"This commit would land on '{branch}', which is protected. "
            "Create a '{type}/{slug}' branch first."
        )
    return None


# --- credentials ------------------------------------------------------


def is_env_file(name: str) -> bool:
    """Report whether a filename denotes a real environment file."""
    if not ENV_FILE.match(name):
        return False
    return not name.endswith(ENV_TEMPLATE_SUFFIXES)


def credential_path(command: str, root: str) -> str | None:
    """Return a reason if a path-shaped token names credential material.

    The check is positional rather than a substring search over the whole
    command. Matching anywhere flags any command that merely *mentions* a
    credential path — writing a permission rule, documenting the sandbox —
    and a guard that fires on documentation is one people learn to route
    around. So a pattern only counts inside a token that looks like a
    filesystem path: one starting with ``/``, ``~``, ``$HOME`` or ``./``,
    or hidden behind an `scp`-style ``host:`` or a `curl` ``@`` prefix.
    """
    home = os.path.realpath(os.path.expanduser("~"))
    protected_dirs = [os.path.join(home, d) for d in HOME_CREDENTIAL_DIRS]

    for token in re.split(r"[\s;|&<>]+", command):
        path = token_path(token)
        if not path.startswith(("/", "~", "./")):
            continue
        resolved = resolve(token, root)
        if any(
            resolved == d or resolved.startswith(d + os.sep)
            for d in protected_dirs
        ):
            return (
                "This reads private credential material. The agent works "
                "with .env.example and fixtures, never real secrets."
            )
        if SAFE_MATERIAL.search(resolved):
            continue
        for pattern in CREDENTIAL_FILE_PATTERNS:
            if re.search(pattern, resolved):
                return (
                    "This reads a private key or credential file. The "
                    "agent works with fixtures, never real secrets."
                )
    return None


def env_file_access(command: str) -> str | None:
    """Return a reason if the command opens a real environment file.

    Environment files are matched by name rather than by path, because
    `cat .env` is how they are actually read and that token starts with
    none of the prefixes that mark a token as a path. The command is
    examined one segment at a time so that the exemption earned by
    creating `.env` from the template cannot cover a `cat .env` chained
    after it.
    """
    for segment in re.split(r"[;&|]+", prose_filtered(command)):
        if ENV_TEMPLATE_COPY.search(segment):
            continue
        for token in re.split(r"[\s<>]+", segment):
            name = os.path.basename(token_path(token))
            if is_env_file(name):
                return (
                    "This reads a real environment file, which holds live "
                    "credentials. Use .env.example, which carries the "
                    "variable names with placeholder values."
                )
    return None


def search_outside_repository(
    words: list[str], cwd: str, root: str
) -> str | None:
    """Return a reason if a tree-walking search is rooted outside the repo.

    `find ~ -name id_rsa -exec cat {} +` reads exactly what the credential
    rule refuses to hand over, and `find` and `rg` are on the settings
    allowlist, so without this the material prints with no prompt at all.
    """
    if not words:
        return None

    tool = os.path.basename(words[0])
    arguments_after_tool = words[1:]
    if tool not in SEARCH_TOOLS:
        return None
    if tool == "find" and any(
        word == "-files0-from" or word.startswith("-files0-from=")
        for word in arguments_after_tool
    ):
        return (
            "find receives its search roots from a file, so the repository "
            "boundary cannot be checked before it runs."
        )
    for argument in search_roots(arguments_after_tool, tool):
        if escapes(resolve(argument, cwd), root):
            return (
                f"This searches '{argument}', which is outside the "
                "repository, and printing what it finds there is how "
                "credentials leak."
            )
    return None


def shell_segments(command: str) -> list[list[str]]:
    """Split a command at shell operators without breaking quoted arguments."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";|&")
    lexer.whitespace_split = True
    lexer.commenters = ""
    segments: list[list[str]] = []
    current: list[str] = []
    for token in lexer:
        if token in {";", "&", "&&", "|", "||"}:
            if current:
                segments.append(current)
                current = []
        else:
            current.append(token)
    if current:
        segments.append(current)
    return segments


def dangerous_deletion(segment: str, cwd: str, root: str) -> str | None:
    """Return a reason if a recursive delete escapes the repository.

    Recursive deletion inside the repository is ordinary housekeeping;
    anywhere else it is refused. Targets are resolved rather than matched,
    so `"$HOME"`, `${HOME}`, `..` and `../other-project` are the same case
    as `/etc`, and `-r` alone counts because `-f` only suppresses the
    prompt.
    """
    if not re.search(r"\brm\s+(?:-[a-zA-Z]*[rR]|--recursive\b)", segment):
        return None

    for target in arguments(segment, "rm"):
        if UNRESOLVABLE.search(token_path(target)):
            return (
                f"The delete target '{target}' is only known once the "
                "shell expands it, so it cannot be checked against the "
                "repository boundary before it runs."
            )
        resolved = resolve(target, cwd)
        if resolved == root:
            return "Recursive delete of the repository root."
        if escapes(resolved, root):
            return (
                f"Recursive delete targets '{target}', which is outside "
                "the repository."
            )
    return None


def walk_segments(command: str, root: str) -> str | None:
    """Check each command segment against the repository boundary.

    The working directory is tracked across the segments because
    `cd .. && rm -rf pocketledger-openspec` deletes this repository while
    naming nothing outside it.
    """
    cwd = root
    for words in shell_segments(command):
        segment = " ".join(words)
        reason = dangerous_deletion(segment, cwd, root)
        if reason:
            return reason
        reason = search_outside_repository(words, cwd, root)
        if reason:
            return reason
        if words and words[0] == "cd" and len(words) > 1:
            cwd = resolve(words[1], cwd)
    return None


def privilege_escalation(command: str) -> str | None:
    """Return a reason if the command escalates privilege.

    The check is not anchored to the start of the command, because `sudo`
    reached through a wrapper, such as `xargs sudo rm` or `time sudo make`,
    escalates exactly as much as `sudo` typed first.
    """
    text = prose_filtered(command)
    if SUDO.search(text) or SU_AS_COMMAND.search(text):
        return "Privilege escalation is outside the repository sandbox."
    return None


def decide(command: str, root: str) -> tuple[str, str] | None:
    """Return ``(verdict, reason)`` for a command, or ``None`` to allow."""
    code = code_view(command)
    checks = (
        credential_path(command, root),
        env_file_access(command),
        walk_segments(command, root),
        privilege_escalation(command),
        push_to_protected_branch(code),
        commit_to_protected_branch(code),
    )
    for reason in checks:
        if reason:
            return "deny", reason

    for verdict, pattern, rule_reason in RULES:
        if pattern.search(code):
            return verdict, rule_reason
    return None


def main() -> int:
    """Read the hook payload, emit a verdict, and exit."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # never block on a malformed payload

    command = payload.get("tool_input", {}).get("command", "")
    if not isinstance(command, str) or not command:
        return 0

    # A payload the guard cannot parse is a reason to stay out of the way;
    # path resolution on an odd string (an embedded NUL, a name longer than
    # the filesystem allows) must not turn into a traceback that leaves the
    # decision unmade and the operator unaware.
    try:
        verdict = decide(command, repo_root())
    except (OSError, ValueError, re.error) as err:
        print(f"guard-bash could not decide: {err}", file=sys.stderr)
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
