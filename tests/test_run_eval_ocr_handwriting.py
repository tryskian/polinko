import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "run_eval_ocr_handwriting.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class RunEvalOcrHandwritingTests(unittest.TestCase):
    def test_run_mode_builds_strict_handwriting_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "handwriting.json"
            server_marker = tmp_path / "server-called"
            args_file = tmp_path / "python-args.txt"
            server_script = tmp_path / "server.sh"
            python_script = tmp_path / "python.sh"
            cases_path.write_text("[]\n", encoding="utf-8")
            _write_executable(
                server_script,
                '#!/usr/bin/env sh\nset -eu\nprintf "server\\n" > "$SERVER_MARKER"\n',
            )
            _write_executable(
                python_script,
                (
                    "#!/usr/bin/env sh\n"
                    "set -eu\n"
                    '[ -f "$SERVER_MARKER" ] || exit 7\n'
                    'printf "%s\\n" "$@" > "$PYTHON_ARGS"\n'
                ),
            )

            env = os.environ.copy()
            env.update(
                {
                    "PYTHON": str(python_script),
                    "EVAL_SERVER_DAEMON_SCRIPT": str(server_script),
                    "PYTHON_ARGS": str(args_file),
                    "OCR_HANDWRITING_CASES": str(cases_path),
                    "OCR_EVAL_TIMEOUT": "12",
                    "OCR_EVAL_OCR_RETRIES": "3",
                    "OCR_EVAL_OCR_RETRY_DELAY_MS": "44",
                    "OCR_MAX_CONSEC_RATE_LIMIT_ERRORS": "5",
                    "SERVER_MARKER": str(server_marker),
                }
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "run"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(server_marker.read_text(encoding="utf-8"), "server\n")
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "tools.eval_ocr",
                    "--timeout",
                    "12",
                    "--cases",
                    str(cases_path),
                    "--strict",
                    "--show-text",
                    "--ocr-retries",
                    "3",
                    "--ocr-retry-delay-ms",
                    "44",
                    "--max-consecutive-rate-limit-errors",
                    "5",
                ],
            )

    def test_report_mode_writes_timestamped_handwriting_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "handwriting.json"
            server_marker = tmp_path / "server-called"
            args_file = tmp_path / "python-args.txt"
            report_dir = tmp_path / "reports"
            server_script = tmp_path / "server.sh"
            python_script = tmp_path / "python.sh"
            cases_path.write_text("[]\n", encoding="utf-8")
            _write_executable(
                server_script,
                '#!/usr/bin/env sh\nset -eu\nprintf "server\\n" > "$SERVER_MARKER"\n',
            )
            _write_executable(
                python_script,
                (
                    "#!/usr/bin/env sh\n"
                    "set -eu\n"
                    '[ -f "$SERVER_MARKER" ] || exit 7\n'
                    'printf "%s\\n" "$@" > "$PYTHON_ARGS"\n'
                ),
            )

            env = os.environ.copy()
            env.update(
                {
                    "PYTHON": str(python_script),
                    "EVAL_SERVER_DAEMON_SCRIPT": str(server_script),
                    "PYTHON_ARGS": str(args_file),
                    "OCR_HANDWRITING_CASES": str(cases_path),
                    "OCR_EVAL_TIMEOUT": "12",
                    "OCR_EVAL_OCR_RETRIES": "3",
                    "OCR_EVAL_OCR_RETRY_DELAY_MS": "44",
                    "OCR_MAX_CONSEC_RATE_LIMIT_ERRORS": "5",
                    "EVAL_REPORTS_DIR": str(report_dir),
                    "EVAL_REPORT_RUN_ID": "run-123",
                    "SERVER_MARKER": str(server_marker),
                }
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "report"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(server_marker.read_text(encoding="utf-8"), "server\n")
            self.assertTrue(report_dir.is_dir())
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "tools.eval_ocr",
                    "--timeout",
                    "12",
                    "--cases",
                    str(cases_path),
                    "--strict",
                    "--show-text",
                    "--ocr-retries",
                    "3",
                    "--ocr-retry-delay-ms",
                    "44",
                    "--max-consecutive-rate-limit-errors",
                    "5",
                    "--run-id",
                    "run-123",
                    "--report-json",
                    str(report_dir / "ocr-handwriting-run-123.json"),
                ],
            )

    def test_rejects_missing_cases_or_unknown_mode(self) -> None:
        missing_result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "run"],
            cwd=REPO_ROOT,
            env={**os.environ, "OCR_HANDWRITING_CASES": "missing.json"},
            capture_output=True,
            text=True,
        )
        self.assertEqual(missing_result.returncode, 1)
        self.assertIn("Handwriting cases file not found", missing_result.stdout)

        unknown_result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "unknown"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(unknown_result.returncode, 2)
        self.assertIn("Unknown OCR handwriting eval mode", unknown_result.stderr)

    def test_resolves_repo_root_when_called_from_outside_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "handwriting.json"
            server_marker = tmp_path / "server-called"
            pwd_file = tmp_path / "python-pwd.txt"
            server_script = tmp_path / "server.sh"
            python_script = tmp_path / "python.sh"
            cases_path.write_text("[]\n", encoding="utf-8")
            _write_executable(
                server_script,
                '#!/usr/bin/env sh\nset -eu\nprintf "server\\n" > "$SERVER_MARKER"\n',
            )
            _write_executable(
                python_script,
                (
                    "#!/usr/bin/env sh\n"
                    "set -eu\n"
                    '[ -f "$SERVER_MARKER" ] || exit 7\n'
                    'pwd > "$PYTHON_PWD"\n'
                ),
            )

            env = os.environ.copy()
            env.update(
                {
                    "PYTHON": str(python_script),
                    "EVAL_SERVER_DAEMON_SCRIPT": str(server_script),
                    "PYTHON_PWD": str(pwd_file),
                    "OCR_HANDWRITING_CASES": str(cases_path),
                    "SERVER_MARKER": str(server_marker),
                }
            )

            result = subprocess.run(
                ["bash", str(SCRIPT), "run"],
                cwd=tmp_path,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(server_marker.read_text(encoding="utf-8"), "server\n")
            self.assertEqual(
                pwd_file.read_text(encoding="utf-8").strip(), str(REPO_ROOT)
            )


if __name__ == "__main__":
    unittest.main()
