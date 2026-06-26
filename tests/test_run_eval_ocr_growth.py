import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GROWTH_CASES_SCRIPT = REPO_ROOT / "tools" / "run_eval_ocr_growth_cases.sh"
GROWTH_BATCH_SCRIPT = REPO_ROOT / "tools" / "run_eval_ocr_growth_batched.sh"
GROWTH_STABILITY_SCRIPT = REPO_ROOT / "tools" / "run_eval_ocr_growth_stability.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _stub_env(tmp_path: Path) -> tuple[dict[str, str], Path, Path, Path, Path]:
    server_marker = tmp_path / "server-called"
    args_file = tmp_path / "python-args.txt"
    env_file = tmp_path / "python-env.txt"
    cwd_file = tmp_path / "python-cwd.txt"
    server_script = tmp_path / "server.sh"
    python_script = tmp_path / "python.sh"

    _write_executable(
        server_script,
        '#!/usr/bin/env sh\nset -eu\nprintf "server\\n" > "$SERVER_MARKER"\n',
    )
    _write_executable(
        python_script,
        (
            "#!/usr/bin/env sh\n"
            "set -eu\n"
            '[ -f "$SERVER_MARKER" ] || exit 7\n'
            'pwd > "$PYTHON_CWD"\n'
            'printf "%s\\n" "$@" > "$PYTHON_ARGS"\n'
            'printf "%s\\n" "${PYTHONUNBUFFERED:-}" > "$PYTHON_ENV"\n'
        ),
    )

    env = os.environ.copy()
    env.update(
        {
            "PYTHON": str(python_script),
            "EVAL_SERVER_DAEMON_SCRIPT": str(server_script),
            "SERVER_MARKER": str(server_marker),
            "PYTHON_ARGS": str(args_file),
            "PYTHON_ENV": str(env_file),
            "PYTHON_CWD": str(cwd_file),
        }
    )
    return env, server_marker, args_file, env_file, cwd_file


class RunEvalOcrGrowthTests(unittest.TestCase):
    def test_growth_cases_runs_server_before_eval_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            subdir = tmp_path / "subdir"
            subdir.mkdir()
            env, server_marker, args_file, env_file, cwd_file = _stub_env(tmp_path)

            result = subprocess.run(
                [
                    "bash",
                    str(GROWTH_CASES_SCRIPT),
                    "cases.json",
                    "12",
                    "2",
                    "9",
                    "3",
                    "44",
                    "5",
                ],
                cwd=subdir,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(server_marker.read_text(encoding="utf-8"), "server\n")
            self.assertEqual(env_file.read_text(encoding="utf-8"), "1\n")
            self.assertEqual(
                cwd_file.read_text(encoding="utf-8").strip(), str(REPO_ROOT)
            )
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "tools.eval_ocr",
                    "--timeout",
                    "12",
                    "--cases",
                    "cases.json",
                    "--show-text",
                    "--offset",
                    "2",
                    "--max-cases",
                    "9",
                    "--ocr-retries",
                    "3",
                    "--ocr-retry-delay-ms",
                    "44",
                    "--max-consecutive-rate-limit-errors",
                    "5",
                ],
            )

    def test_growth_batched_runs_server_before_batched_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            subdir = tmp_path / "subdir"
            subdir.mkdir()
            env, server_marker, args_file, env_file, cwd_file = _stub_env(tmp_path)

            result = subprocess.run(
                [
                    "bash",
                    str(GROWTH_BATCH_SCRIPT),
                    "cases.json",
                    "40",
                    "3",
                    "44",
                    "2",
                    "9",
                    "runs-dir",
                    "summary.json",
                    "summary.md",
                ],
                cwd=subdir,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(server_marker.read_text(encoding="utf-8"), "server\n")
            self.assertEqual(env_file.read_text(encoding="utf-8"), "1\n")
            self.assertEqual(
                cwd_file.read_text(encoding="utf-8").strip(), str(REPO_ROOT)
            )
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "tools.eval_ocr_batched",
                    "--base-url",
                    "http://127.0.0.1:8000",
                    "--cases",
                    "cases.json",
                    "--batch-size",
                    "40",
                    "--ocr-retries",
                    "3",
                    "--ocr-retry-delay-ms",
                    "44",
                    "--offset",
                    "2",
                    "--max-cases",
                    "9",
                    "--report-dir",
                    "runs-dir",
                    "--output-json",
                    "summary.json",
                    "--output-markdown",
                    "summary.md",
                ],
            )

    def test_growth_stability_runs_server_before_stability_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            subdir = tmp_path / "subdir"
            subdir.mkdir()
            env, server_marker, args_file, env_file, cwd_file = _stub_env(tmp_path)

            result = subprocess.run(
                [
                    "bash",
                    str(GROWTH_STABILITY_SCRIPT),
                    "cases.json",
                    "5",
                    "2",
                    "9",
                    "12",
                    "3",
                    "44",
                    "55",
                    "66",
                    "7",
                    "runs-dir",
                    "stability.json",
                ],
                cwd=subdir,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(server_marker.read_text(encoding="utf-8"), "server\n")
            self.assertEqual(env_file.read_text(encoding="utf-8"), "1\n")
            self.assertEqual(
                cwd_file.read_text(encoding="utf-8").strip(), str(REPO_ROOT)
            )
            self.assertEqual(
                args_file.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "tools.eval_ocr_stability",
                    "--base-url",
                    "http://127.0.0.1:8000",
                    "--cases",
                    "cases.json",
                    "--runs",
                    "5",
                    "--offset",
                    "2",
                    "--max-cases",
                    "9",
                    "--timeout",
                    "12",
                    "--ocr-retries",
                    "3",
                    "--ocr-retry-delay-ms",
                    "44",
                    "--case-delay-ms",
                    "55",
                    "--rate-limit-cooldown-ms",
                    "66",
                    "--max-consecutive-rate-limit-errors",
                    "7",
                    "--stop-on-rate-limit-abort",
                    "--report-dir",
                    "runs-dir",
                    "--output-json",
                    "stability.json",
                ],
            )

    def test_growth_scripts_require_exact_arguments(self) -> None:
        for script in (
            GROWTH_CASES_SCRIPT,
            GROWTH_BATCH_SCRIPT,
            GROWTH_STABILITY_SCRIPT,
        ):
            with self.subTest(script=script.name):
                result = subprocess.run(
                    ["bash", str(script.relative_to(REPO_ROOT)), "cases.json"],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 2)
                self.assertIn("Usage:", result.stderr)


if __name__ == "__main__":
    unittest.main()
