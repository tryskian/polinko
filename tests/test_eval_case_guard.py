import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "eval_case_guard.sh"


def _run_guard(cases_path: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHON"] = sys.executable
    script = (
        'set -eu; . "tools/eval_case_guard.sh"; '
        f'eval_case_guard_or_exit "{cases_path}" '
        '"Cases not found" "Run: make ocrmine" "No cases available"; '
        'echo "after guard"'
    )
    return subprocess.run(
        ["/bin/sh", "-c", script],
        capture_output=True,
        cwd=REPO_ROOT,
        env=env,
        text=True,
    )


class EvalCaseGuardTests(unittest.TestCase):
    def test_existing_non_empty_cases_continue_recipe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases_path = Path(tmp) / "cases.json"
            cases_path.write_text('{"cases": [{"id": "a"}]}', encoding="utf-8")

            result = _run_guard(cases_path)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "after guard")

    def test_missing_cases_fail_with_hint(self) -> None:
        result = _run_guard(Path("/tmp/polinko-no-such-cases.json"))

        self.assertEqual(result.returncode, 1)
        self.assertIn("Cases not found: /tmp/polinko-no-such-cases.json", result.stdout)
        self.assertIn("Run: make ocrmine", result.stdout)
        self.assertNotIn("after guard", result.stdout)

    def test_empty_cases_skip_recipe_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases_path = Path(tmp) / "cases.json"
            cases_path.write_text('{"cases": []}', encoding="utf-8")

            result = _run_guard(cases_path)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "No cases available")

    def test_direct_execution_is_rejected(self) -> None:
        result = subprocess.run(
            ["/bin/sh", str(SCRIPT)],
            capture_output=True,
            cwd=REPO_ROOT,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Source this helper", result.stderr)


if __name__ == "__main__":
    unittest.main()
