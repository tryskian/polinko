import os
import signal
import stat
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "run_portfolio_mockups.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _kill_pid_file(path: Path) -> None:
    if not path.exists():
        return
    raw_pid = path.read_text(encoding="utf-8").strip()
    if not raw_pid:
        return
    try:
        os.kill(int(raw_pid), signal.SIGTERM)
    except (ProcessLookupError, ValueError):
        return


class RunPortfolioMockupsTests(unittest.TestCase):
    def test_start_requires_mockup_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PORTFOLIO_MOCKUP_DIR": str(tmp_path / "missing"),
                    "PORTFOLIO_MOCKUP_PID_FILE": str(tmp_path / "mockups.pid"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("Portfolio mockup not found", result.stdout)

    def test_start_removes_stale_pid_and_starts_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            mockup_dir = tmp_path / "mockups"
            mockup_dir.mkdir()
            (mockup_dir / "landing-mockups.html").write_text(
                "<!doctype html><title>mockup</title>",
                encoding="utf-8",
            )
            pid_file = tmp_path / "mockups.pid"
            args_file = tmp_path / "python-args.txt"
            child_pid_file = tmp_path / "child.pid"
            python_script = tmp_path / "python.sh"
            pid_file.write_text("999999", encoding="utf-8")
            _write_executable(
                python_script,
                (
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'printf "%s\\n" "$@" > "$PYTHON_ARGS"\n'
                    'printf "%s" "$$" > "$CHILD_PID_FILE"\n'
                    "sleep 30\n"
                ),
            )

            env = os.environ.copy()
            env.update(
                {
                    "PYTHON": str(python_script),
                    "PYTHON_ARGS": str(args_file),
                    "CHILD_PID_FILE": str(child_pid_file),
                    "PORTFOLIO_MOCKUP_DIR": str(mockup_dir),
                    "PORTFOLIO_MOCKUP_PORT": "8766",
                    "PORTFOLIO_MOCKUP_URL": "http://127.0.0.1:9/missing.html",
                    "PORTFOLIO_MOCKUP_PID_FILE": str(pid_file),
                    "PORTFOLIO_MOCKUP_LOG": str(tmp_path / "logs" / "mockups.log"),
                }
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.addCleanup(_kill_pid_file, pid_file)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("portfolio mockup server started", result.stdout)
            for _ in range(10):
                if args_file.exists() and child_pid_file.exists():
                    break
                time.sleep(0.05)
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "http.server",
                    "8766",
                    "--bind",
                    "127.0.0.1",
                    "--directory",
                    str(mockup_dir),
                ],
            )
            self.assertEqual(
                pid_file.read_text(encoding="utf-8").strip(),
                child_pid_file.read_text(encoding="utf-8").strip(),
            )
            self.assertTrue((tmp_path / "logs").is_dir())

    def test_status_reports_stale_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "mockups.pid"
            pid_file.write_text("999999", encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PORTFOLIO_MOCKUP_PID_FILE": str(pid_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("portfolio mockup server: STALE PID file.", result.stdout)

    def test_stop_kills_managed_pid_and_removes_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "mockups.pid"
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(process.kill)
            pid_file.write_text(str(process.pid), encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "stop"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PORTFOLIO_MOCKUP_PID_FILE": str(pid_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("portfolio mockup server stopped", result.stdout)
            self.assertFalse(pid_file.exists())
            process.wait(timeout=2)

    def test_rejects_arguments(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "extra"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage: run_portfolio_mockups.sh", result.stderr)


if __name__ == "__main__":
    unittest.main()
