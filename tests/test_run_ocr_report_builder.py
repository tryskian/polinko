import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILDER_SCRIPT = REPO_ROOT / "tools" / "run_ocr_report_builder.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class RunOcrReportBuilderTests(unittest.TestCase):
    def _base_env(self, tmp_path: Path) -> tuple[dict[str, str], Path]:
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
                "OCR_TRANSCRIPT_CASES_GROWTH": "growth-cases.json",
                "OCR_TRANSCRIPT_REVIEW": "review.json",
                "OCR_GROWTH_STABILITY_OUTPUT": "growth-stability.json",
                "OCR_GROWTH_STABILITY_REPORT_DIR": "growth-runs",
                "OCR_GROWTH_METRICS_OUTPUT": "growth-metrics.json",
                "OCR_GROWTH_METRICS_MARKDOWN": "growth-metrics.md",
                "OCR_GROWTH_LIMIT_RUNS": "7",
                "OCR_GROWTH_FAIL_COHORT_JSON": "fail-cohort.json",
                "OCR_GROWTH_FAIL_COHORT_MARKDOWN": "fail-cohort.md",
                "OCR_FAIL_COHORT_MIN_RUNS": "2",
                "OCR_FAIL_COHORT_INCLUDE_UNSTABLE": "true",
                "OCR_FAIL_COHORT_REQUIRE_OCR_FRAMING": "true",
                "OCR_FAIL_COHORT_INCLUDE_EXPLORATORY": "true",
                "OCR_FAIL_COHORT_EXPLORATORY_MAX_CASES": "11",
                "OCR_FOCUS_CASES_JSON": "focus-cases.json",
                "OCR_FOCUS_MAX_CASES": "9",
                "OCR_FOCUS_INCLUDE_FAIL_HISTORY": "false",
                "OCR_FOCUS_INCLUDE_EXPLORATORY": "false",
                "OCR_FOCUS_OUTPUT": "focus-stability.json",
                "OCR_FOCUS_FAIL_PATTERNS_JSON": "focus-patterns.json",
                "OCR_FOCUS_FAIL_PATTERNS_MD": "focus-patterns.md",
            }
        )
        return env, args_file

    def test_report_builder_suites_build_expected_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, args_file = self._base_env(tmp_path)
            expectations = {
                "growth-metrics": [
                    "-m",
                    "tools.eval_ocr_growth_metrics",
                    "--cases",
                    "growth-cases.json",
                    "--runs-dir",
                    "growth-runs",
                    "--output-json",
                    "growth-metrics.json",
                    "--output-markdown",
                    "growth-metrics.md",
                    "--limit-runs",
                    "7",
                ],
                "growth-fail-cohort": [
                    "-m",
                    "tools.build_ocr_growth_fail_cohort",
                    "--stability-report",
                    "growth-stability.json",
                    "--cases",
                    "growth-cases.json",
                    "--metrics",
                    "growth-metrics.json",
                    "--review",
                    "review.json",
                    "--output-json",
                    "fail-cohort.json",
                    "--output-markdown",
                    "fail-cohort.md",
                    "--min-runs",
                    "2",
                    "--include-unstable",
                    "--require-ocr-framing",
                    "--include-exploratory",
                    "--exploratory-max-cases",
                    "11",
                ],
                "focus-cases": [
                    "-m",
                    "tools.build_ocr_focus_cases",
                    "--cohort",
                    "fail-cohort.json",
                    "--source-cases",
                    "growth-cases.json",
                    "--output-cases",
                    "focus-cases.json",
                    "--max-cases",
                    "9",
                    "--exclude-fail-history",
                    "--exclude-exploratory",
                ],
                "focus-fail-patterns": [
                    "-m",
                    "tools.report_ocr_focus_fail_patterns",
                    "--stability-report",
                    "focus-stability.json",
                    "--focus-cases",
                    "focus-cases.json",
                    "--output-json",
                    "focus-patterns.json",
                    "--output-markdown",
                    "focus-patterns.md",
                ],
            }

            for suite, expected_args in expectations.items():
                with self.subTest(suite=suite):
                    if args_file.exists():
                        args_file.unlink()

                    result = subprocess.run(
                        ["bash", str(BUILDER_SCRIPT.relative_to(REPO_ROOT)), suite],
                        cwd=REPO_ROOT,
                        env=env,
                        capture_output=True,
                        text=True,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(
                        args_file.read_text(encoding="utf-8").splitlines(),
                        expected_args,
                    )

    def test_optional_flags_are_omitted_when_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, args_file = self._base_env(tmp_path)
            env.update(
                {
                    "OCR_FAIL_COHORT_INCLUDE_UNSTABLE": "false",
                    "OCR_FAIL_COHORT_REQUIRE_OCR_FRAMING": "false",
                    "OCR_FAIL_COHORT_INCLUDE_EXPLORATORY": "false",
                    "OCR_FOCUS_INCLUDE_FAIL_HISTORY": "true",
                    "OCR_FOCUS_INCLUDE_EXPLORATORY": "true",
                }
            )

            for suite, omitted in (
                (
                    "growth-fail-cohort",
                    [
                        "--include-unstable",
                        "--require-ocr-framing",
                        "--include-exploratory",
                    ],
                ),
                (
                    "focus-cases",
                    [
                        "--exclude-fail-history",
                        "--exclude-exploratory",
                    ],
                ),
            ):
                with self.subTest(suite=suite):
                    if args_file.exists():
                        args_file.unlink()

                    result = subprocess.run(
                        ["bash", str(BUILDER_SCRIPT.relative_to(REPO_ROOT)), suite],
                        cwd=REPO_ROOT,
                        env=env,
                        capture_output=True,
                        text=True,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    args = args_file.read_text(encoding="utf-8").splitlines()
                    for arg in omitted:
                        self.assertNotIn(arg, args)

    def test_report_builder_rejects_unknown_or_missing_suite(self) -> None:
        for args in ([], ["unknown"]):
            with self.subTest(args=args):
                result = subprocess.run(
                    ["bash", str(BUILDER_SCRIPT.relative_to(REPO_ROOT)), *args],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 2)
                self.assertTrue(
                    "Usage:" in result.stderr
                    or "Unknown OCR report-builder suite" in result.stderr
                )


if __name__ == "__main__":
    unittest.main()
