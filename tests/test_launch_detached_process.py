import os
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "launch_detached_process.py"


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


def _matching_processes(marker: str) -> list[str]:
    result = subprocess.run(
        ["ps", "-axo", "pid=,command="],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if marker in line]


class LaunchDetachedProcessTests(unittest.TestCase):
    def test_launches_command_args_and_writes_pid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "runtime" / "process.pid"
            log_file = tmp_path / "logs" / "process.log"
            args_file = tmp_path / "args.txt"
            child_pid_file = tmp_path / "child.pid"
            command = tmp_path / "command.sh"
            _write_executable(
                command,
                (
                    "#!/usr/bin/env sh\n"
                    "set -eu\n"
                    'printf "%s\\n" "$@" > "$ARGS_FILE"\n'
                    'printf "%s" "$$" > "$CHILD_PID_FILE"\n'
                    "sleep 30\n"
                ),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--pid-file",
                    str(pid_file),
                    "--log-file",
                    str(log_file),
                    "--",
                    str(command),
                    "alpha",
                    "two words",
                ],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "ARGS_FILE": str(args_file),
                    "CHILD_PID_FILE": str(child_pid_file),
                },
                capture_output=True,
                text=True,
            )

            self.addCleanup(_kill_pid_file, pid_file)
            self.assertEqual(result.returncode, 0, result.stderr)
            for _ in range(10):
                if args_file.exists() and child_pid_file.exists():
                    break
                time.sleep(0.05)
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                ["alpha", "two words"],
            )
            self.assertEqual(
                pid_file.read_text(encoding="utf-8").strip(),
                child_pid_file.read_text(encoding="utf-8").strip(),
            )
            self.assertTrue(log_file.exists())

    def test_launches_command_string_with_shell_style_splitting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "process.pid"
            log_file = tmp_path / "process.log"
            args_file = tmp_path / "args.txt"
            child_pid_file = tmp_path / "child.pid"
            command = tmp_path / "command.sh"
            _write_executable(
                command,
                (
                    "#!/usr/bin/env sh\n"
                    "set -eu\n"
                    'printf "%s\\n" "$@" > "$ARGS_FILE"\n'
                    'printf "%s" "$$" > "$CHILD_PID_FILE"\n'
                    "sleep 30\n"
                ),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--pid-file",
                    str(pid_file),
                    "--log-file",
                    str(log_file),
                    "--command-string",
                    f"{command} 'quoted value'",
                ],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "ARGS_FILE": str(args_file),
                    "CHILD_PID_FILE": str(child_pid_file),
                },
                capture_output=True,
                text=True,
            )

            self.addCleanup(_kill_pid_file, pid_file)
            self.assertEqual(result.returncode, 0, result.stderr)
            for _ in range(10):
                if args_file.exists() and child_pid_file.exists():
                    break
                time.sleep(0.05)
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(), ["quoted value"]
            )

    def test_rejects_missing_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--pid-file",
                    str(tmp_path / "process.pid"),
                    "--log-file",
                    str(tmp_path / "process.log"),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("missing command to launch", result.stderr)

    def test_stops_child_when_pid_file_write_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "process.pid"
            pid_file.mkdir()
            log_file = tmp_path / "process.log"
            marker = f"polinko-detached-launch-test-{os.getpid()}"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--pid-file",
                    str(pid_file),
                    "--log-file",
                    str(log_file),
                    "--",
                    sys.executable,
                    "-c",
                    "import time; time.sleep(30)",
                    marker,
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(log_file.exists())
            for _ in range(10):
                if not _matching_processes(marker):
                    break
                time.sleep(0.1)
            self.assertEqual(_matching_processes(marker), [])
