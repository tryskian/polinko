import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_SCRIPT = REPO_ROOT / "tools" / "run_ocr_report_workflow.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class OcrReportWorkflowTests(unittest.TestCase):
    def _builder_env(self, tmp_path: Path) -> tuple[dict[str, str], Path]:
        builder_args = tmp_path / "builder-args.txt"
        builder_script = tmp_path / "builder.sh"
        _write_executable(
            builder_script,
            '#!/usr/bin/env sh\nset -eu\nprintf "%s\\n" "$@" > "$BUILDER_ARGS"\n',
        )

        env = os.environ.copy()
        env.update(
            {
                "OCR_REPORT_BUILDER_SCRIPT": str(builder_script),
                "BUILDER_ARGS": str(builder_args),
            }
        )
        return env, builder_args

    def _python_env(self, tmp_path: Path) -> tuple[dict[str, str], Path]:
        python_args = tmp_path / "python-args.txt"
        python_script = tmp_path / "python.sh"
        _write_executable(
            python_script,
            (
                "#!/usr/bin/env sh\n"
                "set -eu\n"
                'printf "%s\\n" "$PWD" > "$PYTHON_ARGS"\n'
                'printf "%s\\n" "$@" >> "$PYTHON_ARGS"\n'
            ),
        )

        env = os.environ.copy()
        env.pop("OCR_REPORT_BUILDER_SCRIPT", None)
        env.update(
            {
                "PYTHON": str(python_script),
                "PYTHON_ARGS": str(python_args),
            }
        )
        return env, python_args

    def test_report_workflow_runs_configured_builder_after_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, builder_args = self._builder_env(tmp_path)

            growth_cases = tmp_path / "growth-cases.json"
            growth_runs = tmp_path / "growth-runs"
            growth_report = tmp_path / "growth-stability.json"
            transcript_review = tmp_path / "review.json"
            fail_cohort = tmp_path / "fail-cohort.json"
            focus_output = tmp_path / "focus-stability.json"
            focus_cases = tmp_path / "focus-cases.json"
            growth_runs.mkdir()
            for path in (
                growth_cases,
                growth_report,
                transcript_review,
                fail_cohort,
                focus_output,
                focus_cases,
            ):
                path.write_text("{}", encoding="utf-8")

            env.update(
                {
                    "OCR_TRANSCRIPT_CASES_GROWTH": str(growth_cases),
                    "OCR_GROWTH_STABILITY_REPORT_DIR": str(growth_runs),
                    "OCR_GROWTH_STABILITY_OUTPUT": str(growth_report),
                    "OCR_TRANSCRIPT_REVIEW": str(transcript_review),
                    "OCR_GROWTH_FAIL_COHORT_JSON": str(fail_cohort),
                    "OCR_FOCUS_OUTPUT": str(focus_output),
                    "OCR_FOCUS_CASES_JSON": str(focus_cases),
                }
            )

            for suite in (
                "growth-metrics",
                "growth-fail-cohort",
                "focus-cases",
                "focus-fail-patterns",
            ):
                with self.subTest(suite=suite):
                    if builder_args.exists():
                        builder_args.unlink()

                    result = subprocess.run(
                        ["bash", str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)), suite],
                        cwd=REPO_ROOT,
                        env=env,
                        capture_output=True,
                        text=True,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(
                        builder_args.read_text(encoding="utf-8").splitlines(),
                        [suite],
                    )

    def test_report_workflow_uses_default_builder_from_subdirectory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, python_args = self._python_env(tmp_path)

            growth_cases = tmp_path / "growth-cases.json"
            fail_cohort = tmp_path / "fail-cohort.json"
            focus_cases = tmp_path / "focus-cases.json"
            for path in (growth_cases, fail_cohort):
                path.write_text("{}", encoding="utf-8")

            env.update(
                {
                    "OCR_TRANSCRIPT_CASES_GROWTH": str(growth_cases),
                    "OCR_GROWTH_FAIL_COHORT_JSON": str(fail_cohort),
                    "OCR_FOCUS_CASES_JSON": str(focus_cases),
                    "OCR_FOCUS_MAX_CASES": "12",
                    "OCR_FOCUS_INCLUDE_FAIL_HISTORY": "false",
                    "OCR_FOCUS_INCLUDE_EXPLORATORY": "false",
                }
            )

            result = subprocess.run(
                ["bash", "../tools/run_ocr_report_workflow.sh", "focus-cases"],
                cwd=REPO_ROOT / "docs",
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                python_args.read_text(encoding="utf-8").splitlines(),
                [
                    str(REPO_ROOT),
                    "-m",
                    "tools.build_ocr_focus_cases",
                    "--cohort",
                    str(fail_cohort),
                    "--source-cases",
                    str(growth_cases),
                    "--output-cases",
                    str(focus_cases),
                    "--max-cases",
                    "12",
                    "--exclude-fail-history",
                    "--exclude-exploratory",
                ],
            )

    def test_report_workflow_preserves_growth_metrics_missing_case_message(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, builder_args = self._builder_env(tmp_path)
            missing_cases = tmp_path / "missing-growth-cases.json"
            env.update(
                {
                    "OCR_TRANSCRIPT_CASES_GROWTH": str(missing_cases),
                    "OCR_GROWTH_STABILITY_REPORT_DIR": str(tmp_path),
                }
            )

            result = subprocess.run(
                ["bash", str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)), "growth-metrics"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            f"Transcript OCR growth cases not found: {missing_cases}",
            result.stdout,
        )
        self.assertIn(
            "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export",
            result.stdout,
        )
        self.assertFalse(builder_args.exists())

    def test_report_workflow_preserves_focus_pattern_missing_case_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, builder_args = self._builder_env(tmp_path)
            focus_output = tmp_path / "focus-stability.json"
            missing_focus_cases = tmp_path / "missing-focus-cases.json"
            focus_output.write_text("{}", encoding="utf-8")
            env.update(
                {
                    "OCR_FOCUS_OUTPUT": str(focus_output),
                    "OCR_FOCUS_CASES_JSON": str(missing_focus_cases),
                }
            )

            result = subprocess.run(
                [
                    "bash",
                    str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)),
                    "focus-fail-patterns",
                ],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            f"OCR focus cases not found: {missing_focus_cases}",
            result.stdout,
        )
        self.assertIn("Run: make ocrfocuscases", result.stdout)
        self.assertFalse(builder_args.exists())

    def test_report_workflow_rejects_unknown_or_missing_suite(self) -> None:
        for args in ([], ["unknown"]):
            with self.subTest(args=args):
                result = subprocess.run(
                    ["bash", str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)), *args],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 2)
                self.assertTrue(
                    "Usage:" in result.stderr
                    or "Unknown OCR report workflow suite" in result.stderr
                )


if __name__ == "__main__":
    unittest.main()
