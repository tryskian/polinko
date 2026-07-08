from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from tools import run_dependency_lock


REPO_ROOT = Path(__file__).resolve().parents[1]


def _pip_tools_version() -> str:
    text = (REPO_ROOT / "makefiles" / "config" / "build.mk").read_text(encoding="utf-8")
    match = re.search(r"(?m)^PIP_TOOLS_VERSION \?= (?P<version>\S+)$", text)
    if match is None:
        raise AssertionError("PIP_TOOLS_VERSION missing from build config")
    return match.group("version")


class RunDependencyLockTests(unittest.TestCase):
    def test_bootstrap_skips_install_when_piptools_exists(self) -> None:
        pip_tools_version = _pip_tools_version()
        version = mock.Mock(returncode=0)
        compile_run = mock.Mock(returncode=0)

        with mock.patch(
            "tools.run_dependency_lock.subprocess.run",
            side_effect=[version, compile_run],
        ) as run:
            with mock.patch("builtins.print"):
                status = run_dependency_lock.run_dependency_lock(
                    python="python3",
                    requirements_in="requirements.in",
                    requirements_lock="requirements.txt",
                    ensure_bootstrap=True,
                    pip_tools_version=pip_tools_version,
                    check_lockfile=False,
                )

        self.assertEqual(status, 0)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(
            run.call_args_list[0].args[0],
            ["python3", "-m", "piptools", "--version"],
        )
        self.assertEqual(
            run.call_args_list[1].args[0],
            [
                "python3",
                "-m",
                "piptools",
                "compile",
                "--resolver=backtracking",
                "--allow-unsafe",
                "--strip-extras",
                "--output-file",
                "requirements.txt",
                "requirements.in",
            ],
        )
        self.assertEqual(run.call_args_list[1].kwargs["capture_output"], True)
        self.assertEqual(run.call_args_list[1].kwargs["text"], True)

    def test_bootstrap_installs_missing_piptools_before_compile(self) -> None:
        pip_tools_version = _pip_tools_version()
        version = mock.Mock(returncode=1)
        install = mock.Mock(returncode=0)
        compile_run = mock.Mock(returncode=0)

        with mock.patch(
            "tools.run_dependency_lock.subprocess.run",
            side_effect=[version, install, compile_run],
        ) as run:
            with mock.patch("builtins.print"):
                status = run_dependency_lock.run_dependency_lock(
                    python=".venv/bin/python",
                    requirements_in="requirements.in",
                    requirements_lock="requirements.txt",
                    ensure_bootstrap=True,
                    pip_tools_version=pip_tools_version,
                    check_lockfile=False,
                )

        self.assertEqual(status, 0)
        self.assertEqual(
            run.call_args_list[1].args[0],
            [
                ".venv/bin/python",
                "-m",
                "pip",
                "install",
                f"pip-tools=={pip_tools_version}",
            ],
        )

    def test_install_failure_stops_before_compile(self) -> None:
        pip_tools_version = _pip_tools_version()
        version = mock.Mock(returncode=1)
        install = mock.Mock(returncode=2)

        with mock.patch(
            "tools.run_dependency_lock.subprocess.run",
            side_effect=[version, install],
        ) as run:
            status = run_dependency_lock.run_dependency_lock(
                python="python3",
                requirements_in="requirements.in",
                requirements_lock="requirements.txt",
                ensure_bootstrap=True,
                pip_tools_version=pip_tools_version,
                check_lockfile=False,
            )

        self.assertEqual(status, 2)
        self.assertEqual(run.call_count, 2)

    def test_check_mode_compiles_and_verifies_lockfile_diff(self) -> None:
        compile_run = mock.Mock(returncode=0)
        diff_run = mock.Mock(returncode=0)

        with mock.patch(
            "tools.run_dependency_lock.subprocess.run",
            side_effect=[compile_run, diff_run],
        ) as run:
            with mock.patch("builtins.print"):
                status = run_dependency_lock.run_dependency_lock(
                    python="python3",
                    requirements_in="requirements.in",
                    requirements_lock="requirements.txt",
                    ensure_bootstrap=False,
                    pip_tools_version=None,
                    check_lockfile=True,
                )

        self.assertEqual(status, 0)
        self.assertEqual(
            run.call_args_list[1].args[0],
            [
                "git",
                "diff",
                "--exit-code",
                "--",
                "requirements.txt",
            ],
        )

    def test_compile_failure_skips_lockfile_diff(self) -> None:
        compile_run = subprocess.CompletedProcess(
            args=["python3", "-m", "piptools", "compile"],
            returncode=3,
            stdout="",
            stderr="",
        )

        with mock.patch(
            "tools.run_dependency_lock.subprocess.run",
            return_value=compile_run,
        ) as run:
            status = run_dependency_lock.run_dependency_lock(
                python="python3",
                requirements_in="requirements.in",
                requirements_lock="requirements.txt",
                ensure_bootstrap=False,
                pip_tools_version=None,
                check_lockfile=True,
            )

        self.assertEqual(status, 3)
        self.assertEqual(run.call_count, 1)

    def test_compile_failure_emits_captured_output(self) -> None:
        compile_run = subprocess.CompletedProcess(
            args=["python3", "-m", "piptools", "compile"],
            returncode=3,
            stdout="compile stdout\n",
            stderr="compile stderr\n",
        )

        with mock.patch(
            "tools.run_dependency_lock.subprocess.run",
            return_value=compile_run,
        ):
            with mock.patch("sys.stdout") as stdout:
                with mock.patch("sys.stderr") as stderr:
                    status = run_dependency_lock.compile_lockfile(
                        python="python3",
                        requirements_in="requirements.in",
                        requirements_lock="requirements.txt",
                    )

        self.assertEqual(status, 3)
        stdout.write.assert_called_once_with("compile stdout\n")
        stderr.write.assert_called_once_with("compile stderr\n")

    def test_check_mode_prints_concise_clean_status(self) -> None:
        compile_run = mock.Mock(returncode=0)
        diff_run = mock.Mock(returncode=0)

        with mock.patch(
            "tools.run_dependency_lock.subprocess.run",
            side_effect=[compile_run, diff_run],
        ):
            with mock.patch("builtins.print") as print_mock:
                status = run_dependency_lock.run_dependency_lock(
                    python="python3",
                    requirements_in="requirements.in",
                    requirements_lock="requirements.txt",
                    ensure_bootstrap=False,
                    pip_tools_version=None,
                    check_lockfile=True,
                )

        self.assertEqual(status, 0)
        print_mock.assert_any_call(
            "dependency-lock: compiled requirements.txt from requirements.in"
        )
        print_mock.assert_any_call("dependency-lock: requirements.txt is current")

    def test_cli_requires_version_when_bootstrap_enabled(self) -> None:
        with self.assertRaises(SystemExit):
            with mock.patch("sys.stderr"):
                run_dependency_lock.parse_args(
                    [
                        "--python",
                        "python3",
                        "--requirements-in",
                        "requirements.in",
                        "--requirements-lock",
                        "requirements.txt",
                        "--ensure-pip-tools",
                    ]
                )


if __name__ == "__main__":
    unittest.main()
