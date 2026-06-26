import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_SCRIPT = REPO_ROOT / "tools" / "run_ocr_base_transcript_workflow.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class OcrBaseTranscriptWorkflowTests(unittest.TestCase):
    def test_cases_workflow_runs_configured_eval_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "cases.json"
            args_file = tmp_path / "runner-args.txt"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": [{"id": "case-1"}]}', encoding="utf-8")
            _write_executable(
                runner_path,
                '#!/usr/bin/env sh\nset -eu\nprintf "%s\\n" "$@" > "$RUNNER_ARGS"\n',
            )

            env = os.environ.copy()
            env.update(
                {
                    "OCR_TRANSCRIPT_CASES": str(cases_path),
                    "OCR_EVAL_RUNNER_SCRIPT": str(runner_path),
                    "RUNNER_ARGS": str(args_file),
                }
            )

            result = subprocess.run(
                ["bash", str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)), "cases"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(), [str(cases_path)]
            )

    def test_cases_workflow_uses_default_guard_from_subdirectory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "cases.json"
            args_file = tmp_path / "runner-args.txt"
            cwd_file = tmp_path / "runner-cwd.txt"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": [{"id": "case-1"}]}', encoding="utf-8")
            _write_executable(
                runner_path,
                (
                    "#!/usr/bin/env sh\n"
                    "set -eu\n"
                    'printf "%s\\n" "$PWD" > "$RUNNER_CWD"\n'
                    'printf "%s\\n" "$@" > "$RUNNER_ARGS"\n'
                ),
            )

            env = os.environ.copy()
            env.pop("OCR_WORKFLOW_COMMON_SCRIPT", None)
            env.pop("EVAL_CASE_GUARD_SCRIPT", None)
            env.update(
                {
                    "PYTHON": sys.executable,
                    "OCR_TRANSCRIPT_CASES": str(cases_path),
                    "OCR_EVAL_RUNNER_SCRIPT": str(runner_path),
                    "RUNNER_ARGS": str(args_file),
                    "RUNNER_CWD": str(cwd_file),
                }
            )

            result = subprocess.run(
                ["bash", "../tools/run_ocr_base_transcript_workflow.sh", "cases"],
                cwd=REPO_ROOT / "docs",
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(cwd_file.read_text(encoding="utf-8"), f"{REPO_ROOT}\n")
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(), [str(cases_path)]
            )

    def test_stability_workflow_runs_configured_stability_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "cases.json"
            args_file = tmp_path / "runner-args.txt"
            env_file = tmp_path / "runner-env.txt"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": [{"id": "case-1"}]}', encoding="utf-8")
            _write_executable(
                runner_path,
                (
                    "#!/usr/bin/env sh\n"
                    "set -eu\n"
                    'printf "%s\\n" "$@" > "$RUNNER_ARGS"\n'
                    'printf "%s\\n" "${OCR_STABILITY_PYTHONUNBUFFERED:-}" > "$RUNNER_ENV"\n'
                ),
            )

            env = os.environ.copy()
            env.update(
                {
                    "OCR_TRANSCRIPT_CASES": str(cases_path),
                    "OCR_STABILITY_RUNNER_SCRIPT": str(runner_path),
                    "OCR_STABILITY_RUNS": "4",
                    "OCR_STABILITY_OCR_RETRIES": "3",
                    "OCR_STABILITY_OCR_RETRY_DELAY_MS": "44",
                    "OCR_STABILITY_CASE_DELAY_MS": "55",
                    "OCR_STABILITY_RATE_LIMIT_COOLDOWN_MS": "66",
                    "OCR_STABILITY_REPORT_DIR": "runs-dir",
                    "OCR_STABILITY_OUTPUT": "out.json",
                    "RUNNER_ARGS": str(args_file),
                    "RUNNER_ENV": str(env_file),
                }
            )

            result = subprocess.run(
                ["bash", str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)), "stability"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                [
                    str(cases_path),
                    "4",
                    "3",
                    "44",
                    "55",
                    "66",
                    "runs-dir",
                    "out.json",
                ],
            )
            self.assertEqual(env_file.read_text(encoding="utf-8"), "1\n")

    def test_missing_cases_fail_with_existing_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            missing_cases = tmp_path / "missing-cases.json"

            env = os.environ.copy()
            env["OCR_TRANSCRIPT_CASES"] = str(missing_cases)

            result = subprocess.run(
                ["bash", str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)), "cases"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn(f"Transcript OCR cases not found: {missing_cases}", result.stdout)
        self.assertIn(
            "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export",
            result.stdout,
        )

    def test_empty_cases_skip_without_running_eval_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "cases.json"
            marker_path = tmp_path / "runner-called.txt"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": []}', encoding="utf-8")
            _write_executable(
                runner_path,
                ('#!/usr/bin/env sh\nset -eu\nprintf "called\\n" > "$RUNNER_MARKER"\n'),
            )

            env = os.environ.copy()
            env.update(
                {
                    "OCR_TRANSCRIPT_CASES": str(cases_path),
                    "OCR_EVAL_RUNNER_SCRIPT": str(runner_path),
                    "RUNNER_MARKER": str(marker_path),
                }
            )

            result = subprocess.run(
                ["bash", str(WORKFLOW_SCRIPT.relative_to(REPO_ROOT)), "cases"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "No transcript OCR cases available yet; skipping eval.", result.stdout
        )
        self.assertFalse(marker_path.exists())

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
                    or "Unknown OCR base transcript workflow suite" in result.stderr
                )


if __name__ == "__main__":
    unittest.main()
