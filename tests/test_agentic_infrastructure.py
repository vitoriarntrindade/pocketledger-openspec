"""Behavioural tests for the deterministic workflow guards.

These verify the `agentic-workflow` capability's protection requirements the
same way the application's tests verify its behaviour: by asserting outcomes,
not by inspecting configuration.

The guards are loaded by path because their filenames use hyphens, which are
not importable as modules. Every assertion calls `decide()` directly, so no
test here runs a shell command, touches the filesystem outside a temporary
directory, or performs any destructive action.

Traceability:
    Requirement: Feature Branch Isolation
        -> test_blocks_push_to_protected_branch
        -> test_blocks_force_push
    Requirement: Deterministic Protection Of Dangerous Operations
        -> test_blocks_destructive_history_rewrite
        -> test_blocks_privilege_escalation
        -> test_blocks_recursive_delete_outside_repository
        -> test_blocks_credential_reads
        -> test_blocks_data_destroying_operations
        -> test_blocks_write_outside_repository
        -> test_blocks_write_to_secret_files
        -> test_permits_safe_example_and_fixture_files
    Requirement: Human Acceptance Gate
        -> test_asks_before_publishing
        -> test_never_merges
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import types

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load(name: str, filename: str) -> types.ModuleType:
    """Load a hyphenated script from scripts/ as an importable module."""
    spec = importlib.util.spec_from_file_location(
        name, REPO_ROOT / "scripts" / filename
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


guard_bash = _load("guard_bash", "guard-bash.py")
guard_write = _load("guard_write", "guard-write.py")

ROOT = str(REPO_ROOT)


def verdict(command: str) -> str:
    """Return the guard's decision for a shell command."""
    result = guard_bash.decide(command, ROOT)
    return "allow" if result is None else result[0]


def write_verdict(path: str) -> str:
    """Return the guard's decision for a write target."""
    result = guard_write.decide(path, ROOT)
    return "allow" if result is None else result[0]


# --- Feature Branch Isolation ---------------------------------------------


def test_blocks_push_to_protected_branch():
    assert verdict("git push origin main") == "deny"
    assert verdict("git push origin master") == "deny"


def test_blocks_force_push():
    assert verdict("git push --force origin feature/x") == "deny"
    assert verdict("git push -f origin feature/x") == "deny"


def test_permits_ordinary_branch_work():
    assert verdict("git checkout -b feature/transfers") == "allow"
    assert verdict("git commit -m 'feat: add transfers'") == "allow"
    assert verdict("git status --short") == "allow"


# --- Deterministic Protection Of Dangerous Operations ----------------------


def test_blocks_destructive_history_rewrite():
    assert verdict("git reset --hard HEAD~3") == "deny"
    assert verdict("git clean -fdx") == "deny"
    assert verdict("git branch -D feature/x") == "deny"


def test_blocks_privilege_escalation():
    assert verdict("sudo systemctl restart postgres") == "deny"
    assert verdict("apt-get install redis") == "deny"


def test_blocks_global_package_installs():
    assert verdict("pip install requests") == "deny"
    assert verdict("pip install -r requirements-dev.txt") == "allow"


def test_blocks_recursive_delete_outside_repository():
    assert verdict("rm -rf /etc/nginx") == "deny"
    assert verdict("rm -rf ~/Documents") == "deny"


def test_permits_recursive_delete_inside_repository():
    assert verdict("rm -rf .pytest_cache") == "allow"
    assert verdict("rm -rf htmlcov") == "allow"


def test_blocks_credential_reads():
    home = str(pathlib.Path.home())
    assert verdict("cat ~/.ssh/id_rsa") == "deny"
    assert verdict("cp ~/.aws/credentials ./x") == "deny"
    assert verdict(f"cat {home}/.ssh/config") == "deny"


def test_mentioning_a_credential_path_is_not_access():
    """A guard that fires on documentation gets routed around.

    Writing a permission rule or a note that contains a credential path is
    not the same as reading one, and the guard must tell them apart.
    """
    assert verdict('echo "Edit(~/.ssh/**)" >> notes.md') == "allow"
    assert verdict("grep -r 'ssh' docs/") == "allow"


def test_blocks_data_destroying_operations():
    assert verdict("docker compose down -v") == "deny"
    assert verdict("dropdb pocketledger") == "deny"


def test_permits_ordinary_database_work():
    assert verdict("docker compose up -d db") == "allow"
    assert verdict("scripts/dev-db.sh") == "allow"


def test_blocks_write_outside_repository():
    assert write_verdict("/etc/hosts") == "deny"
    assert write_verdict("../other-project/main.py") == "deny"
    assert write_verdict(str(pathlib.Path.home() / ".bashrc")) == "deny"


def test_blocks_write_to_secret_files():
    assert write_verdict(".env") == "deny"
    assert write_verdict("config/server.pem") == "deny"
    assert write_verdict("deploy/id_rsa") == "deny"


def test_permits_safe_example_and_fixture_files():
    """Named like a secret is not the same as being one."""
    assert write_verdict(".env.example") == "allow"
    assert write_verdict("tests/fixtures/dummy.pem") == "allow"


def test_permits_ordinary_project_writes():
    assert write_verdict("app/services/transfer_service.py") == "allow"
    assert write_verdict("openspec/changes/x/proposal.md") == "allow"
    assert write_verdict("docs/agentic-development.md") == "allow"


# --- Human Acceptance Gate -------------------------------------------------


def test_asks_before_publishing():
    """Publishing is legitimate, but a human decides when."""
    assert verdict("git push origin feature/transfers") == "ask"
    assert verdict("gh pr create --draft") == "ask"


def test_never_merges():
    assert verdict("gh pr merge 12 --squash") == "deny"


def test_blocks_releases():
    assert verdict("gh release create v1.0.0") == "deny"
    assert verdict("twine upload dist/*") == "deny"


# --- Guard robustness ------------------------------------------------------


def test_malformed_payload_does_not_block_work():
    """A guard that crashes closed would halt all work on a bad payload."""
    assert guard_bash.decide("", ROOT) is None
    assert guard_write.decide("", ROOT) is None
