import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "git_prune_stale_refs.sh"
REPO_ROOT_HELPER = REPO_ROOT / "tools" / "repo_root.sh"


def _run_git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _configure_identity(repo: Path) -> None:
    _run_git(repo, "config", "user.name", "Polinko Test")
    _run_git(repo, "config", "user.email", "polinko-test@example.invalid")


def _commit_file(repo: Path, name: str, content: str) -> None:
    (repo / name).write_text(content, encoding="utf-8")
    _run_git(repo, "add", name)
    _run_git(repo, "commit", "-m", f"Add {name}")


def _install_helper(repo: Path) -> None:
    tools_dir = repo / "tools"
    tools_dir.mkdir()
    shutil.copy2(SCRIPT, tools_dir / SCRIPT.name)
    shutil.copy2(REPO_ROOT_HELPER, tools_dir / REPO_ROOT_HELPER.name)
    _run_git(repo, "add", "tools/git_prune_stale_refs.sh", "tools/repo_root.sh")


def _init_repo(root: Path, remote_name: str = "origin") -> Path:
    remote = root / f"{remote_name}.git"
    work = root / "work"

    _run_git(root, "init", "--bare", str(remote))
    _run_git(root, "init", "-b", "main", str(work))
    _configure_identity(work)
    _install_helper(work)
    _commit_file(work, "tracked.txt", "initial\n")
    _run_git(work, "remote", "add", remote_name, str(remote))
    _run_git(work, "push", "-u", remote_name, "main")

    return work


def _run_script(
    cwd: Path, remote_name: str = "origin"
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["END_GIT_REMOTE"] = remote_name

    return subprocess.run(
        ["bash", "tools/git_prune_stale_refs.sh"],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )


def _remote_branches(repo: Path) -> list[str]:
    result = _run_git(repo, "branch", "-r")
    return [line.strip() for line in result.stdout.splitlines()]


class GitPruneStaleRefsTests(unittest.TestCase):
    def test_prunes_stale_refs_for_configured_remote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = _init_repo(Path(tmp), remote_name="upstream")
            _run_git(work, "switch", "-c", "stale/demo")
            _commit_file(work, "stale.txt", "stale\n")
            _run_git(work, "push", "-u", "upstream", "stale/demo")
            _run_git(work, "switch", "main")
            self.assertIn("upstream/stale/demo", _remote_branches(work))

            _run_git(work, "push", "upstream", "--delete", "stale/demo")
            _run_git(
                work,
                "update-ref",
                "refs/remotes/upstream/stale/demo",
                "refs/heads/stale/demo",
            )
            self.assertIn("upstream/stale/demo", _remote_branches(work))
            result = _run_script(work, remote_name="upstream")
            self.assertNotIn("upstream/stale/demo", _remote_branches(work))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "git-prune-stale-refs: PASS (checked stale refs for upstream)",
            result.stdout,
        )

    def test_fails_without_configured_remote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = _init_repo(Path(tmp))

            result = _run_script(work, remote_name="missing")

        self.assertEqual(result.returncode, 1)
        self.assertIn("git-prune-stale-refs: FAIL", result.stderr)
        self.assertIn("remote missing is not configured", result.stderr)

    def test_empty_remote_name_uses_default_remote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = _init_repo(Path(tmp))

            result = _run_script(work, remote_name="")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "git-prune-stale-refs: PASS (checked stale refs for origin)",
            result.stdout,
        )

    def test_fails_on_malformed_remote_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = _init_repo(Path(tmp))

            result = _run_script(work, remote_name="origin remote")

        self.assertEqual(result.returncode, 1)
        self.assertIn("git-prune-stale-refs: FAIL", result.stderr)
        self.assertIn("END_GIT_REMOTE must be a non-empty remote name", result.stderr)


if __name__ == "__main__":
    unittest.main()
