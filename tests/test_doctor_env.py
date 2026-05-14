import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools import doctor_env


class DoctorEnvTests(unittest.TestCase):
    def test_expected_python_candidates_prefer_repo_dotvenv(self) -> None:
        candidates = doctor_env._expected_python_candidates(None)

        expected_prefix = [
            doctor_env.ROOT / ".venv" / "bin" / "python3.14",
            doctor_env.ROOT / ".venv" / "bin" / "python3",
            doctor_env.ROOT / ".venv" / "bin" / "python",
        ]
        self.assertEqual(candidates[:3], expected_prefix)

    def test_check_interpreter_accepts_repo_dotvenv_python314(self) -> None:
        current_python = doctor_env.ROOT / ".venv" / "bin" / "python3.14"
        stdout = io.StringIO()

        with patch.object(doctor_env.sys, "executable", str(current_python)):
            with patch.dict("os.environ", {"VIRTUAL_ENV": str(doctor_env.ROOT / ".venv")}, clear=True):
                with patch("tools.doctor_env._is_runnable_python") as is_runnable:
                    with patch("tools.doctor_env.shutil.which", return_value=str(current_python)):
                        is_runnable.side_effect = (
                            lambda path: path.parent.parent == doctor_env.ROOT / ".venv"
                        )
                        with redirect_stdout(stdout):
                            issues = doctor_env._check_interpreter()

        output = stdout.getvalue()
        self.assertEqual(issues, 0)
        self.assertIn("Interpreter:", output)
        self.assertIn("VIRTUAL_ENV=", output)
        self.assertNotIn("Interpreter mismatch", output)

    def test_check_interpreter_mismatch_points_to_dotvenv_activation(self) -> None:
        stdout = io.StringIO()
        current_python = Path("/usr/bin/python3")

        with patch.object(doctor_env.sys, "executable", str(current_python)):
            with patch.dict("os.environ", {"VIRTUAL_ENV": str(doctor_env.ROOT / ".venv")}, clear=True):
                with patch("tools.doctor_env._is_runnable_python") as is_runnable:
                    with patch("tools.doctor_env.shutil.which", return_value=str(current_python)):
                        is_runnable.side_effect = (
                            lambda path: path.parent.parent == doctor_env.ROOT / ".venv"
                        )
                        with redirect_stdout(stdout):
                            issues = doctor_env._check_interpreter()

        output = stdout.getvalue()
        self.assertEqual(issues, 1)
        self.assertIn("Interpreter mismatch", output)
        self.assertIn(str(doctor_env.ROOT / ".venv" / "bin" / "activate"), output)


if __name__ == "__main__":
    unittest.main()
