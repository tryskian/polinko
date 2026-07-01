import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "ensure_eval_server_daemon.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class EnsureEvalServerDaemonTests(unittest.TestCase):
    def test_delegates_to_make_server_daemon_from_repo_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            make_script = tmp_path / "make"
            args_file = tmp_path / "make-args.txt"
            cwd_file = tmp_path / "make-cwd.txt"
            _write_executable(
                make_script,
                (
                    "#!/usr/bin/env sh\n"
                    "set -eu\n"
                    'printf "%s\\n" "$PWD" > "$MAKE_CWD"\n'
                    'printf "%s\\n" "$@" > "$MAKE_ARGS"\n'
                ),
            )

            env = os.environ.copy()
            env.update(
                {
                    "MAKE": str(make_script),
                    "MAKE_ARGS": str(args_file),
                    "MAKE_CWD": str(cwd_file),
                }
            )

            result = subprocess.run(
                ["bash", "../tools/ensure_eval_server_daemon.sh"],
                cwd=REPO_ROOT / "docs",
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                cwd_file.read_text(encoding="utf-8").strip(), str(REPO_ROOT)
            )
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                ["--no-print-directory", "server-daemon"],
            )

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
                f"ensure-eval-server-daemon: missing make command: {missing_make}",
                result.stderr,
            )


if __name__ == "__main__":
    unittest.main()
