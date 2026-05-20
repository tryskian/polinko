import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "run_eval_ocr_cases.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class RunEvalOcrCasesTests(unittest.TestCase):
    def test_runs_server_before_strict_eval_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            server_marker = tmp_path / "server-called"
            args_file = tmp_path / "python-args.txt"
            server_script = tmp_path / "server.sh"
            python_script = tmp_path / "python.sh"

            _write_executable(
                server_script,
                '#!/usr/bin/env sh\nset -eu\nprintf "server\\n" > "$SERVER_MARKER"\n',
            )
            _write_executable(
                python_script,
                (
                    '#!/usr/bin/env sh\n'
                    'set -eu\n'
                    '[ -f "$SERVER_MARKER" ] || exit 7\n'
                    'printf "%s\\n" "$@" > "$PYTHON_ARGS"\n'
                ),
            )

            env = os.environ.copy()
            env.update(
                {
                    "PYTHON": str(python_script),
                    "EVAL_SERVER_DAEMON_SCRIPT": str(server_script),
                    "OCR_EVAL_TIMEOUT": "12",
                    "OCR_EVAL_OCR_RETRIES": "3",
                    "OCR_EVAL_OCR_RETRY_DELAY_MS": "44",
                    "OCR_MAX_CONSEC_RATE_LIMIT_ERRORS": "5",
                    "SERVER_MARKER": str(server_marker),
                    "PYTHON_ARGS": str(args_file),
                }
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "cases.json"],
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
                    "cases.json",
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

    def test_requires_cases_path(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT))],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage: run_eval_ocr_cases.sh <cases-json>", result.stderr)


if __name__ == "__main__":
    unittest.main()
