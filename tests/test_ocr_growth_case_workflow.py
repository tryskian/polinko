import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_SCRIPT = REPO_ROOT / "tools" / "run_ocr_growth_case_workflow.sh"


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


def _base_env(runner_path: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "PYTHON": sys.executable,
            "EVAL_CASE_GUARD_SCRIPT": "tools/eval_case_guard.sh",
            "OCR_GROWTH_EVAL_RUNNER_SCRIPT": str(runner_path),
            "OCR_GROWTH_BATCH_RUNNER_SCRIPT": str(runner_path),
        }
    )
    return env


class OcrGrowthCaseWorkflowTests(unittest.TestCase):
    def test_eval_suite_runs_configured_growth_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "growth.json"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": [{"id": "growth-a"}]}', encoding="utf-8")
            _write_runner(runner_path)

            env = _base_env(runner_path)
            env.update(
                {
                    "OCR_TRANSCRIPT_CASES_GROWTH": str(cases_path),
                    "OCR_EVAL_TIMEOUT": "91",
                    "OCR_GROWTH_EVAL_OFFSET": "2",
                    "OCR_GROWTH_EVAL_MAX_CASES": "8",
                    "OCR_EVAL_OCR_RETRIES": "4",
                    "OCR_EVAL_OCR_RETRY_DELAY_MS": "55",
                    "OCR_MAX_CONSEC_RATE_LIMIT_ERRORS": "6",
                }
            )

            result = subprocess.run(
                ["bash", str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)), "eval"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            f"runner args: <{cases_path}> <91> <2> <8> <4> <55> <6>",
        )

    def test_batched_suite_runs_configured_batch_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "growth.json"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": [{"id": "growth-b"}]}', encoding="utf-8")
            _write_runner(runner_path)

            env = _base_env(runner_path)
            env.update(
                {
                    "OCR_TRANSCRIPT_CASES_GROWTH": str(cases_path),
                    "OCR_GROWTH_BATCH_SIZE": "12",
                    "OCR_GROWTH_OCR_RETRIES": "3",
                    "OCR_GROWTH_OCR_RETRY_DELAY_MS": "44",
                    "OCR_GROWTH_EVAL_OFFSET": "5",
                    "OCR_GROWTH_EVAL_MAX_CASES": "9",
                    "OCR_GROWTH_BATCH_REPORT_DIR": "runs-dir",
                    "OCR_GROWTH_BATCH_SUMMARY_JSON": "summary.json",
                    "OCR_GROWTH_BATCH_SUMMARY_MD": "summary.md",
                }
            )

            result = subprocess.run(
                ["bash", str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)), "batched"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            f"runner args: <{cases_path}> <12> <3> <44> <5> <9> "
            "<runs-dir> <summary.json> <summary.md>",
        )

    def test_missing_cases_fail_with_existing_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            missing_cases = tmp_path / "missing-growth.json"
            runner_path = tmp_path / "runner.sh"
            _write_runner(runner_path)

            env = _base_env(runner_path)
            env["OCR_TRANSCRIPT_CASES_GROWTH"] = str(missing_cases)

            result = subprocess.run(
                ["bash", str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)), "eval"],
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
        self.assertNotIn("runner args:", result.stdout)

    def test_empty_cases_skip_with_existing_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "empty-growth.json"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": []}', encoding="utf-8")
            _write_runner(runner_path)

            env = _base_env(runner_path)
            env["OCR_TRANSCRIPT_CASES_GROWTH"] = str(cases_path)

            result = subprocess.run(
                ["bash", str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)), "batched"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.strip(),
            "No transcript OCR growth cases available yet; skipping eval.",
        )

    def test_workflow_rejects_unknown_or_missing_suite(self) -> None:
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
                    or "Unknown OCR growth case workflow suite" in result.stderr
                )


if __name__ == "__main__":
    unittest.main()
