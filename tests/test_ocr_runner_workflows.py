import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FOCUS_WORKFLOW = REPO_ROOT / "tools" / "run_ocr_focus_stability_workflow.sh"
GROWTH_WORKFLOW = REPO_ROOT / "tools" / "run_ocr_growth_stability_workflow.sh"


def _write_runner(path: Path) -> None:
    path.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env sh
            printf 'runner args:'
            for arg in "$@"; do
                printf ' <%s>' "$arg"
            done
            printf '\\n'
            """
        ),
        encoding="utf-8",
    )
    path.chmod(0o755)


def _base_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHON"] = sys.executable
    env["EVAL_CASE_GUARD_SCRIPT"] = "tools/eval_case_guard.sh"
    env["EVAL_SERVER_DAEMON_SCRIPT"] = "unused-daemon.sh"
    return env


class OcrRunnerWorkflowTests(unittest.TestCase):
    def test_focus_stability_workflow_runs_configured_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "focus_cases.json"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": [{"id": "focus-a"}]}', encoding="utf-8")
            _write_runner(runner_path)

            env = _base_env()
            env.update(
                {
                    "OCR_STABILITY_RUNNER_SCRIPT": str(runner_path),
                    "OCR_FOCUS_CASES_JSON": str(cases_path),
                    "OCR_FOCUS_RUNS": "4",
                    "OCR_FOCUS_OCR_RETRIES": "5",
                    "OCR_FOCUS_OCR_RETRY_DELAY_MS": "600",
                    "OCR_FOCUS_CASE_DELAY_MS": "700",
                    "OCR_FOCUS_RATE_LIMIT_COOLDOWN_MS": "800",
                    "OCR_FOCUS_REPORT_DIR": str(tmp_path / "focus-runs"),
                    "OCR_FOCUS_OUTPUT": str(tmp_path / "focus-output.json"),
                    "OCR_FOCUS_SKIP_RECENT_RATE_LIMIT": "false",
                    "OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS": "900",
                    "OCR_GROWTH_FAIL_COHORT_JSON": str(tmp_path / "fail-cohort.json"),
                }
            )

            result = subprocess.run(
                ["bash", str(FOCUS_WORKFLOW)],
                capture_output=True,
                cwd=REPO_ROOT,
                env=env,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn(f"runner args: <{cases_path}> <4> <5> <600>", result.stdout)
        self.assertIn("<700> <800>", result.stdout)

    def test_focus_stability_workflow_skips_empty_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "focus_cases.json"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": []}', encoding="utf-8")
            _write_runner(runner_path)

            env = _base_env()
            env.update(
                {
                    "OCR_STABILITY_RUNNER_SCRIPT": str(runner_path),
                    "OCR_FOCUS_CASES_JSON": str(cases_path),
                }
            )

            result = subprocess.run(
                ["bash", str(FOCUS_WORKFLOW)],
                capture_output=True,
                cwd=REPO_ROOT,
                env=env,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.strip(),
            "No OCR focus cases available; skipping focus stability run.",
        )
        self.assertNotIn("runner args:", result.stdout)

    def test_focus_stability_workflow_uses_default_common_from_subdirectory(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "focus_cases.json"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text(
                '{"cases": [{"id": "focus-subdir"}]}', encoding="utf-8"
            )
            _write_runner(runner_path)

            env = _base_env()
            env.update(
                {
                    "OCR_STABILITY_RUNNER_SCRIPT": str(runner_path),
                    "OCR_FOCUS_CASES_JSON": str(cases_path),
                    "OCR_FOCUS_SKIP_RECENT_RATE_LIMIT": "false",
                }
            )

            result = subprocess.run(
                ["bash", str(FOCUS_WORKFLOW)],
                capture_output=True,
                cwd=REPO_ROOT / "docs",
                env=env,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"runner args: <{cases_path}>", result.stdout)

    def test_growth_stability_workflow_preserves_sliced_output_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "growth_cases.json"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": [{"id": "growth-a"}]}', encoding="utf-8")
            _write_runner(runner_path)

            env = _base_env()
            env.update(
                {
                    "OCR_GROWTH_STABILITY_RUNNER_SCRIPT": str(runner_path),
                    "OCR_TRANSCRIPT_CASES_GROWTH": str(cases_path),
                    "OCR_GROWTH_STABILITY_RUNS": "6",
                    "OCR_GROWTH_EVAL_OFFSET": "2",
                    "OCR_GROWTH_EVAL_MAX_CASES": "9",
                    "OCR_EVAL_TIMEOUT": "90",
                    "OCR_GROWTH_OCR_RETRIES": "3",
                    "OCR_GROWTH_OCR_RETRY_DELAY_MS": "400",
                    "OCR_GROWTH_CASE_DELAY_MS": "500",
                    "OCR_GROWTH_RATE_LIMIT_COOLDOWN_MS": "600",
                    "OCR_MAX_CONSEC_RATE_LIMIT_ERRORS": "7",
                    "OCR_GROWTH_STABILITY_REPORT_DIR": str(tmp_path / "growth-runs"),
                    "OCR_GROWTH_STABILITY_OUTPUT": str(tmp_path / "growth.json"),
                }
            )

            result = subprocess.run(
                ["bash", str(GROWTH_WORKFLOW)],
                capture_output=True,
                cwd=REPO_ROOT,
                env=env,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "Using sliced growth stability output: "
            ".local/eval_reports/ocr_growth_stability.slice-offset2-max9.json",
            result.stdout,
        )
        self.assertIn(f"runner args: <{cases_path}> <6> <2> <9>", result.stdout)
        self.assertIn(
            "<.local/eval_reports/ocr_growth_stability.slice-offset2-max9.json>",
            result.stdout,
        )

    def test_growth_stability_workflow_rejects_invalid_slice_controls(self) -> None:
        for env_name in ("OCR_GROWTH_EVAL_OFFSET", "OCR_GROWTH_EVAL_MAX_CASES"):
            with self.subTest(env_name=env_name):
                with tempfile.TemporaryDirectory() as tmp:
                    tmp_path = Path(tmp)
                    cases_path = tmp_path / "growth_cases.json"
                    runner_path = tmp_path / "runner.sh"
                    cases_path.write_text(
                        '{"cases": [{"id": "growth-invalid"}]}',
                        encoding="utf-8",
                    )
                    _write_runner(runner_path)

                    env = _base_env()
                    env.update(
                        {
                            "OCR_GROWTH_STABILITY_RUNNER_SCRIPT": str(runner_path),
                            "OCR_TRANSCRIPT_CASES_GROWTH": str(cases_path),
                            "OCR_GROWTH_EVAL_OFFSET": "0",
                            "OCR_GROWTH_EVAL_MAX_CASES": "0",
                            env_name: "abc",
                        }
                    )

                    result = subprocess.run(
                        ["bash", str(GROWTH_WORKFLOW)],
                        capture_output=True,
                        cwd=REPO_ROOT,
                        env=env,
                        text=True,
                    )

                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    "Invalid numeric value for OCR growth stability workflow: "
                    f"{env_name} must be a non-negative integer (got abc)",
                    result.stderr,
                )
                self.assertNotIn("runner args:", result.stdout)

    def test_growth_stability_workflow_uses_default_common_from_subdirectory(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "growth_cases.json"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text(
                '{"cases": [{"id": "growth-subdir"}]}', encoding="utf-8"
            )
            _write_runner(runner_path)

            env = _base_env()
            env.update(
                {
                    "OCR_GROWTH_STABILITY_RUNNER_SCRIPT": str(runner_path),
                    "OCR_TRANSCRIPT_CASES_GROWTH": str(cases_path),
                }
            )

            result = subprocess.run(
                ["bash", str(GROWTH_WORKFLOW)],
                capture_output=True,
                cwd=REPO_ROOT / "docs",
                env=env,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"runner args: <{cases_path}>", result.stdout)


if __name__ == "__main__":
    unittest.main()
