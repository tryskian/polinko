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
SCRIPT = REPO_ROOT / "tools" / "run_eval_sidecar_start.sh"


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


def _write_sidecar_pid_fake(fake_bin: Path) -> None:
    _write_executable(
        fake_bin / "ps",
        (
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            'if [ "${1:-}" = "-o" ] && [ "${2:-}" = "command=" ] '
            '&& [ "${3:-}" = "-p" ] && [ "${4:-}" = "$EXPECTED_PID" ]; then\n'
            '  printf "%s -m tools.eval_sidecar run --target %s\\n" '
            '"$PYTHON" "${EVAL_SIDECAR_TARGET:-quality-gate-deterministic}"\n'
            "  exit 0\n"
            "fi\n"
            '/bin/ps "$@"\n'
        ),
    )


def _sidecar_ready_python_stub() -> str:
    return (
        "#!/usr/bin/env sh\n"
        "set -eu\n"
        'printf "%s\\n" "$@" > "$PYTHON_ARGS"\n'
        'printf "%s" "$$" > "$CHILD_PID_FILE"\n'
        'current_file=""\n'
        'while [ "$#" -gt 0 ]; do\n'
        '  if [ "${1:-}" = "--current-file" ]; then\n'
        "    shift\n"
        '    current_file="${1:-}"\n'
        "  fi\n"
        "  shift || true\n"
        "done\n"
        'if [ -n "$current_file" ]; then\n'
        '  run_dir="$(dirname "$current_file")/test-run"\n'
        '  mkdir -p "$run_dir" "$(dirname "$current_file")"\n'
        '  printf "%s" "$run_dir" > "$current_file"\n'
        '  printf "{}" > "$run_dir/status.json"\n'
        "fi\n"
        "sleep 30\n"
    )


class RunEvalSidecarStartTests(unittest.TestCase):
    def test_start_rejects_invalid_launcher_python_before_launch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PYTHON": sys.executable,
                    "EVAL_SIDECAR_LAUNCHER_PYTHON": str(tmp_path / "missing-python"),
                    "EVAL_SIDECAR_PID_FILE": str(tmp_path / "sidecar.pid"),
                    "EVAL_SIDECAR_LOG": str(tmp_path / "sidecar.log"),
                    "EVAL_SIDECAR_RUNS_DIR": str(tmp_path / "runs"),
                    "EVAL_SIDECAR_CURRENT_FILE": str(tmp_path / "current.txt"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("Configured EVAL_SIDECAR_LAUNCHER_PYTHON", result.stderr)
            self.assertFalse((tmp_path / "sidecar.pid").exists())

    def test_uses_existing_live_sidecar_pid_without_starting_new_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "sidecar.pid"
            current_file = tmp_path / "current.txt"
            args_file = tmp_path / "python-args.txt"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            python_script = tmp_path / "python.sh"
            pid_file.write_text(str(process.pid), encoding="utf-8")
            current_file.write_text(str(tmp_path / "run"), encoding="utf-8")
            _write_executable(
                python_script,
                '#!/usr/bin/env sh\nset -eu\nprintf "%s\\n" "$@" > "$PYTHON_ARGS"\n',
            )
            _write_sidecar_pid_fake(fake_bin)

            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": str(python_script),
                    "PYTHON_ARGS": str(args_file),
                    "EXPECTED_PID": str(process.pid),
                    "EVAL_SIDECAR_PID_FILE": str(pid_file),
                    "EVAL_SIDECAR_LOG": str(tmp_path / "sidecar.log"),
                    "EVAL_SIDECAR_RUNS_DIR": str(tmp_path / "runs"),
                    "EVAL_SIDECAR_CURRENT_FILE": str(current_file),
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
            self.assertIn("eval-sidecar already running", result.stdout)
            self.assertFalse(args_file.exists())

    def test_start_reports_live_pid_without_current_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "sidecar.pid"
            current_file = tmp_path / "current.txt"
            args_file = tmp_path / "python-args.txt"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            python_script = tmp_path / "python.sh"
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
            _write_executable(
                python_script,
                '#!/usr/bin/env sh\nset -eu\nprintf "%s\\n" "$@" > "$PYTHON_ARGS"\n',
            )
            _write_sidecar_pid_fake(fake_bin)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": str(python_script),
                    "PYTHON_ARGS": str(args_file),
                    "EXPECTED_PID": str(process.pid),
                    "EVAL_SIDECAR_PID_FILE": str(pid_file),
                    "EVAL_SIDECAR_CURRENT_FILE": str(current_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("eval-sidecar current file missing", result.stdout)
            self.assertIn("already running without run context", result.stdout)
            self.assertFalse(args_file.exists())

    def test_start_cleans_live_non_sidecar_pid_file_without_killing_process(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "sidecar.pid"
            args_file = tmp_path / "python-args.txt"
            child_pid_file = tmp_path / "child.pid"
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
            python_script = tmp_path / "python.sh"
            _write_executable(python_script, _sidecar_ready_python_stub())

            env = os.environ.copy()
            env.update(
                {
                    "PYTHON": str(python_script),
                    "PYTHON_ARGS": str(args_file),
                    "EVAL_SIDECAR_LAUNCHER_PYTHON": sys.executable,
                    "CHILD_PID_FILE": str(child_pid_file),
                    "EVAL_SIDECAR_PID_FILE": str(pid_file),
                    "EVAL_SIDECAR_LOG": str(tmp_path / "logs" / "sidecar.log"),
                    "EVAL_SIDECAR_RUNS_DIR": str(tmp_path / "runs"),
                    "EVAL_SIDECAR_CURRENT_FILE": str(tmp_path / "current.txt"),
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
            self.assertIn("non-sidecar process; cleaning up", result.stdout)
            self.assertIn("eval-sidecar started", result.stdout)
            self.assertIsNone(process.poll())

    def test_removes_stale_pid_and_starts_sidecar_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "sidecar.pid"
            args_file = tmp_path / "python-args.txt"
            child_pid_file = tmp_path / "child.pid"
            python_script = tmp_path / "python.sh"
            pid_file.write_text("999999", encoding="utf-8")
            _write_executable(python_script, _sidecar_ready_python_stub())

            env = os.environ.copy()
            env.update(
                {
                    "PYTHON": str(python_script),
                    "PYTHON_ARGS": str(args_file),
                    "EVAL_SIDECAR_LAUNCHER_PYTHON": sys.executable,
                    "CHILD_PID_FILE": str(child_pid_file),
                    "EVAL_SIDECAR_PID_FILE": str(pid_file),
                    "EVAL_SIDECAR_LOG": str(tmp_path / "logs" / "sidecar.log"),
                    "EVAL_SIDECAR_TARGET": "quality-gate-deterministic",
                    "EVAL_SIDECAR_MIN_SECONDS": "42",
                    "EVAL_SIDECAR_RUNS_DIR": str(tmp_path / "runs"),
                    "EVAL_SIDECAR_CURRENT_FILE": str(tmp_path / "current.txt"),
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
            self.assertIn("eval-sidecar started", result.stdout)
            for _ in range(10):
                if args_file.exists() and child_pid_file.exists():
                    break
                time.sleep(0.05)
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "tools.eval_sidecar",
                    "run",
                    "--target",
                    "quality-gate-deterministic",
                    "--min-seconds",
                    "42",
                    "--runs-dir",
                    str(tmp_path / "runs"),
                    "--pid-file",
                    str(pid_file),
                    "--current-file",
                    str(tmp_path / "current.txt"),
                ],
            )
            self.assertTrue((tmp_path / "logs").is_dir())

    def test_status_reports_off_without_current_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "sidecar.pid"
            current_file = tmp_path / "current.txt"
            args_file = tmp_path / "python-args.txt"
            python_script = tmp_path / "python.sh"
            _write_executable(
                python_script,
                '#!/usr/bin/env sh\nset -eu\nprintf "%s\\n" "$@" > "$PYTHON_ARGS"\n',
            )

            env = os.environ.copy()
            env.update(
                {
                    "PYTHON": str(python_script),
                    "PYTHON_ARGS": str(args_file),
                    "EVAL_SIDECAR_PID_FILE": str(pid_file),
                    "EVAL_SIDECAR_CURRENT_FILE": str(current_file),
                }
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("eval-sidecar: OFF.", result.stdout)
            self.assertFalse(args_file.exists())

    def test_status_reports_stale_pid_file_without_current_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "sidecar.pid"
            current_file = tmp_path / "current.txt"
            pid_file.write_text("999999", encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "EVAL_SIDECAR_PID_FILE": str(pid_file),
                    "EVAL_SIDECAR_CURRENT_FILE": str(current_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("eval-sidecar: STALE PID file.", result.stdout)

    def test_status_reports_live_sidecar_without_current_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "sidecar.pid"
            current_file = tmp_path / "current.txt"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
            _write_sidecar_pid_fake(fake_bin)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": sys.executable,
                    "EXPECTED_PID": str(process.pid),
                    "EVAL_SIDECAR_PID_FILE": str(pid_file),
                    "EVAL_SIDECAR_CURRENT_FILE": str(current_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("eval-sidecar: RUNNING", result.stdout)
            self.assertIn("current file missing", result.stdout)

    def test_status_rejects_live_non_sidecar_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "sidecar.pid"
            current_file = tmp_path / "current.txt"
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "EVAL_SIDECAR_PID_FILE": str(pid_file),
                    "EVAL_SIDECAR_CURRENT_FILE": str(current_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("not a matching sidecar", result.stdout)
            self.assertTrue(pid_file.exists())
            self.assertIsNone(process.poll())

    def test_stop_is_noop_without_current_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "sidecar.pid"
            current_file = tmp_path / "current.txt"
            args_file = tmp_path / "python-args.txt"
            python_script = tmp_path / "python.sh"
            _write_executable(
                python_script,
                '#!/usr/bin/env sh\nset -eu\nprintf "%s\\n" "$@" > "$PYTHON_ARGS"\n',
            )

            env = os.environ.copy()
            env.update(
                {
                    "PYTHON": str(python_script),
                    "PYTHON_ARGS": str(args_file),
                    "EVAL_SIDECAR_PID_FILE": str(pid_file),
                    "EVAL_SIDECAR_CURRENT_FILE": str(current_file),
                }
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "stop"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("No eval-sidecar run found.", result.stdout)
            self.assertFalse(args_file.exists())

    def test_stop_cleans_up_live_pid_without_current_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "sidecar.pid"
            current_file = tmp_path / "current.txt"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
            _write_sidecar_pid_fake(fake_bin)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "stop"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": sys.executable,
                    "EXPECTED_PID": str(process.pid),
                    "EVAL_SIDECAR_PID_FILE": str(pid_file),
                    "EVAL_SIDECAR_CURRENT_FILE": str(current_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("eval-sidecar current file missing", result.stdout)
            self.assertIn("stopped managed PID", result.stdout)
            self.assertFalse(pid_file.exists())
            process.wait(timeout=2)

    def test_stop_preserves_pid_file_when_matching_sidecar_does_not_exit(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "sidecar.pid"
            current_file = tmp_path / "current.txt"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            process = subprocess.Popen(
                ["bash", "-c", "trap '' TERM; while :; do sleep 1; done"]
            )
            self.addCleanup(_terminate_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
            _write_sidecar_pid_fake(fake_bin)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "stop"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "PYTHON": sys.executable,
                    "EXPECTED_PID": str(process.pid),
                    "EVAL_SIDECAR_PID_FILE": str(pid_file),
                    "EVAL_SIDECAR_CURRENT_FILE": str(current_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("did not exit after stop signal", result.stdout)
            self.assertTrue(pid_file.exists())
            self.assertIsNone(process.poll())

    def test_stop_cleans_live_non_sidecar_pid_file_without_killing_process(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "sidecar.pid"
            current_file = tmp_path / "current.txt"
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "stop"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "EVAL_SIDECAR_PID_FILE": str(pid_file),
                    "EVAL_SIDECAR_CURRENT_FILE": str(current_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("non-sidecar process; cleaning up", result.stdout)
            self.assertFalse(pid_file.exists())
            self.assertIsNone(process.poll())

    def test_rejects_invalid_readiness_attempts_before_start(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
            cwd=REPO_ROOT,
            env={**os.environ, "EVAL_SIDECAR_START_ATTEMPTS": "abc"},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "EVAL_SIDECAR_START_ATTEMPTS must be a positive integer",
            result.stderr,
        )

    def test_rejects_invalid_readiness_sleep_before_start(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
            cwd=REPO_ROOT,
            env={**os.environ, "EVAL_SIDECAR_START_SLEEP_SECONDS": "-1"},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "EVAL_SIDECAR_START_SLEEP_SECONDS must be a non-negative decimal number",
            result.stderr,
        )

    def test_rejects_invalid_min_seconds_before_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "EVAL_SIDECAR_MIN_SECONDS": "0",
                    "EVAL_SIDECAR_PID_FILE": str(tmp_path / "sidecar.pid"),
                    "EVAL_SIDECAR_LOG": str(tmp_path / "sidecar.log"),
                    "EVAL_SIDECAR_RUNS_DIR": str(tmp_path / "runs"),
                    "EVAL_SIDECAR_CURRENT_FILE": str(tmp_path / "current.txt"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "EVAL_SIDECAR_MIN_SECONDS must be a positive integer",
                result.stderr,
            )
            self.assertFalse((tmp_path / "sidecar.pid").exists())

    def test_rejects_arguments(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "extra"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage: run_eval_sidecar_start.sh", result.stderr)


if __name__ == "__main__":
    unittest.main()
