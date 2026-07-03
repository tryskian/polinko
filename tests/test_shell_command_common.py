import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER = REPO_ROOT / "tools" / "shell_command_common.sh"


class ShellCommandCommonTests(unittest.TestCase):
    def test_direct_execution_rejects_running_as_script(self) -> None:
        result = subprocess.run(
            ["/bin/sh", str(HELPER)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "Source this helper from runtime shell scripts instead of executing it directly.",
            result.stderr,
        )

    def test_command_available_accepts_shell_builtins(self) -> None:
        result = subprocess.run(
            ["/bin/sh", "-c", f'. "{HELPER}"; polinko_command_available :'],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_command_available_rejects_missing_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    "/bin/sh",
                    "-c",
                    (
                        f'. "{HELPER}"; '
                        f'PATH="{tmp}"; '
                        "polinko_command_available definitely-missing"
                    ),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1)

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

    def test_require_labeled_command_reports_missing_command_with_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    "/bin/sh",
                    "-c",
                    (
                        f'. "{HELPER}"; '
                        f'PATH="{tmp}"; '
                        "polinko_require_labeled_command definitely-missing "
                        '"bootstrap Python" "setup-devcontainer"'
                    ),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "setup-devcontainer: missing bootstrap Python command: definitely-missing",
            result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
