import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "run_eval_reports_parallel.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class RunEvalReportsParallelTests(unittest.TestCase):
    def test_builds_parallel_orchestrator_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
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
                    "BASE_URL": "http://127.0.0.1:9999",
                    "EVAL_REPORTS_PARALLEL_RUN_ID": "run-123",
                    "HALLUCINATION_EVAL_MODE": "deterministic",
                    "HALLUCINATION_MIN_ACCEPTABLE_SCORE": "7",
                }
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT))],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "tools.eval_parallel_orchestrator",
                    "--base-url",
                    "http://127.0.0.1:9999",
                    "--run-id",
                    "run-123",
                    "--hallucination-mode",
                    "deterministic",
                    "--hallucination-min-acceptable-score",
                    "7",
                ],
            )

    def test_runs_from_subdirectory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
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
                    "EVAL_REPORTS_PARALLEL_RUN_ID": "run-456",
                }
            )

            result = subprocess.run(
                ["bash", "../tools/run_eval_reports_parallel.sh"],
                cwd=REPO_ROOT / "docs",
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "tools.eval_parallel_orchestrator",
                    "--base-url",
                    "http://127.0.0.1:8000",
                    "--run-id",
                    "run-456",
                    "--hallucination-mode",
                    "judge",
                    "--hallucination-min-acceptable-score",
                    "5",
                ],
            )

    def test_rejects_arguments(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "extra"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage: run_eval_reports_parallel.sh", result.stderr)


if __name__ == "__main__":
    unittest.main()
