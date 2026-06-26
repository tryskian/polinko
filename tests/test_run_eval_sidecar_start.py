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


class RunEvalSidecarStartTests(unittest.TestCase):
    def test_uses_existing_live_pid_without_starting_new_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "sidecar.pid"
            current_file = tmp_path / "current.txt"
            args_file = tmp_path / "python-args.txt"
            python_script = tmp_path / "python.sh"
            pid_file.write_text(str(os.getpid()), encoding="utf-8")
            current_file.write_text(str(tmp_path / "run"), encoding="utf-8")
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
            python_script = tmp_path / "python.sh"
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_terminate_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
            _write_executable(
                python_script,
                '#!/usr/bin/env sh\nset -eu\nprintf "%s\\n" "$@" > "$PYTHON_ARGS"\n',
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PYTHON": str(python_script),
                    "PYTHON_ARGS": str(args_file),
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

    def test_removes_stale_pid_and_starts_sidecar_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "sidecar.pid"
            args_file = tmp_path / "python-args.txt"
            child_pid_file = tmp_path / "child.pid"
            python_script = tmp_path / "python.sh"
            pid_file.write_text("999999", encoding="utf-8")
            _write_executable(
                python_script,
                (
                    "#!/usr/bin/env sh\n"
                    "set -eu\n"
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
                    "EVAL_SIDECAR_PID_FILE": str(pid_file),
                    "EVAL_SIDECAR_LOG": str(tmp_path / "logs" / "sidecar.log"),
                    "EVAL_SIDECAR_TARGET": "quality-gate-deterministic",
                    "EVAL_SIDECAR_MIN_SECONDS": "42",
                    "EVAL_SIDECAR_RUNS_DIR": str(tmp_path / "runs"),
                    "EVAL_SIDECAR_CURRENT_FILE": str(tmp_path / "current.txt"),
                    "EVAL_SIDECAR_LAUNCHER_PYTHON": sys.executable,
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
            self.assertIn("eval-sidecar current file missing", result.stdout)
            self.assertIn("stopped managed PID", result.stdout)
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
        self.assertIn("Usage: run_eval_sidecar_start.sh", result.stderr)


if __name__ == "__main__":
    unittest.main()
