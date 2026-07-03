import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "pwcli_daily.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _symlink_required_command(bin_dir: Path, command: str) -> None:
    command_path = shutil.which(command)
    if command_path is None:
        raise AssertionError(f"required test command not found: {command}")
    os.symlink(command_path, bin_dir / command)


class PwcliDailyTests(unittest.TestCase):
    def test_print_dir_uses_configured_snapshot_root_and_day(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            snapshot_base = tmp_path / "snapshots"

            result = subprocess.run(
                ["/bin/bash", str(SCRIPT.relative_to(REPO_ROOT)), "--print-dir"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PLAYWRIGHT_SNAPSHOT_BASE_DIR": str(snapshot_base),
                    "PLAYWRIGHT_SNAPSHOT_DAY": "23-06-26",
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), str(snapshot_base / "23-06-26"))
            self.assertTrue((snapshot_base / "23-06-26").is_dir())

    def test_reports_blocked_snapshot_directory_before_print_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            blocked_parent = tmp_path / "blocked-parent"
            blocked_parent.write_text("not a directory", encoding="utf-8")

            result = subprocess.run(
                ["/bin/bash", str(SCRIPT.relative_to(REPO_ROOT)), "--print-dir"],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PLAYWRIGHT_SNAPSHOT_BASE_DIR": str(blocked_parent / "snapshots"),
                    "PLAYWRIGHT_SNAPSHOT_DAY": "23-06-26",
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "pwcli-daily failed to prepare snapshot directory: "
                f"{blocked_parent / 'snapshots' / '23-06-26'}",
                result.stderr,
            )
            self.assertEqual(result.stdout, "")

    def test_missing_npx_uses_shared_command_prerequisite_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bin_dir = tmp_path / "bin"
            bin_dir.mkdir()
            _symlink_required_command(bin_dir, "dirname")
            _symlink_required_command(bin_dir, "mkdir")

            result = subprocess.run(
                [
                    "/bin/bash",
                    str(SCRIPT.relative_to(REPO_ROOT)),
                    "snapshot",
                    "http://127.0.0.1:8000/",
                ],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": str(bin_dir),
                    "PLAYWRIGHT_SNAPSHOT_BASE_DIR": str(tmp_path / "snapshots"),
                    "PLAYWRIGHT_SNAPSHOT_DAY": "23-06-26",
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("pwcli-daily: missing npx command: npx", result.stderr)

    def test_screenshot_injects_default_session_and_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bin_dir = tmp_path / "bin"
            bin_dir.mkdir()
            npx = bin_dir / "npx"
            pwcli = tmp_path / "playwright_cli.sh"
            args_file = tmp_path / "args.txt"
            snapshot_base = tmp_path / "snapshots"
            _write_executable(npx, "#!/usr/bin/env sh\nset -eu\nexit 0\n")
            _write_executable(
                pwcli,
                '#!/usr/bin/env sh\nset -eu\nprintf "%s\\n" "$@" > "$PWCLI_ARGS_FILE"\n',
            )

            result = subprocess.run(
                [
                    "/bin/bash",
                    str(SCRIPT.relative_to(REPO_ROOT)),
                    "screenshot",
                    "http://127.0.0.1:8000/",
                ],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                    "PWCLI": str(pwcli),
                    "PWCLI_ARGS_FILE": str(args_file),
                    "PLAYWRIGHT_SESSION": "daily",
                    "PLAYWRIGHT_SNAPSHOT_BASE_DIR": str(snapshot_base),
                    "PLAYWRIGHT_SNAPSHOT_DAY": "23-06-26",
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(
                f"Playwright snapshot directory: {snapshot_base / '23-06-26'}",
                result.stderr,
            )
            args = args_file.read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                args[:4], ["--session", "daily", "screenshot", "http://127.0.0.1:8000/"]
            )
            self.assertEqual(args[-2], "--filename")
            self.assertTrue(
                args[-1].startswith(str(snapshot_base / "23-06-26" / "screenshot-"))
            )
            self.assertTrue(args[-1].endswith(".png"))

    def test_capture_command_detection_skips_preceding_option_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bin_dir = tmp_path / "bin"
            bin_dir.mkdir()
            npx = bin_dir / "npx"
            pwcli = tmp_path / "playwright_cli.sh"
            args_file = tmp_path / "args.txt"
            snapshot_base = tmp_path / "snapshots"
            _write_executable(npx, "#!/usr/bin/env sh\nset -eu\nexit 0\n")
            _write_executable(
                pwcli,
                '#!/usr/bin/env sh\nset -eu\nprintf "%s\\n" "$@" > "$PWCLI_ARGS_FILE"\n',
            )

            result = subprocess.run(
                [
                    "/bin/bash",
                    str(SCRIPT.relative_to(REPO_ROOT)),
                    "--viewport",
                    "1280,720",
                    "screenshot",
                    "http://127.0.0.1:8000/",
                ],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                    "PWCLI": str(pwcli),
                    "PWCLI_ARGS_FILE": str(args_file),
                    "PLAYWRIGHT_SESSION": "daily",
                    "PLAYWRIGHT_SNAPSHOT_BASE_DIR": str(snapshot_base),
                    "PLAYWRIGHT_SNAPSHOT_DAY": "23-06-26",
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            args = args_file.read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                args[:6],
                [
                    "--session",
                    "daily",
                    "--viewport",
                    "1280,720",
                    "screenshot",
                    "http://127.0.0.1:8000/",
                ],
            )
            self.assertEqual(args[-2], "--filename")
            self.assertTrue(
                args[-1].startswith(str(snapshot_base / "23-06-26" / "screenshot-"))
            )
            self.assertTrue(args[-1].endswith(".png"))

    def test_explicit_session_and_filename_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bin_dir = tmp_path / "bin"
            bin_dir.mkdir()
            npx = bin_dir / "npx"
            pwcli = tmp_path / "playwright_cli.sh"
            args_file = tmp_path / "args.txt"
            output_file = tmp_path / "manual.png"
            _write_executable(npx, "#!/usr/bin/env sh\nset -eu\nexit 0\n")
            _write_executable(
                pwcli,
                '#!/usr/bin/env sh\nset -eu\nprintf "%s\\n" "$@" > "$PWCLI_ARGS_FILE"\n',
            )

            result = subprocess.run(
                [
                    "/bin/bash",
                    str(SCRIPT.relative_to(REPO_ROOT)),
                    "--session",
                    "custom",
                    "screenshot",
                    "http://127.0.0.1:8000/",
                    "--filename",
                    str(output_file),
                ],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                    "PWCLI": str(pwcli),
                    "PWCLI_ARGS_FILE": str(args_file),
                    "PLAYWRIGHT_SNAPSHOT_BASE_DIR": str(tmp_path / "snapshots"),
                    "PLAYWRIGHT_SNAPSHOT_DAY": "23-06-26",
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                [
                    "--session",
                    "custom",
                    "screenshot",
                    "http://127.0.0.1:8000/",
                    "--filename",
                    str(output_file),
                ],
            )

    def test_configured_snapshot_stamp_is_used_for_default_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bin_dir = tmp_path / "bin"
            bin_dir.mkdir()
            npx = bin_dir / "npx"
            pwcli = tmp_path / "playwright_cli.sh"
            args_file = tmp_path / "args.txt"
            snapshot_base = tmp_path / "snapshots"
            _write_executable(npx, "#!/usr/bin/env sh\nset -eu\nexit 0\n")
            _write_executable(
                pwcli,
                '#!/usr/bin/env sh\nset -eu\nprintf "%s\\n" "$@" > "$PWCLI_ARGS_FILE"\n',
            )

            result = subprocess.run(
                [
                    "/bin/bash",
                    str(SCRIPT.relative_to(REPO_ROOT)),
                    "snapshot",
                    "http://127.0.0.1:8000/",
                ],
                cwd=REPO_ROOT,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                    "PWCLI": str(pwcli),
                    "PWCLI_ARGS_FILE": str(args_file),
                    "PLAYWRIGHT_SESSION": "daily",
                    "PLAYWRIGHT_SNAPSHOT_BASE_DIR": str(snapshot_base),
                    "PLAYWRIGHT_SNAPSHOT_DAY": "23-06-26",
                    "PLAYWRIGHT_SNAPSHOT_STAMP": "fixed-capture",
                },
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            args = args_file.read_text(encoding="utf-8").splitlines()
            self.assertEqual(args[-2], "--filename")
            self.assertEqual(
                args[-1], str(snapshot_base / "23-06-26" / "snapshot-fixed-capture.md")
            )
