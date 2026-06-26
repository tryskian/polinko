import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "run_guarded_ocr_case_eval.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class RunGuardedOcrCaseEvalTests(unittest.TestCase):
    def test_guarded_runner_uses_default_guard_from_subdirectory(self) -> None:
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
                    "RUNNER_ARGS": str(args_file),
                    "RUNNER_CWD": str(cwd_file),
                }
            )

            result = subprocess.run(
                [
                    "bash",
                    "../tools/run_guarded_ocr_case_eval.sh",
                    str(cases_path),
                    "Cases missing",
                    "Run: make ocrmine",
                    "No cases; skipping.",
                    "--",
                    str(runner_path),
                    "alpha",
                    "beta",
                ],
                cwd=REPO_ROOT / "docs",
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(cwd_file.read_text(encoding="utf-8"), f"{REPO_ROOT}\n")
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                ["alpha", "beta"],
            )

    def test_guarded_runner_preserves_empty_case_skip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cases_path = tmp_path / "cases.json"
            marker_path = tmp_path / "runner-called.txt"
            runner_path = tmp_path / "runner.sh"
            cases_path.write_text('{"cases": []}', encoding="utf-8")
            _write_executable(
                runner_path,
                '#!/usr/bin/env sh\nset -eu\nprintf "called\\n" > "$RUNNER_MARKER"\n',
            )

            env = os.environ.copy()
            env.update(
                {
                    "PYTHON": sys.executable,
                    "RUNNER_MARKER": str(marker_path),
                }
            )

            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPT.relative_to(REPO_ROOT)),
                    str(cases_path),
                    "Cases missing",
                    "Run: make ocrmine",
                    "No cases; skipping.",
                    "--",
                    str(runner_path),
                ],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "No cases; skipping.")
            self.assertFalse(marker_path.exists())


if __name__ == "__main__":
    unittest.main()
