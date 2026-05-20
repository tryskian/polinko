import os
import signal
import stat
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "manage_caffeinate.sh"


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


class ManageCaffeinateTests(unittest.TestCase):
    def test_start_skips_on_non_macos(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Linux\n")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={**os.environ, "UNAME_BIN": str(uname_script)},
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("caffeinate is macOS-only; skipping.", result.stdout)

    def test_start_uses_existing_live_pid_without_spawning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pid_file = tmp_path / "caffeinate.pid"
            marker_file = tmp_path / "started.txt"
            fake_caffeinate = tmp_path / "fake-caffeinate.sh"
            pid_file.write_text(str(os.getpid()), encoding="utf-8")
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            _write_executable(
                fake_caffeinate,
                ('#!/usr/bin/env sh\nset -eu\nprintf started > "$MARKER_FILE"\n'),
            )

            env = os.environ.copy()
            env.update(
                {
                    "UNAME_BIN": str(uname_script),
                    "CAFFEINATE_PID_FILE": str(pid_file),
                    "CAFFEINATE_LOG": str(tmp_path / "caffeinate.log"),
                    "CAFFEINATE_CMD": str(fake_caffeinate),
                    "MARKER_FILE": str(marker_file),
                }
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("caffeinate already running", result.stdout)
            self.assertFalse(marker_file.exists())

    def test_start_removes_stale_pid_and_starts_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pid_file = tmp_path / "caffeinate.pid"
            child_pid_file = tmp_path / "child.pid"
            fake_caffeinate = tmp_path / "fake-caffeinate.sh"
            pid_file.write_text("999999", encoding="utf-8")
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            _write_executable(
                fake_caffeinate,
                (
                    "#!/usr/bin/env sh\n"
                    "set -eu\n"
                    'printf "%s" "$$" > "$CHILD_PID_FILE"\n'
                    "sleep 30\n"
                ),
            )

            env = os.environ.copy()
            env.update(
                {
                    "UNAME_BIN": str(uname_script),
                    "CHILD_PID_FILE": str(child_pid_file),
                    "CAFFEINATE_PID_FILE": str(pid_file),
                    "CAFFEINATE_LOG": str(tmp_path / "logs" / "caffeinate.log"),
                    "CAFFEINATE_CMD": str(fake_caffeinate),
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
            self.assertIn("caffeinate started", result.stdout)
            for _ in range(10):
                if child_pid_file.exists():
                    break
                time.sleep(0.05)
            self.assertEqual(
                pid_file.read_text(encoding="utf-8").strip(),
                child_pid_file.read_text(encoding="utf-8").strip(),
            )
            self.assertTrue((tmp_path / "logs").is_dir())

    def test_stop_kills_managed_pid_and_removes_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pid_file = tmp_path / "caffeinate.pid"
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(process.kill)
            pid_file.write_text(str(process.pid), encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "stop"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "UNAME_BIN": str(uname_script),
                    "CAFFEINATE_PID_FILE": str(pid_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("caffeinate stopped", result.stdout)
            self.assertFalse(pid_file.exists())
            process.wait(timeout=2)

    def test_stop_all_kills_matching_pids_and_removes_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pgrep_script = tmp_path / "pgrep.sh"
            pid_file = tmp_path / "caffeinate.pid"
            first = subprocess.Popen(["sleep", "30"])
            second = subprocess.Popen(["sleep", "30"])
            self.addCleanup(first.kill)
            self.addCleanup(second.kill)
            pid_file.write_text("999999", encoding="utf-8")
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            _write_executable(
                pgrep_script,
                (
                    "#!/usr/bin/env sh\n"
                    "set -eu\n"
                    'printf "%s\\n%s\\n" "$FIRST_PID" "$SECOND_PID"\n'
                ),
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "stop-all"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "UNAME_BIN": str(uname_script),
                    "PGREP_BIN": str(pgrep_script),
                    "FIRST_PID": str(first.pid),
                    "SECOND_PID": str(second.pid),
                    "CAFFEINATE_PID_FILE": str(pid_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Stopped matching caffeinate processes", result.stdout)
            self.assertFalse(pid_file.exists())
            first.wait(timeout=2)
            second.wait(timeout=2)

    def test_status_reports_unmanaged_pid_and_pmset_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pgrep_script = tmp_path / "pgrep.sh"
            pmset_script = tmp_path / "pmset.sh"
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            _write_executable(pgrep_script, "#!/usr/bin/env sh\nprintf '12345\\n'\n")
            _write_executable(
                pmset_script,
                (
                    "#!/usr/bin/env sh\n"
                    "set -eu\n"
                    "printf 'PreventUserIdleSystemSleep 1\\n'\n"
                ),
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "UNAME_BIN": str(uname_script),
                    "PGREP_BIN": str(pgrep_script),
                    "PMSET_BIN": str(pmset_script),
                    "CAFFEINATE_PID_FILE": str(tmp_path / "missing.pid"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Managed caffeinate: OFF.", result.stdout)
            self.assertIn("Unmanaged caffeinate detected (PID 12345)", result.stdout)
            self.assertIn("PreventUserIdleSystemSleep", result.stdout)

    def test_rejects_unknown_action(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "unknown"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage: manage_caffeinate.sh", result.stderr)


if __name__ == "__main__":
    unittest.main()
