import os
import signal
import stat
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "run_server_daemon.sh"


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


class RunServerDaemonTests(unittest.TestCase):
    def test_uses_existing_live_pid_without_starting_new_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            args_file = tmp_path / "python-args.txt"
            python_script = tmp_path / "python.sh"
            pid_file.write_text(str(os.getpid()), encoding="utf-8")
            _write_executable(
                python_script,
                (
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [ "${1:-}" = "-c" ]; then\n'
                    "  command -v python3\n"
                    "  exit 0\n"
                    "fi\n"
                    'printf "%s\\n" "$@" > "$PYTHON_ARGS"\n'
                ),
            )

            env = os.environ.copy()
            env.update(
                {
                    "PYTHON": str(python_script),
                    "PYTHON_ARGS": str(args_file),
                    "SERVER_PID_FILE": str(pid_file),
                    "SERVER_LOG": str(tmp_path / "server.log"),
                }
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT))],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("server-daemon already running", result.stdout)
            self.assertFalse(args_file.exists())

    def test_removes_stale_pid_and_starts_server_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            args_file = tmp_path / "python-args.txt"
            child_pid_file = tmp_path / "child.pid"
            python_script = tmp_path / "python.sh"
            pid_file.write_text("999999", encoding="utf-8")
            _write_executable(
                python_script,
                (
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [ "${1:-}" = "-c" ]; then\n'
                    "  command -v python3\n"
                    "  exit 0\n"
                    "fi\n"
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
                    "ASGI_APP": "server:app",
                    "DEV_HOST": "127.0.0.1",
                    "DEV_BACKEND_PORT": "8765",
                    "SERVER_PID_FILE": str(pid_file),
                    "SERVER_LOG": str(tmp_path / "logs" / "server.log"),
                }
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT))],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.addCleanup(_kill_pid_file, child_pid_file)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("server-daemon started", result.stdout)
            for _ in range(10):
                if args_file.exists() and child_pid_file.exists():
                    break
                time.sleep(0.05)
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "uvicorn",
                    "server:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8765",
                    "--reload",
                ],
            )
            self.assertTrue((tmp_path / "logs").is_dir())

    def test_rejects_arguments(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "extra"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage: run_server_daemon.sh", result.stderr)


if __name__ == "__main__":
    unittest.main()
