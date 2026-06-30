import json
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


def _cleanup_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=2)


def _write_metadata(meta_file: Path, pid: int, repo_root: Path = REPO_ROOT) -> None:
    meta_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "runner": "caffeinate",
                "repo_slug": "polinko",
                "repo_root": str(repo_root),
                "branch": "test",
                "commit": "test",
                "pid": pid,
                "command": "test command",
                "match_pattern": "test",
                "started_at": "2026-06-27T00:00:00Z",
                "pid_file": "test.pid",
                "log_file": "test.log",
            }
        ),
        encoding="utf-8",
    )


class ManageCaffeinateTests(unittest.TestCase):
    def test_activity_writes_repo_activity_without_pid_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pid_file = tmp_path / "caffeinate.pid"
            meta_file = tmp_path / "caffeinate.meta.json"
            activity_file = tmp_path / "caffeinate.activity.json"

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "activity"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "CAFFEINATE_PID_FILE": str(pid_file),
                    "CAFFEINATE_META_FILE": str(meta_file),
                    "CAFFEINATE_ACTIVITY_FILE": str(activity_file),
                    "CAFFEINATE_ACTIVITY_LABEL": "make test",
                    "CAFFEINATE_ACTIVITY_TARGET": "test",
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertFalse(pid_file.exists())
            self.assertFalse(meta_file.exists())
            activity = json.loads(activity_file.read_text(encoding="utf-8"))
            self.assertEqual(activity["repo_slug"], "polinko")
            self.assertEqual(activity["repo_root"], str(REPO_ROOT))
            self.assertEqual(activity["last_activity_label"], "make test")
            self.assertEqual(activity["last_activity_target"], "test")

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

    def test_rejects_invalid_active_window_seconds(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "activity"],
            cwd=REPO_ROOT,
            env={**os.environ, "CAFFEINATE_ACTIVE_WINDOW_SECONDS": "0"},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("caffeinate config error", result.stderr)
        self.assertIn("CAFFEINATE_ACTIVE_WINDOW_SECONDS", result.stderr)

    def test_rejects_invalid_global_cleanup_flag(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "activity"],
            cwd=REPO_ROOT,
            env={**os.environ, "CAFFEINATE_ALLOW_GLOBAL_CLEANUP": "maybe"},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("caffeinate config error", result.stderr)
        self.assertIn("CAFFEINATE_ALLOW_GLOBAL_CLEANUP", result.stderr)

    def test_rejects_empty_caffeinate_command(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "activity"],
            cwd=REPO_ROOT,
            env={**os.environ, "CAFFEINATE_CMD": "  "},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("caffeinate config error", result.stderr)
        self.assertIn("CAFFEINATE_CMD", result.stderr)

    def test_rejects_invalid_match_pattern(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "activity"],
            cwd=REPO_ROOT,
            env={**os.environ, "CAFFEINATE_MATCH_PATTERN": "["},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("caffeinate config error", result.stderr)
        self.assertIn("CAFFEINATE_MATCH_PATTERN", result.stderr)

    def test_rejects_invalid_launcher_python_before_manager_exec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            activity_file = tmp_path / "caffeinate.activity.json"

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "activity"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "CAFFEINATE_LAUNCHER_PYTHON": str(tmp_path / "missing-python"),
                    "CAFFEINATE_ACTIVITY_FILE": str(activity_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("Configured CAFFEINATE_LAUNCHER_PYTHON", result.stderr)
            self.assertFalse(activity_file.exists())

    def test_start_rejects_missing_ps_before_pid_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pid_file = tmp_path / "caffeinate.pid"
            meta_file = tmp_path / "caffeinate.meta.json"
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            pid_file.write_text("999999", encoding="utf-8")
            meta_file.write_text("{}", encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "UNAME_BIN": str(uname_script),
                    "PS_BIN": str(tmp_path / "missing-ps"),
                    "CAFFEINATE_PID_FILE": str(pid_file),
                    "CAFFEINATE_META_FILE": str(meta_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("PS_BIN command not found", result.stderr)
            self.assertTrue(pid_file.exists())
            self.assertTrue(meta_file.exists())

    def test_status_rejects_missing_ps_before_pid_classification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pid_file = tmp_path / "caffeinate.pid"
            meta_file = tmp_path / "caffeinate.meta.json"
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_cleanup_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
            _write_metadata(meta_file, process.pid)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "UNAME_BIN": str(uname_script),
                    "PS_BIN": str(tmp_path / "missing-ps"),
                    "CAFFEINATE_PID_FILE": str(pid_file),
                    "CAFFEINATE_META_FILE": str(meta_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("PS_BIN command not found", result.stderr)
            self.assertEqual(
                pid_file.read_text(encoding="utf-8").strip(), str(process.pid)
            )
            self.assertTrue(meta_file.exists())

    def test_start_cleans_live_non_owned_pid_without_killing_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pid_file = tmp_path / "caffeinate.pid"
            meta_file = tmp_path / "caffeinate.meta.json"
            activity_file = tmp_path / "caffeinate.activity.json"
            child_pid_file = tmp_path / "child.pid"
            fake_caffeinate = tmp_path / "fake-caffeinate.sh"
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_cleanup_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
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
                    "CAFFEINATE_META_FILE": str(meta_file),
                    "CAFFEINATE_ACTIVITY_FILE": str(activity_file),
                    "CAFFEINATE_LOG": str(tmp_path / "caffeinate.log"),
                    "CAFFEINATE_CMD": str(fake_caffeinate),
                    "CAFFEINATE_MATCH_PATTERN": str(fake_caffeinate),
                    "PMSET_BIN": str(tmp_path / "missing-pmset"),
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
            self.assertIn("Cleaned non-owned caffeinate PID reference", result.stdout)
            self.assertIn("caffeinate started", result.stdout)
            self.assertIsNone(process.poll())
            self.assertTrue(meta_file.exists())
            self.assertTrue(activity_file.exists())

    def test_start_refreshes_legacy_matching_pid_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pid_file = tmp_path / "caffeinate.pid"
            meta_file = tmp_path / "caffeinate.meta.json"
            activity_file = tmp_path / "caffeinate.activity.json"
            fake_caffeinate = tmp_path / "fake-caffeinate.sh"
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            _write_executable(fake_caffeinate, "#!/usr/bin/env sh\nsleep 30\n")
            process = subprocess.Popen([str(fake_caffeinate)])
            self.addCleanup(_cleanup_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "UNAME_BIN": str(uname_script),
                    "CAFFEINATE_PID_FILE": str(pid_file),
                    "CAFFEINATE_META_FILE": str(meta_file),
                    "CAFFEINATE_ACTIVITY_FILE": str(activity_file),
                    "CAFFEINATE_CMD": str(fake_caffeinate),
                    "CAFFEINATE_MATCH_PATTERN": str(fake_caffeinate),
                    "PMSET_BIN": str(tmp_path / "missing-pmset"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("metadata refreshed", result.stdout)
            self.assertEqual(
                json.loads(meta_file.read_text(encoding="utf-8"))["pid"], process.pid
            )
            self.assertTrue(activity_file.exists())

    def test_start_migrates_flat_runtime_files_without_duplicate_launch(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            state_dir = tmp_path / "state" / "polinko"
            pid_file = state_dir / "caffeinate.pid"
            log_file = state_dir / "caffeinate.log"
            meta_file = state_dir / "caffeinate.meta.json"
            activity_file = state_dir / "activity.meta.json"
            legacy_pid_file = tmp_path / "polinko-caffeinate.pid"
            legacy_log_file = tmp_path / "polinko-caffeinate.log"
            legacy_meta_file = tmp_path / "polinko-caffeinate.meta.json"
            legacy_activity_file = tmp_path / "polinko-caffeinate.activity.json"
            fake_caffeinate = tmp_path / "fake-caffeinate.sh"
            launcher_marker = tmp_path / "launcher-called"
            detached_launcher = tmp_path / "launch-detached.py"

            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            _write_executable(fake_caffeinate, "#!/usr/bin/env sh\nsleep 30\n")
            detached_launcher.write_text(
                (
                    "from pathlib import Path\n"
                    f"Path({str(launcher_marker)!r}).write_text('called')\n"
                    "raise SystemExit(1)\n"
                ),
                encoding="utf-8",
            )
            process = subprocess.Popen([str(fake_caffeinate)])
            self.addCleanup(_cleanup_process, process)
            legacy_pid_file.write_text(str(process.pid), encoding="utf-8")
            legacy_log_file.write_text("legacy log\n", encoding="utf-8")
            legacy_activity_file.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "repo_slug": "polinko",
                        "repo_root": str(REPO_ROOT),
                        "branch": "test",
                        "commit": "test",
                        "last_activity_at": "2026-06-27T00:00:00Z",
                        "last_activity_label": "make test",
                        "last_activity_target": "test",
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "UNAME_BIN": str(uname_script),
                    "CAFFEINATE_PID_FILE": str(pid_file),
                    "CAFFEINATE_LOG": str(log_file),
                    "CAFFEINATE_META_FILE": str(meta_file),
                    "CAFFEINATE_ACTIVITY_FILE": str(activity_file),
                    "CAFFEINATE_LEGACY_PID_FILE": str(legacy_pid_file),
                    "CAFFEINATE_LEGACY_LOG": str(legacy_log_file),
                    "CAFFEINATE_LEGACY_META_FILE": str(legacy_meta_file),
                    "CAFFEINATE_LEGACY_ACTIVITY_FILE": str(legacy_activity_file),
                    "CAFFEINATE_DETACHED_LAUNCHER": str(detached_launcher),
                    "CAFFEINATE_CMD": str(fake_caffeinate),
                    "CAFFEINATE_MATCH_PATTERN": str(fake_caffeinate),
                    "PMSET_BIN": str(tmp_path / "missing-pmset"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Migrated flat caffeinate runtime files", result.stdout)
            self.assertIn("caffeinate already running", result.stdout)
            self.assertFalse(launcher_marker.exists())
            self.assertFalse(legacy_pid_file.exists())
            self.assertTrue(pid_file.exists())
            self.assertEqual(
                pid_file.read_text(encoding="utf-8").strip(), str(process.pid)
            )
            self.assertFalse(legacy_log_file.exists())
            self.assertEqual(log_file.read_text(encoding="utf-8"), "legacy log\n")
            self.assertFalse(legacy_activity_file.exists())
            self.assertTrue(activity_file.exists())
            metadata = json.loads(meta_file.read_text(encoding="utf-8"))
            self.assertEqual(metadata["pid"], process.pid)
            self.assertEqual(metadata["pid_file"], str(pid_file))

    def test_start_finds_default_flat_tmp_runtime_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            slug = f"polinko-test-{os.getpid()}-{time.time_ns()}"
            uname_script = tmp_path / "uname.sh"
            state_dir = tmp_path / "state" / slug
            pid_file = state_dir / "caffeinate.pid"
            meta_file = state_dir / "caffeinate.meta.json"
            activity_file = state_dir / "activity.meta.json"
            legacy_pid_file = Path("/tmp") / f"{slug}-caffeinate.pid"
            legacy_log_file = Path("/tmp") / f"{slug}-caffeinate.log"
            legacy_meta_file = Path("/tmp") / f"{slug}-caffeinate.meta.json"
            legacy_activity_file = Path("/tmp") / f"{slug}-caffeinate.activity.json"
            fake_caffeinate = tmp_path / "fake-caffeinate.sh"
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            _write_executable(fake_caffeinate, "#!/usr/bin/env sh\nsleep 30\n")
            process = subprocess.Popen([str(fake_caffeinate)])
            self.addCleanup(_cleanup_process, process)
            self.addCleanup(_kill_pid_file, pid_file)
            for path in (
                legacy_pid_file,
                legacy_log_file,
                legacy_meta_file,
                legacy_activity_file,
            ):
                self.addCleanup(lambda p=path: p.unlink(missing_ok=True))
            legacy_pid_file.write_text(str(process.pid), encoding="utf-8")
            legacy_log_file.write_text("legacy log\n", encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "UNAME_BIN": str(uname_script),
                    "CAFFEINATE_REPO_SLUG": slug,
                    "CAFFEINATE_PID_FILE": str(pid_file),
                    "CAFFEINATE_META_FILE": str(meta_file),
                    "CAFFEINATE_ACTIVITY_FILE": str(activity_file),
                    "CAFFEINATE_CMD": str(fake_caffeinate),
                    "CAFFEINATE_MATCH_PATTERN": str(fake_caffeinate),
                    "PMSET_BIN": str(tmp_path / "missing-pmset"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Migrated flat caffeinate runtime files", result.stdout)
            self.assertFalse(legacy_pid_file.exists())
            self.assertTrue(pid_file.exists())
            self.assertEqual(
                pid_file.read_text(encoding="utf-8").strip(), str(process.pid)
            )

    def test_start_cleans_orphaned_flat_runtime_metadata_before_launch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pid_file = tmp_path / "state" / "polinko" / "caffeinate.pid"
            legacy_pid_file = tmp_path / "polinko-caffeinate.pid"
            legacy_meta_file = tmp_path / "polinko-caffeinate.meta.json"
            child_pid_file = tmp_path / "child.pid"
            fake_caffeinate = tmp_path / "fake-caffeinate.sh"
            legacy_pid_file.write_text("999999", encoding="utf-8")
            legacy_meta_file.write_text("{}", encoding="utf-8")
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

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "start"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "UNAME_BIN": str(uname_script),
                    "CHILD_PID_FILE": str(child_pid_file),
                    "CAFFEINATE_PID_FILE": str(pid_file),
                    "CAFFEINATE_LEGACY_PID_FILE": str(legacy_pid_file),
                    "CAFFEINATE_LEGACY_META_FILE": str(legacy_meta_file),
                    "CAFFEINATE_CMD": str(fake_caffeinate),
                    "CAFFEINATE_MATCH_PATTERN": str(fake_caffeinate),
                    "PMSET_BIN": str(tmp_path / "missing-pmset"),
                },
                capture_output=True,
                text=True,
            )

            self.addCleanup(_kill_pid_file, pid_file)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(
                "Cleaned orphaned flat caffeinate PID metadata", result.stdout
            )
            self.assertIn("caffeinate started", result.stdout)
            self.assertFalse(legacy_pid_file.exists())
            self.assertFalse(legacy_meta_file.exists())

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
                    "CAFFEINATE_MATCH_PATTERN": str(fake_caffeinate),
                    "PMSET_BIN": str(tmp_path / "missing-pmset"),
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

    def test_stop_kills_owned_pid_and_removes_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pid_file = tmp_path / "caffeinate.pid"
            meta_file = tmp_path / "caffeinate.meta.json"
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_cleanup_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
            _write_metadata(meta_file, process.pid)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "stop"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "UNAME_BIN": str(uname_script),
                    "CAFFEINATE_PID_FILE": str(pid_file),
                    "CAFFEINATE_META_FILE": str(meta_file),
                    "CAFFEINATE_MATCH_PATTERN": "sleep 30",
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("caffeinate stopped", result.stdout)
            self.assertFalse(pid_file.exists())
            self.assertFalse(meta_file.exists())
            process.wait(timeout=2)

    def test_stop_kills_owned_pid_that_ignores_term(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            ps_script = tmp_path / "ps.sh"
            pid_file = tmp_path / "caffeinate.pid"
            meta_file = tmp_path / "caffeinate.meta.json"
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            _write_executable(
                ps_script,
                """#!/usr/bin/env sh
set -eu
case "$*" in
\t*"command="*) printf "managed-caffeinate\\n" ;;
\t*"stat="*) exec /bin/ps "$@" ;;
esac
""",
            )
            process = subprocess.Popen(
                ["bash", "-c", "trap '' TERM; while :; do sleep 1; done"]
            )
            self.addCleanup(_cleanup_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
            _write_metadata(meta_file, process.pid)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "stop"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "UNAME_BIN": str(uname_script),
                    "PS_BIN": str(ps_script),
                    "CAFFEINATE_PID_FILE": str(pid_file),
                    "CAFFEINATE_META_FILE": str(meta_file),
                    "CAFFEINATE_MATCH_PATTERN": "managed-caffeinate",
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("caffeinate stopped", result.stdout)
            self.assertFalse(pid_file.exists())
            self.assertFalse(meta_file.exists())
            process.wait(timeout=2)

    def test_stop_cleans_non_owned_pid_reference_without_killing_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pid_file = tmp_path / "caffeinate.pid"
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_cleanup_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "stop"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "UNAME_BIN": str(uname_script),
                    "CAFFEINATE_PID_FILE": str(pid_file),
                    "CAFFEINATE_MATCH_PATTERN": str(tmp_path / "fake-caffeinate.sh"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Cleaned non-owned caffeinate PID reference", result.stdout)
            self.assertFalse(pid_file.exists())
            self.assertIsNone(process.poll())

    def test_stop_all_is_repo_scoped_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pgrep_script = tmp_path / "pgrep.sh"
            pid_file = tmp_path / "caffeinate.pid"
            first = subprocess.Popen(["sleep", "30"])
            second = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_cleanup_process, first)
            self.addCleanup(_cleanup_process, second)
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
            self.assertIn("Current repo caffeinate cleanup complete", result.stdout)
            self.assertIn("Global caffeinate cleanup skipped", result.stdout)
            self.assertFalse(pid_file.exists())
            self.assertIsNone(first.poll())
            self.assertIsNone(second.poll())

    def test_stop_all_global_cleanup_requires_explicit_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pgrep_script = tmp_path / "pgrep.sh"
            first = subprocess.Popen(["sleep", "30"])
            second = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_cleanup_process, first)
            self.addCleanup(_cleanup_process, second)
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
                    "CAFFEINATE_PID_FILE": str(tmp_path / "missing.pid"),
                    "CAFFEINATE_ALLOW_GLOBAL_CLEANUP": "1",
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Stopped matching caffeinate processes", result.stdout)
            first.wait(timeout=2)
            second.wait(timeout=2)

    def test_status_reports_unmanaged_pid_and_pmset_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pgrep_script = tmp_path / "pgrep.sh"
            pmset_script = tmp_path / "pmset.sh"
            activity_file = tmp_path / "caffeinate.activity.json"
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
            activity_file.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "repo_slug": "polinko",
                        "repo_root": str(REPO_ROOT),
                        "branch": "test",
                        "commit": "test",
                        "last_activity_at": "2026-06-27T00:00:00Z",
                        "last_activity_label": "make test",
                        "last_activity_target": "test",
                    }
                ),
                encoding="utf-8",
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
                    "CAFFEINATE_ACTIVITY_FILE": str(activity_file),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Managed caffeinate: OFF", result.stdout)
            self.assertIn(f"Repo root: {REPO_ROOT}", result.stdout)
            self.assertIn("Last repo activity:", result.stdout)
            self.assertIn("via make test", result.stdout)
            self.assertIn("Unmanaged caffeinate detected (PID 12345)", result.stdout)
            self.assertIn("PreventUserIdleSystemSleep", result.stdout)

    def test_status_reports_quiet_for_owned_pid_without_recent_activity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            pid_file = tmp_path / "caffeinate.pid"
            meta_file = tmp_path / "caffeinate.meta.json"
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_cleanup_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
            _write_metadata(meta_file, process.pid)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "UNAME_BIN": str(uname_script),
                    "CAFFEINATE_PID_FILE": str(pid_file),
                    "CAFFEINATE_META_FILE": str(meta_file),
                    "CAFFEINATE_MATCH_PATTERN": "sleep 30",
                    "PMSET_BIN": str(tmp_path / "missing-pmset"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Managed caffeinate: QUIET", result.stdout)
            self.assertIn(f"Repo root: {REPO_ROOT}", result.stdout)
            self.assertIn("no recorded repo activity", result.stdout)

    def test_status_treats_zombie_pid_file_as_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            uname_script = tmp_path / "uname.sh"
            ps_script = tmp_path / "ps.sh"
            pid_file = tmp_path / "caffeinate.pid"
            meta_file = tmp_path / "caffeinate.meta.json"
            _write_executable(uname_script, "#!/usr/bin/env sh\nprintf Darwin\n")
            _write_executable(
                ps_script,
                """#!/usr/bin/env sh
set -eu
case "$*" in
\t*"command="*) printf "managed-caffeinate\\n" ;;
\t*"stat="*) printf "Z\\n" ;;
esac
""",
            )
            process = subprocess.Popen(["sleep", "30"])
            self.addCleanup(_cleanup_process, process)
            pid_file.write_text(str(process.pid), encoding="utf-8")
            _write_metadata(meta_file, process.pid)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "status"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "UNAME_BIN": str(uname_script),
                    "PS_BIN": str(ps_script),
                    "CAFFEINATE_PID_FILE": str(pid_file),
                    "CAFFEINATE_META_FILE": str(meta_file),
                    "CAFFEINATE_MATCH_PATTERN": "managed-caffeinate",
                    "PMSET_BIN": str(tmp_path / "missing-pmset"),
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("Managed caffeinate: STALE", result.stdout)
            self.assertIn("PID is not live", result.stdout)

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
