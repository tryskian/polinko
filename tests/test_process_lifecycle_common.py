import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER = REPO_ROOT / "tools" / "process_lifecycle_common.sh"


class ProcessLifecycleCommonTests(unittest.TestCase):
    def test_require_command_accepts_shell_builtins(self) -> None:
        result = subprocess.run(
            [
                "/bin/sh",
                "-c",
                f'. "{HELPER}"; polinko_require_command : "unit test"',
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_require_command_reports_missing_command_with_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    "/bin/sh",
                    "-c",
                    (
                        f'. "{HELPER}"; '
                        f'PATH="{tmp}"; '
                        'polinko_require_command definitely-missing "unit test"'
                    ),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "Missing required command for unit test: definitely-missing",
            result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
