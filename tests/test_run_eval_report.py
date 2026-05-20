import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_SCRIPT = REPO_ROOT / "tools" / "run_eval_report.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class RunEvalReportTests(unittest.TestCase):
    def test_report_suites_build_expected_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            args_file = tmp_path / "python-args.txt"
            report_dir = tmp_path / "eval_reports"
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
                    "EVAL_REPORTS_DIR": str(report_dir),
                    "EVAL_REPORT_RUN_ID": "run-123",
                    "RETRIEVAL_REQUEST_RETRIES": "8",
                    "RETRIEVAL_REQUEST_RETRY_DELAY_MS": "1234",
                    "HALLUCINATION_MIN_ACCEPTABLE_SCORE": "6",
                    "STYLE_CASE_ATTEMPTS": "4",
                    "STYLE_MIN_PASS_ATTEMPTS": "3",
                    "OCR_SAFETY_CASES": "safety.json",
                    "OCR_EVAL_TIMEOUT": "45",
                    "OCR_EVAL_OCR_RETRIES": "5",
                    "OCR_EVAL_OCR_RETRY_DELAY_MS": "678",
                    "OCR_MAX_CONSEC_RATE_LIMIT_ERRORS": "9",
                    "CLIP_AB_SOURCE_TYPES": "image,text",
                }
            )

            report = lambda name: str(report_dir / f"{name}-run-123.json")
            expectations = {
                "retrieval": [
                    "-m",
                    "tools.eval_retrieval",
                    "--run-id",
                    "run-123",
                    "--request-retries",
                    "8",
                    "--request-retry-delay-ms",
                    "1234",
                    "--report-json",
                    report("retrieval"),
                ],
                "file-search": [
                    "-m",
                    "tools.eval_file_search",
                    "--run-id",
                    "run-123",
                    "--report-json",
                    report("file-search"),
                ],
                "hallucination": [
                    "-m",
                    "tools.eval_hallucination",
                    "--run-id",
                    "run-123",
                    "--report-json",
                    report("hallucination"),
                    "--min-acceptable-score",
                    "6",
                ],
                "style": [
                    "-m",
                    "tools.eval_style",
                    "--run-id",
                    "run-123",
                    "--report-json",
                    report("style"),
                    "--case-attempts",
                    "4",
                    "--min-pass-attempts",
                    "3",
                ],
                "response-behaviour": [
                    "-m",
                    "tools.eval_response_behaviour",
                    "--run-id",
                    "run-123",
                    "--report-json",
                    report("response-behaviour"),
                ],
                "ocr-safety": [
                    "-m",
                    "tools.eval_response_behaviour",
                    "--suite-id",
                    "ocr_safety",
                    "--cases",
                    "safety.json",
                    "--session-prefix",
                    "ocr-safety-eval",
                    "--run-id",
                    "run-123",
                    "--report-json",
                    report("ocr-safety"),
                ],
                "ocr": [
                    "-m",
                    "tools.eval_ocr",
                    "--timeout",
                    "45",
                    "--ocr-retries",
                    "5",
                    "--ocr-retry-delay-ms",
                    "678",
                    "--max-consecutive-rate-limit-errors",
                    "9",
                    "--run-id",
                    "run-123",
                    "--report-json",
                    report("ocr"),
                ],
                "ocr-recovery": [
                    "-m",
                    "tools.eval_ocr_recovery",
                    "--run-id",
                    "run-123",
                    "--report-json",
                    report("ocr-recovery"),
                ],
                "clip-ab": [
                    "-m",
                    "tools.eval_clip_ab",
                    "--source-types",
                    "image,text",
                    "--run-id",
                    "run-123",
                    "--report-json",
                    report("clip-ab"),
                ],
            }

            for suite, expected_args in expectations.items():
                with self.subTest(suite=suite):
                    if args_file.exists():
                        args_file.unlink()

                    result = subprocess.run(
                        ["bash", str(REPORT_SCRIPT.relative_to(REPO_ROOT)), suite],
                        cwd=REPO_ROOT,
                        env=env,
                        capture_output=True,
                        text=True,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertTrue(report_dir.is_dir())
                    self.assertEqual(
                        args_file.read_text(encoding="utf-8").splitlines(),
                        expected_args,
                    )

    def test_report_script_rejects_unknown_or_missing_suite(self) -> None:
        for args in ([], ["unknown"]):
            with self.subTest(args=args):
                result = subprocess.run(
                    ["bash", str(REPORT_SCRIPT.relative_to(REPO_ROOT)), *args],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 2)
                self.assertTrue(
                    "Usage:" in result.stderr or "Unknown eval report suite" in result.stderr
                )


if __name__ == "__main__":
    unittest.main()
