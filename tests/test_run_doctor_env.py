from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from tools import run_doctor_env


class RunDoctorEnvTests(unittest.TestCase):
    def test_interpreter_source_uses_make_origin(self) -> None:
        self.assertEqual(
            run_doctor_env.interpreter_source_label("python", "command line"),
            "command-line PYTHON override",
        )
        self.assertEqual(
            run_doctor_env.interpreter_source_label("python", "environment"),
            "environment PYTHON override",
        )
        self.assertEqual(
            run_doctor_env.interpreter_source_label("python", "environment override"),
            "environment PYTHON override",
        )

    def test_interpreter_source_uses_make_python_shape(self) -> None:
        self.assertEqual(
            run_doctor_env.interpreter_source_label(".venv/bin/python3.14", "file"),
            "repo .venv selected by Make",
        )
        self.assertEqual(
            run_doctor_env.interpreter_source_label("python3", "file"),
            "host python3 fallback selected by Make",
        )
        self.assertEqual(
            run_doctor_env.interpreter_source_label("/opt/bin/python3.14", "file"),
            "make PYTHON",
        )

    def test_active_venv_is_derived_from_python_bin_path(self) -> None:
        cwd = Path("/repo")

        self.assertEqual(
            run_doctor_env.active_venv_for_python(
                ".venv/bin/python3.14",
                cwd=cwd,
            ),
            "/repo/.venv",
        )
        self.assertIsNone(run_doctor_env.active_venv_for_python("python3", cwd=cwd))
        self.assertIsNone(
            run_doctor_env.active_venv_for_python("/opt/python3.14", cwd=cwd)
        )

    def test_runner_sets_doctor_environment_for_active_venv(self) -> None:
        completed = mock.Mock(returncode=0)

        with mock.patch.dict(os.environ, {"PATH": "/usr/bin"}, clear=True):
            with mock.patch(
                "tools.run_doctor_env.subprocess.run",
                return_value=completed,
            ) as run:
                status = run_doctor_env.run_doctor_env(
                    python_path=".venv/bin/python3.14",
                    python_origin="file",
                )

        self.assertEqual(status, 0)
        run.assert_called_once()
        args, kwargs = run.call_args
        self.assertEqual(args[0], [".venv/bin/python3.14", "-m", "tools.doctor_env"])
        env = kwargs["env"]
        self.assertEqual(
            env["POLINKO_DOCTOR_INTERPRETER_SOURCE"],
            "repo .venv selected by Make",
        )
        self.assertTrue(env["VIRTUAL_ENV"].endswith("/.venv"))
        self.assertTrue(env["PATH"].startswith(f"{env['VIRTUAL_ENV']}/bin:"))
        self.assertFalse(kwargs["check"])


if __name__ == "__main__":
    unittest.main()
