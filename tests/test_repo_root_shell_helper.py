from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER = REPO_ROOT / "tools" / "repo_root.sh"


class RepoRootShellHelperTests(unittest.TestCase):
    def test_helper_prints_repo_root_when_executed_directly(self) -> None:
        result = subprocess.run(
            ["bash", str(HELPER)],
            cwd=Path("/tmp"),
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.strip(), str(REPO_ROOT))

    def test_helper_cd_function_moves_to_repo_root(self) -> None:
        command = (
            f"source {HELPER}; "
            "polinko_cd_repo_root; "
            'printf "%s\\n%s\\n" "$POLINKO_REPO_ROOT" "$PWD"'
        )
        result = subprocess.run(
            ["bash", "-c", command],
            cwd=Path("/tmp"),
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.splitlines(), [str(REPO_ROOT), str(REPO_ROOT)])


if __name__ == "__main__":
    unittest.main()
