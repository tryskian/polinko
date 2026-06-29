import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER = REPO_ROOT / "tools" / "python_runtime.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class PythonRuntimeShellTests(unittest.TestCase):
    def _run_resolver(self, cwd: Path, env: dict[str, str] | None = None) -> str:
        result = subprocess.run(
            ["sh", "-c", f'. "{HELPER}"; polinko_default_python_bin'],
            cwd=cwd,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_python_override_wins(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            custom_python = root / "custom-python"
            _write_executable(custom_python, "#!/usr/bin/env sh\nexit 0\n")
            env = os.environ.copy()
            env["PYTHON"] = str(custom_python)

            self.assertEqual(self._run_resolver(root, env), str(custom_python))

    def test_python_override_must_resolve_to_executable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            env = os.environ.copy()
            env["PYTHON"] = str(Path(tmpdir) / "missing-python")

            result = subprocess.run(
                ["sh", "-c", f'. "{HELPER}"; polinko_default_python_bin'],
                cwd=tmpdir,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("Configured PYTHON is not executable", result.stderr)

    def test_repo_venv_python_is_preferred_before_system_python3(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            venv_python = root / ".venv" / "bin" / "python3.14"
            venv_python.parent.mkdir(parents=True)
            _write_executable(venv_python, "#!/usr/bin/env sh\nexit 0\n")
            env = os.environ.copy()
            env.pop("PYTHON", None)

            self.assertEqual(self._run_resolver(root, env), "./.venv/bin/python3.14")

    def test_system_python3_is_final_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            env = os.environ.copy()
            env.pop("PYTHON", None)

            self.assertEqual(self._run_resolver(Path(tmpdir), env), "python3")

    def test_helper_rejects_direct_execution(self) -> None:
        result = subprocess.run(
            ["sh", str(HELPER)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Source this helper", result.stderr)


if __name__ == "__main__":
    unittest.main()
