import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.count_eval_cases import count_cases


REPO_ROOT = Path(__file__).resolve().parents[1]


class CountEvalCasesTests(unittest.TestCase):
    def test_counts_cases_list(self) -> None:
        self.assertEqual(count_cases({"cases": [{"id": "a"}, {"id": "b"}]}), 2)

    def test_missing_cases_defaults_to_zero(self) -> None:
        self.assertEqual(count_cases({"summary": {"selected_cases": 2}}), 0)

    def test_wrong_cases_type_fails(self) -> None:
        with self.assertRaises(RuntimeError):
            count_cases({"cases": "not-a-list"})

    def test_cli_prints_case_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases_path = Path(tmp) / "cases.json"
            cases_path.write_text('{"cases": [{"id": "a"}]}', encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "tools.count_eval_cases", str(cases_path)],
                check=True,
                capture_output=True,
                cwd=REPO_ROOT,
                text=True,
            )

        self.assertEqual(result.stdout.strip(), "1")

    def test_cli_fails_for_non_object_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases_path = Path(tmp) / "cases.json"
            cases_path.write_text("[]", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "tools.count_eval_cases", str(cases_path)],
                check=False,
                capture_output=True,
                cwd=REPO_ROOT,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
