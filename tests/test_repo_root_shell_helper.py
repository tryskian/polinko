from __future__ import annotations

import shutil
import subprocess
import tempfile
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

    def test_default_python_prefers_env_override(self) -> None:
        command = (
            f"source {HELPER}; "
            "polinko_cd_repo_root; "
            "PYTHON=/tmp/custom-python polinko_default_python_bin"
        )
        result = subprocess.run(
            ["bash", "-c", command],
            cwd=Path("/tmp"),
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.strip(), "/tmp/custom-python")

    def test_default_python_prefers_local_venv_when_unset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake_repo = Path(tmp)
            tools_dir = fake_repo / "tools"
            venv_dir = fake_repo / ".venv" / "bin"
            tools_dir.mkdir()
            venv_dir.mkdir(parents=True)
            shutil.copy(HELPER, tools_dir / "repo_root.sh")
            fake_python = venv_dir / "python"
            fake_python.write_text("#!/usr/bin/env sh\nprintf 'Python 3.14.0\\n'\n")
            fake_python.chmod(0o755)

            command = (
                f"source {tools_dir / 'repo_root.sh'}; "
                "polinko_cd_repo_root; "
                "unset PYTHON; "
                "polinko_default_python_bin"
            )
            result = subprocess.run(
                ["bash", "-c", command],
                cwd=Path("/tmp"),
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.stdout.strip(), "./.venv/bin/python")


if __name__ == "__main__":
    unittest.main()
