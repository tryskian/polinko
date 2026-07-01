import os
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from tools import launch_detached_process


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


def _kill_process_group(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
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

    def test_rejects_empty_executable(self) -> None:
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
                    "--command-string",
                    "''",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("missing executable to launch", result.stderr)

    def test_reports_missing_executable_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "process.pid"
            log_file = tmp_path / "process.log"
            missing_command = tmp_path / "missing-command"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--pid-file",
                    str(pid_file),
                    "--log-file",
                    str(log_file),
                    "--",
                    str(missing_command),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 127)
            self.assertIn("launch-detached: command not found", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(pid_file.exists())
            self.assertTrue(log_file.exists())

    def test_reports_unlaunchable_executable_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "process.pid"
            log_file = tmp_path / "process.log"
            command = tmp_path / "command.sh"
            command.write_text("#!/usr/bin/env sh\nsleep 30\n", encoding="utf-8")

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
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("launch-detached: failed to launch", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(pid_file.exists())
            self.assertTrue(log_file.exists())

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

            self.assertEqual(result.returncode, 1)
            self.assertIn("launch-detached: failed to write PID file", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertTrue(log_file.exists())
            for _ in range(10):
                if not _matching_processes(marker):
                    break
                time.sleep(0.1)
            self.assertEqual(_matching_processes(marker), [])

    def test_reports_log_file_open_failure_without_launching_child(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "process.pid"
            log_file = tmp_path / "process.log"
            log_file.mkdir()
            marker = f"polinko-detached-log-open-test-{os.getpid()}"

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

            self.assertEqual(result.returncode, 1)
            self.assertIn("launch-detached: failed to open log file", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(pid_file.exists())
            self.assertEqual(_matching_processes(marker), [])

    def test_stop_unmanaged_child_terminates_process_group(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            child_pid_file = tmp_path / "child.pid"
            marker = f"polinko-detached-group-test-{os.getpid()}"
            command = tmp_path / "command.sh"
            _write_executable(
                command,
                (
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    '"$PYTHON_BIN" -c "import time; time.sleep(30)" "$MARKER-child" &\n'
                    'printf "%s" "$!" > "$CHILD_PID_FILE"\n'
                    "sleep 30\n"
                ),
            )

            process = subprocess.Popen(
                [str(command)],
                env={
                    **os.environ,
                    "CHILD_PID_FILE": str(child_pid_file),
                    "MARKER": marker,
                    "PYTHON_BIN": sys.executable,
                },
                start_new_session=True,
            )
            self.addCleanup(_kill_process_group, process.pid)

            for _ in range(10):
                if child_pid_file.exists() and _matching_processes(marker):
                    break
                time.sleep(0.1)
            self.assertTrue(child_pid_file.exists())
            self.assertTrue(_matching_processes(marker))

            launch_detached_process._stop_unmanaged_child(process)

            for _ in range(10):
                if not _matching_processes(marker):
                    break
                time.sleep(0.1)
            self.assertEqual(_matching_processes(marker), [])
