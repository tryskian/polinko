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


def _terminate_process(process: subprocess.Popen) -> None:
    if process.poll() is None:
        process.kill()
    process.wait(timeout=2)


def _write_server_port_fakes(fake_bin: Path) -> None:
    _write_executable(
        fake_bin / "lsof",
        "#!/usr/bin/env bash\nprintf '%s\\n' \"$EXPECTED_PID\"\n",
    )
    _write_executable(
        fake_bin / "ps",
        (
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            'if [ "${1:-}" = "-o" ] && [ "${2:-}" = "command=" ] '
            '&& [ "${3:-}" = "-p" ] && [ "${4:-}" = "$EXPECTED_PID" ]; then\n'
            "  printf '%s -m uvicorn %s --host 127.0.0.1 --port %s --reload\\n' "
            '"$PYTHON" "$ASGI_APP" "$DEV_BACKEND_PORT"\n'
            "  exit 0\n"
            "fi\n"
            '/bin/ps "$@"\n'
        ),
    )


def _write_ready_health_fake(fake_bin: Path) -> None:
    _write_executable(fake_bin / "curl", "#!/usr/bin/env bash\nexit 0\n")


def _write_unready_health_fake(fake_bin: Path) -> None:
    _write_executable(fake_bin / "curl", "#!/usr/bin/env bash\nexit 1\n")


def _write_matching_server_ps_fake(fake_bin: Path) -> None:
    _write_executable(
        fake_bin / "ps",
        (
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            'if [ "${1:-}" = "-o" ] && [ "${2:-}" = "command=" ]; then\n'
            "  printf '%s -m uvicorn %s --host 127.0.0.1 --port %s --reload\\n' "
            '"$PYTHON" "$ASGI_APP" "$DEV_BACKEND_PORT"\n'
            "  exit 0\n"
            "fi\n"
            'if [ "${1:-}" = "-o" ] && [ "${2:-}" = "stat=" ]; then\n'
            "  printf 'S\\n'\n"
            "  exit 0\n"
            "fi\n"
            '/bin/ps "$@"\n'
        ),
    )


class RunServerDaemonTests(unittest.TestCase):
    def test_rejects_invalid_port_before_start(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
            cwd=REPO_ROOT,
            env={**os.environ, "DEV_BACKEND_PORT": "abc"},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("DEV_BACKEND_PORT must be", result.stderr)

    def test_rejects_empty_port_before_start(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
            cwd=REPO_ROOT,
            env={**os.environ, "DEV_BACKEND_PORT": ""},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("DEV_BACKEND_PORT must be", result.stderr)

    def test_rejects_invalid_readiness_bounds_before_start(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
            cwd=REPO_ROOT,
            env={**os.environ, "SERVER_START_ATTEMPTS": "0"},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("SERVER_START_ATTEMPTS must be a positive integer", result.stderr)

    def test_rejects_empty_readiness_attempts_before_start(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
            cwd=REPO_ROOT,
            env={**os.environ, "SERVER_START_ATTEMPTS": ""},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("SERVER_START_ATTEMPTS must be a positive integer", result.stderr)

    def test_rejects_empty_readiness_sleep_before_start(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
            cwd=REPO_ROOT,
            env={**os.environ, "SERVER_START_SLEEP_SECONDS": ""},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "SERVER_START_SLEEP_SECONDS must be a non-negative decimal number",
            result.stderr,
        )

    def test_rejects_empty_repo_slug_before_state_derivation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_root = tmp_path / "runtime"

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "SERVER_REPO_SLUG": "  ",
                    "SERVER_RUNTIME_ROOT": str(runtime_root),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "SERVER_REPO_SLUG must be a non-empty repo slug", result.stderr
            )
            self.assertFalse(runtime_root.exists())

    def test_rejects_blank_repo_slug_before_state_derivation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_root = tmp_path / "runtime"

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "SERVER_REPO_SLUG": "",
                    "SERVER_RUNTIME_ROOT": str(runtime_root),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "SERVER_REPO_SLUG must be a non-empty repo slug", result.stderr
            )
            self.assertFalse(runtime_root.exists())

    def test_rejects_health_url_port_mismatch_before_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "DEV_BACKEND_PORT": "8781",
                    "SERVER_HEALTH_URL": "http://127.0.0.1:8782/health",
                    "SERVER_PID_FILE": str(tmp_path / "server.pid"),
                    "SERVER_LOG": str(tmp_path / "server.log"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("SERVER_HEALTH_URL port must match 8781", result.stderr)
            self.assertFalse((tmp_path / "server.pid").exists())

    def test_rejects_empty_health_url_before_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "DEV_BACKEND_PORT": "8781",
                    "SERVER_HEALTH_URL": "",
                    "SERVER_PID_FILE": str(tmp_path / "server.pid"),
                    "SERVER_LOG": str(tmp_path / "server.log"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "SERVER_HEALTH_URL must include an explicit port", result.stderr
            )
            self.assertFalse((tmp_path / "server.pid").exists())

    def test_start_rejects_invalid_launcher_python_before_launch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PYTHON": sys.executable,
                    "SERVER_LAUNCHER_PYTHON": str(tmp_path / "missing-python"),
                    "DEV_BACKEND_PORT": "8781",
                    "SERVER_PID_FILE": str(tmp_path / "server.pid"),
                    "SERVER_LOG": str(tmp_path / "server.log"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("Configured SERVER_LAUNCHER_PYTHON", result.stderr)
            self.assertFalse((tmp_path / "server.pid").exists())

    def test_start_reports_blocked_pid_file_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            blocked_parent = tmp_path / "pid-parent"
            blocked_parent.write_text("not a directory", encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PYTHON": sys.executable,
                    "DEV_BACKEND_PORT": "8781",
                    "SERVER_PID_FILE": str(blocked_parent / "server.pid"),
                    "SERVER_LOG": str(tmp_path / "server.log"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                f"server-daemon failed to prepare PID file parent: {blocked_parent}",
                result.stderr,
            )

    def test_start_reports_blocked_log_file_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            blocked_parent = tmp_path / "log-parent"
            blocked_parent.write_text("not a directory", encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PYTHON": sys.executable,
                    "DEV_BACKEND_PORT": "8781",
                    "SERVER_PID_FILE": str(tmp_path / "server.pid"),
                    "SERVER_LOG": str(blocked_parent / "server.log"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                f"server-daemon failed to prepare log file parent: {blocked_parent}",
                result.stderr,
            )
            self.assertFalse((tmp_path / "server.pid").exists())

    def test_uses_existing_live_server_pid_without_starting_new_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            args_file = tmp_path / "python-args.txt"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            python_script = tmp_path / "python.sh"
            pid_file.write_text(str(process.pid), encoding="utf-8")
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
            _write_server_port_fakes(fake_bin)

            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": str(python_script),
                    "PYTHON_ARGS": str(args_file),
                    "EXPECTED_PID": str(process.pid),
                    "ASGI_APP": "server:app",
                    "DEV_BACKEND_PORT": "8764",
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

    def test_start_cleans_live_non_server_pid_file_without_killing_process(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            args_file = tmp_path / "python-args.txt"
            child_pid_file = tmp_path / "child.pid"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            _write_executable(fake_bin / "lsof", "#!/usr/bin/env bash\nexit 0\n")
            _write_ready_health_fake(fake_bin)
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
            python_script = tmp_path / "python.sh"
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
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": str(python_script),
                    "PYTHON_ARGS": str(args_file),
                    "SERVER_LAUNCHER_PYTHON": sys.executable,
                    "CHILD_PID_FILE": str(child_pid_file),
                    "ASGI_APP": "server:app",
                    "DEV_HOST": "127.0.0.1",
                    "DEV_BACKEND_PORT": "8770",
                    "SERVER_PID_FILE": str(pid_file),
                    "SERVER_LOG": str(tmp_path / "logs" / "server.log"),
                }
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.addCleanup(_kill_pid_file, child_pid_file)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("non-server process; cleaning up", result.stdout)
            self.assertIn("server-daemon started", result.stdout)
            self.assertIsNone(process.poll())

    def test_start_adopts_matching_server_without_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            args_file = tmp_path / "python-args.txt"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            _write_ready_health_fake(fake_bin)
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            python_script = tmp_path / "python.sh"
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
            _write_server_port_fakes(fake_bin)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": str(python_script),
                    "PYTHON_ARGS": str(args_file),
                    "EXPECTED_PID": str(process.pid),
                    "ASGI_APP": "server:app",
                    "DEV_BACKEND_PORT": "8767",
                    "SERVER_PID_FILE": str(pid_file),
                    "SERVER_LOG": str(tmp_path / "server.log"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("adopted PID", result.stdout)
            self.assertEqual(
                pid_file.read_text(encoding="utf-8").strip(), str(process.pid)
            )
            self.assertFalse(args_file.exists())

    def test_start_restarts_matching_server_with_interpreter_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            args_file = tmp_path / "python-args.txt"
            child_pid_file = tmp_path / "child.pid"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            _write_ready_health_fake(fake_bin)
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            expected_python = tmp_path / "expected-python.sh"
            existing_python = tmp_path / "existing-python.sh"
            _write_executable(
                expected_python,
                (
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [ "${1:-}" = "-c" ]; then\n'
                    "  printf '%s\\n' \"$EXPECTED_PYTHON_REAL\"\n"
                    "  exit 0\n"
                    "fi\n"
                    'printf "%s\\n" "$@" > "$PYTHON_ARGS"\n'
                    'printf "%s" "$$" > "$CHILD_PID_FILE"\n'
                    "sleep 30\n"
                ),
            )
            _write_executable(
                existing_python,
                (
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [ "${1:-}" = "-c" ]; then\n'
                    "  printf '%s\\n' \"$EXISTING_PYTHON_REAL\"\n"
                    "  exit 0\n"
                    "fi\n"
                ),
            )
            _write_executable(
                fake_bin / "lsof",
                "#!/usr/bin/env bash\nprintf '%s\\n' \"$EXPECTED_PID\"\n",
            )
            _write_executable(
                fake_bin / "ps",
                (
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [ "${1:-}" = "-o" ] && [ "${2:-}" = "command=" ] '
                    '&& [ "${3:-}" = "-p" ] && [ "${4:-}" = "$EXPECTED_PID" ]; then\n'
                    "  printf '%s -m uvicorn %s --host 127.0.0.1 --port %s --reload\\n' "
                    '"$EXISTING_PYTHON" "$ASGI_APP" "$DEV_BACKEND_PORT"\n'
                    "  exit 0\n"
                    "fi\n"
                    '/bin/ps "$@"\n'
                ),
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": str(expected_python),
                    "PYTHON_ARGS": str(args_file),
                    "SERVER_LAUNCHER_PYTHON": sys.executable,
                    "CHILD_PID_FILE": str(child_pid_file),
                    "EXPECTED_PID": str(process.pid),
                    "EXPECTED_PYTHON_REAL": "/tmp/polinko-expected-python",
                    "EXISTING_PYTHON": str(existing_python),
                    "EXISTING_PYTHON_REAL": "/tmp/polinko-existing-python",
                    "ASGI_APP": "server:app",
                    "DEV_BACKEND_PORT": "8772",
                    "SERVER_PID_FILE": str(pid_file),
                    "SERVER_LOG": str(tmp_path / "server.log"),
                },
                capture_output=True,
                text=True,
            )

            self.addCleanup(_kill_pid_file, child_pid_file)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("interpreter mismatch", result.stdout)
            self.assertIn("Restarting server-daemon", result.stdout)
            self.assertIn("server-daemon started", result.stdout)
            process.wait(timeout=2)
            self.assertNotEqual(
                pid_file.read_text(encoding="utf-8").strip(), str(process.pid)
            )
            self.assertTrue(args_file.exists())

    def test_start_does_not_replace_mismatched_server_that_does_not_exit(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            args_file = tmp_path / "python-args.txt"
            child_pid_file = tmp_path / "child.pid"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            process = subprocess.Popen(
                ["bash", "-c", "trap '' TERM; while :; do sleep 1; done"]
            )
            self.addCleanup(_terminate_process, process)
            expected_python = tmp_path / "expected-python.sh"
            existing_python = tmp_path / "existing-python.sh"
            _write_executable(
                expected_python,
                (
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [ "${1:-}" = "-c" ]; then\n'
                    "  printf '%s\\n' \"$EXPECTED_PYTHON_REAL\"\n"
                    "  exit 0\n"
                    "fi\n"
                    'printf "%s\\n" "$@" > "$PYTHON_ARGS"\n'
                    'printf "%s" "$$" > "$CHILD_PID_FILE"\n'
                    "sleep 30\n"
                ),
            )
            _write_executable(
                existing_python,
                (
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [ "${1:-}" = "-c" ]; then\n'
                    "  printf '%s\\n' \"$EXISTING_PYTHON_REAL\"\n"
                    "  exit 0\n"
                    "fi\n"
                ),
            )
            _write_executable(
                fake_bin / "lsof",
                "#!/usr/bin/env bash\nprintf '%s\\n' \"$EXPECTED_PID\"\n",
            )
            _write_executable(
                fake_bin / "ps",
                (
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [ "${1:-}" = "-o" ] && [ "${2:-}" = "command=" ] '
                    '&& [ "${3:-}" = "-p" ] && [ "${4:-}" = "$EXPECTED_PID" ]; then\n'
                    "  printf '%s -m uvicorn %s --host 127.0.0.1 --port %s --reload\\n' "
                    '"$EXISTING_PYTHON" "$ASGI_APP" "$DEV_BACKEND_PORT"\n'
                    "  exit 0\n"
                    "fi\n"
                    '/bin/ps "$@"\n'
                ),
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": str(expected_python),
                    "PYTHON_ARGS": str(args_file),
                    "SERVER_LAUNCHER_PYTHON": sys.executable,
                    "CHILD_PID_FILE": str(child_pid_file),
                    "EXPECTED_PID": str(process.pid),
                    "EXPECTED_PYTHON_REAL": "/tmp/polinko-expected-python",
                    "EXISTING_PYTHON": str(existing_python),
                    "EXISTING_PYTHON_REAL": "/tmp/polinko-existing-python",
                    "ASGI_APP": "server:app",
                    "DEV_BACKEND_PORT": "8774",
                    "SERVER_PID_FILE": str(pid_file),
                    "SERVER_LOG": str(tmp_path / "server.log"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("interpreter mismatch", result.stdout)
            self.assertIn("did not exit after stop signal", result.stdout)
            self.assertFalse(args_file.exists())
            self.assertFalse(pid_file.exists())
            self.assertIsNone(process.poll())

    def test_removes_stale_pid_and_starts_server_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            args_file = tmp_path / "python-args.txt"
            child_pid_file = tmp_path / "child.pid"
            python_script = tmp_path / "python.sh"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            _write_ready_health_fake(fake_bin)
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
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON_ARGS": str(args_file),
                    "SERVER_LAUNCHER_PYTHON": sys.executable,
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

    def test_start_preserves_live_pid_when_server_does_not_become_ready(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            args_file = tmp_path / "python-args.txt"
            child_pid_file = tmp_path / "child.pid"
            python_script = tmp_path / "python.sh"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            _write_executable(fake_bin / "lsof", "#!/usr/bin/env bash\nexit 0\n")
            _write_unready_health_fake(fake_bin)
            _write_matching_server_ps_fake(fake_bin)
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

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": str(python_script),
                    "PYTHON_ARGS": str(args_file),
                    "SERVER_LAUNCHER_PYTHON": sys.executable,
                    "CHILD_PID_FILE": str(child_pid_file),
                    "ASGI_APP": "server:app",
                    "DEV_HOST": "127.0.0.1",
                    "DEV_BACKEND_PORT": "8766",
                    "SERVER_PID_FILE": str(pid_file),
                    "SERVER_LOG": str(tmp_path / "logs" / "server.log"),
                    "SERVER_START_ATTEMPTS": "1",
                    "SERVER_START_SLEEP_SECONDS": "0",
                },
                capture_output=True,
                text=True,
            )

            self.addCleanup(_kill_pid_file, pid_file)
            self.assertEqual(result.returncode, 1)
            self.assertIn("did not become ready", result.stdout)
            self.assertIn("leaving PID file in place", result.stdout)
            self.assertTrue(pid_file.exists())
            self.assertEqual(
                pid_file.read_text(encoding="utf-8").strip(),
                child_pid_file.read_text(encoding="utf-8").strip(),
            )

    def test_status_reports_off_without_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            _write_executable(fake_bin / "lsof", "#!/usr/bin/env bash\nexit 0\n")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "SERVER_PID_FILE": str(tmp_path / "server.pid"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("server-daemon: OFF.", result.stdout)
            self.assertIn(f"Repo root: {REPO_ROOT}", result.stdout)
            self.assertIn(f"PID file: {tmp_path / 'server.pid'}", result.stdout)

    def test_status_derives_pid_and_log_from_state_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            state_dir = tmp_path / "runtime" / "toyrepo"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            _write_executable(fake_bin / "lsof", "#!/usr/bin/env bash\nexit 0\n")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "SERVER_REPO_SLUG": "toyrepo",
                    "SERVER_STATE_DIR": str(state_dir),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Repo: toyrepo", result.stdout)
            self.assertIn(f"Repo root: {REPO_ROOT}", result.stdout)
            self.assertIn(f"PID file: {state_dir / 'server.pid'}", result.stdout)
            self.assertIn(f"Log file: {state_dir / 'server.log'}", result.stdout)
            self.assertIn("server-daemon: OFF.", result.stdout)

    def test_status_reports_stale_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            pid_file.write_text("999999", encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={**os.environ, "SERVER_PID_FILE": str(pid_file)},
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("server-daemon: STALE PID file.", result.stdout)

    def test_status_rejects_live_non_server_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={**os.environ, "SERVER_PID_FILE": str(pid_file)},
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("not a matching server", result.stdout)
            self.assertTrue(pid_file.exists())
            self.assertIsNone(process.poll())

    def test_status_reports_matching_server_without_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            python_script = tmp_path / "python.sh"
            _write_executable(
                python_script,
                (
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [ "${1:-}" = "-c" ]; then\n'
                    "  command -v python3\n"
                    "  exit 0\n"
                    "fi\n"
                ),
            )
            _write_server_port_fakes(fake_bin)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": str(python_script),
                    "EXPECTED_PID": str(process.pid),
                    "ASGI_APP": "server:app",
                    "DEV_BACKEND_PORT": "8768",
                    "SERVER_PID_FILE": str(pid_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("RUNNING without managed PID file", result.stdout)

    def test_stop_kills_managed_pid_and_removes_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
            _write_server_port_fakes(fake_bin)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "stop"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": sys.executable,
                    "EXPECTED_PID": str(process.pid),
                    "ASGI_APP": "server:app",
                    "DEV_BACKEND_PORT": "8771",
                    "SERVER_PID_FILE": str(pid_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("server-daemon stopped", result.stdout)
            self.assertFalse(pid_file.exists())
            process.wait(timeout=2)

    def test_stop_preserves_pid_file_when_matching_server_does_not_exit(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            process = subprocess.Popen(
                ["bash", "-c", "trap '' TERM; while :; do sleep 1; done"]
            )
            self.addCleanup(_terminate_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
            _write_server_port_fakes(fake_bin)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "stop"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": sys.executable,
                    "EXPECTED_PID": str(process.pid),
                    "ASGI_APP": "server:app",
                    "DEV_BACKEND_PORT": "8775",
                    "SERVER_PID_FILE": str(pid_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("did not exit after stop signal", result.stdout)
            self.assertTrue(pid_file.exists())
            self.assertIsNone(process.poll())

    def test_stop_cleans_live_non_server_pid_file_without_killing_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            _write_executable(fake_bin / "lsof", "#!/usr/bin/env bash\nexit 0\n")
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "stop"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "SERVER_PID_FILE": str(pid_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("non-server process; cleaning up", result.stdout)
            self.assertFalse(pid_file.exists())
            self.assertIsNone(process.poll())

    def test_stop_closes_matching_server_without_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "server.pid"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            python_script = tmp_path / "python.sh"
            _write_executable(
                python_script,
                (
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [ "${1:-}" = "-c" ]; then\n'
                    "  command -v python3\n"
                    "  exit 0\n"
                    "fi\n"
                ),
            )
            _write_server_port_fakes(fake_bin)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "stop"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": str(python_script),
                    "EXPECTED_PID": str(process.pid),
                    "ASGI_APP": "server:app",
                    "DEV_BACKEND_PORT": "8769",
                    "SERVER_PID_FILE": str(pid_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("stopped matching server without PID file", result.stdout)
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
        self.assertIn("Usage: run_server_daemon.sh", result.stderr)


if __name__ == "__main__":
    unittest.main()
