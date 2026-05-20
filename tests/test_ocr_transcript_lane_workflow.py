import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_SCRIPT = REPO_ROOT / "tools" / "run_ocr_transcript_lane_workflow.sh"


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
            "OCR_GUARDED_CASE_RUNNER_SCRIPT": "tools/run_guarded_ocr_case_eval.sh",
            "OCR_EVAL_RUNNER_SCRIPT": str(runner_path),
            "OCR_STABILITY_RUNNER_SCRIPT": str(runner_path),
        }
    )
    return env


class OcrTranscriptLaneWorkflowTests(unittest.TestCase):
    def test_case_lane_runs_configured_eval_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "handwriting.json"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": [{"id": "hand-a"}]}', encoding="utf-8")
            _write_runner(runner_path)

            env = _base_env(runner_path)
            env["OCR_TRANSCRIPT_CASES_HANDWRITING"] = str(cases_path)

            result = subprocess.run(
                [
                    "bash",
                    str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)),
                    "case",
                    "handwriting",
                ],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), f"runner args: <{cases_path}>")

    def test_case_lane_preserves_missing_case_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            missing_cases = tmp_path / "typed-benchmark.json"
            runner_path = tmp_path / "runner.sh"
            _write_runner(runner_path)

            env = _base_env(runner_path)
            env["OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK"] = str(missing_cases)

            result = subprocess.run(
                [
                    "bash",
                    str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)),
                    "case",
                    "typed-benchmark",
                ],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            f"Transcript typed benchmark OCR cases not found: {missing_cases}",
            result.stdout,
        )
        self.assertIn(
            "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export",
            result.stdout,
        )
        self.assertNotIn("runner args:", result.stdout)

    def test_case_lane_preserves_empty_case_skip_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "illustration.json"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": []}', encoding="utf-8")
            _write_runner(runner_path)

            env = _base_env(runner_path)
            env["OCR_TRANSCRIPT_CASES_ILLUSTRATION"] = str(cases_path)

            result = subprocess.run(
                [
                    "bash",
                    str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)),
                    "case",
                    "illustration",
                ],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.strip(),
            "No transcript illustration OCR cases available yet; skipping eval.",
        )

    def test_stability_lane_runs_configured_stability_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "handwriting-benchmark.json"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": [{"id": "hand-bench"}]}', encoding="utf-8")
            _write_runner(runner_path)

            env = _base_env(runner_path)
            env.update(
                {
                    "OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK": str(cases_path),
                    "OCR_STABILITY_RUNS": "4",
                    "OCR_STABILITY_OCR_RETRIES": "3",
                    "OCR_STABILITY_OCR_RETRY_DELAY_MS": "44",
                    "OCR_STABILITY_CASE_DELAY_MS": "55",
                    "OCR_STABILITY_RATE_LIMIT_COOLDOWN_MS": "66",
                    "OCR_STABILITY_HANDWRITING_BENCHMARK_REPORT_DIR": "runs-dir",
                    "OCR_STABILITY_HANDWRITING_BENCHMARK_OUTPUT": "out.json",
                }
            )

            result = subprocess.run(
                [
                    "bash",
                    str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)),
                    "stability",
                    "handwriting-benchmark",
                ],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            f"runner args: <{cases_path}> <4> <3> <44> <55> <66> <runs-dir> <out.json>",
        )

    def test_stability_lane_preserves_empty_case_skip_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "typed-benchmark.json"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": []}', encoding="utf-8")
            _write_runner(runner_path)

            env = _base_env(runner_path)
            env["OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK"] = str(cases_path)

            result = subprocess.run(
                [
                    "bash",
                    str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)),
                    "stability",
                    "typed-benchmark",
                ],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.strip(),
            "No transcript typed benchmark OCR cases available yet; skipping stability run.",
        )

    def test_workflow_rejects_unknown_mode_or_lane(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runner_path = tmp_path / "runner.sh"
            _write_runner(runner_path)

            for args in ([], ["case"], ["unknown", "handwriting"], ["case", "other"]):
                with self.subTest(args=args):
                    result = subprocess.run(
                        [
                            "bash",
                            str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)),
                            *args,
                        ],
                        cwd=REPO_ROOT,
                        env=_base_env(runner_path),
                        capture_output=True,
                        text=True,
                    )

                    self.assertEqual(result.returncode, 2)
                    self.assertTrue(
                        "Usage:" in result.stderr
                        or "Unknown OCR transcript lane workflow" in result.stderr
                    )


if __name__ == "__main__":
    unittest.main()
