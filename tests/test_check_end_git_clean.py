import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_end_git_clean.sh"
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


def _install_gate(repo: Path) -> None:
    tools_dir = repo / "tools"
    tools_dir.mkdir()
    shutil.copy2(SCRIPT, tools_dir / SCRIPT.name)
    shutil.copy2(REPO_ROOT_HELPER, tools_dir / REPO_ROOT_HELPER.name)
    _run_git(repo, "add", "tools/check_end_git_clean.sh", "tools/repo_root.sh")


def _init_repo(root: Path) -> Path:
    remote = root / "origin.git"
    work = root / "work"

    _run_git(root, "init", "--bare", str(remote))
    _run_git(root, "init", "-b", "main", str(work))
    _configure_identity(work)
    _install_gate(work)
    _commit_file(work, "tracked.txt", "initial\n")
    _run_git(work, "remote", "add", "origin", str(remote))
    _run_git(work, "push", "-u", "origin", "main")

    return work


def _run_script(
    cwd: Path, script_path: str = "tools/check_end_git_clean.sh"
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["END_GIT_BRANCH"] = "main"
    env["END_GIT_REMOTE"] = "origin"

    return subprocess.run(
        ["bash", script_path],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )


class CheckEndGitCleanTests(unittest.TestCase):
    def test_passes_on_clean_synced_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = _init_repo(Path(tmp))

            result = _run_script(work)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "end-git-check: PASS (main clean and synced with origin/main)",
            result.stdout,
        )

    def test_passes_from_subdirectory_on_clean_synced_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = _init_repo(Path(tmp))
            nested_dir = work / "nested"
            nested_dir.mkdir()

            result = _run_script(nested_dir, "../tools/check_end_git_clean.sh")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "end-git-check: PASS (main clean and synced with origin/main)",
            result.stdout,
        )

    def test_fails_on_feature_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = _init_repo(Path(tmp))
            _run_git(work, "switch", "-c", "feature/demo")

            result = _run_script(work)

        self.assertEqual(result.returncode, 1)
        self.assertIn("end-git-check: FAIL", result.stderr)
        self.assertIn("expected branch main, found feature/demo", result.stderr)
        self.assertIn("rerunning make end", result.stderr)

    def test_fails_on_dirty_working_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = _init_repo(Path(tmp))
            (work / "tracked.txt").write_text("changed\n", encoding="utf-8")

            result = _run_script(work)

        self.assertEqual(result.returncode, 1)
        self.assertIn(" M tracked.txt", result.stderr)
        self.assertIn("working tree is not clean", result.stderr)

    def test_fails_without_configured_remote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "work"
            _run_git(Path(tmp), "init", "-b", "main", str(work))
            _configure_identity(work)
            _install_gate(work)
            _commit_file(work, "tracked.txt", "initial\n")

            result = _run_script(work)

        self.assertEqual(result.returncode, 1)
        self.assertIn("remote origin is not configured", result.stderr)

    def test_fails_when_local_main_lags_remote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = _init_repo(root)
            updater = root / "updater"
            remote = root / "origin.git"

            _run_git(root, "clone", "--branch", "main", str(remote), str(updater))
            _configure_identity(updater)
            _commit_file(updater, "remote.txt", "remote update\n")
            _run_git(updater, "push", "origin", "main")

            result = _run_script(work)

        self.assertEqual(result.returncode, 1)
        self.assertIn("local main is not synced with origin/main", result.stderr)

    def test_fails_when_remote_branch_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = _init_repo(root)
            remote = root / "origin.git"
            _run_git(remote, "update-ref", "-d", "refs/heads/main")

            result = _run_script(work)

        self.assertEqual(result.returncode, 1)
        self.assertIn("could not resolve origin/main", result.stderr)
        self.assertIn("rerunning make end", result.stderr)


if __name__ == "__main__":
    unittest.main()
