import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "session_status.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class SessionStatusTests(unittest.TestCase):
    def test_reports_runner_status_targets_from_repo_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            make_script = tmp_path / "make"
            log_file = tmp_path / "make.log"
            _write_executable(
                make_script,
                (
                    "#!/usr/bin/env sh\n"
                    "set -eu\n"
                    'printf "pwd=%s args:" "$PWD" >> "$MAKE_LOG"\n'
                    'for arg in "$@"; do printf " <%s>" "$arg" >> "$MAKE_LOG"; done\n'
                    'printf "\\n" >> "$MAKE_LOG"\n'
                ),
            )

            env = os.environ.copy()
            env.update({"MAKE": str(make_script), "MAKE_LOG": str(log_file)})

            result = subprocess.run(
                ["bash", str(SCRIPT)],
                cwd=REPO_ROOT / "docs",
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                log_file.read_text(encoding="utf-8").splitlines(),
                [
                    f"pwd={REPO_ROOT} args: <--no-print-directory> "
                    "<server-daemon-status>",
                    f"pwd={REPO_ROOT} args: <--no-print-directory> "
                    "<eval-sidecar-status>",
                    f"pwd={REPO_ROOT} args: <--no-print-directory> <caffeinate-status>",
                ],
            )
            self.assertIn("== Server ==", result.stdout)
            self.assertIn("== Eval sidecar ==", result.stdout)
            self.assertIn("== Keep-awake ==", result.stdout)

    def test_reports_missing_make_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing_make = Path(tmp) / "missing-make"
            env = os.environ.copy()
            env["MAKE"] = str(missing_make)

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT))],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn(
                f"session-status: missing make command: {missing_make}",
                result.stderr,
            )


if __name__ == "__main__":
    unittest.main()
