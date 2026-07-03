import os
import signal
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_EVALS = REPO_ROOT / "makefiles" / "config" / "evals.mk"
RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_local_eval_gate.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _kill_pid_file(path: Path) -> None:
    if not path.exists():
        return
    raw_pid = path.read_text(encoding="utf-8").strip()
    if not raw_pid:
        return
    try:
        os.kill(int(raw_pid), signal.SIGKILL)
    except ProcessLookupError:
        pass


def _makefile_source_text(path: Path, seen: set[Path] | None = None) -> str:
    if seen is None:
        seen = set()
    resolved_path = path.resolve()
    if resolved_path in seen:
        return ""
    seen.add(resolved_path)

    text = path.read_text(encoding="utf-8")
    source_texts = [text]
    for line in text.splitlines():
        if line.startswith("include "):
            for include_path in line.removeprefix("include ").split():
                source_texts.append(
                    _makefile_source_text(REPO_ROOT / include_path, seen)
                )
    return "\n".join(source_texts)


class RunLocalEvalGateTests(unittest.TestCase):
    def test_default_smoke_resources_are_run_scoped(self) -> None:
        config = _makefile_source_text(CONFIG_EVALS)
        runner = RUNNER_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("SMOKE_PORT ?=\n", config)
        self.assertIn("SMOKE_BASE_URL ?=\n", config)
        self.assertIn("SMOKE_HISTORY_DB ?=\n", config)
        self.assertIn("source=tools/python_runtime.sh", runner)
        self.assertIn('. "$script_dir/python_runtime.sh"', runner)
        self.assertIn("python_bin=$(polinko_default_python_bin)", runner)
        self.assertIn(
            "local_eval_gate_temp_root=${LOCAL_EVAL_GATE_TEMP_ROOT:-/tmp}",
            runner,
        )
        self.assertIn("temp_artifact_path()", runner)
        self.assertIn(
            'polinko_join_path "$local_eval_gate_temp_root" "$1"',
            runner,
        )
        self.assertIn("LOCAL_EVAL_GATE_START_ATTEMPTS ?= 100", config)
        self.assertIn("LOCAL_EVAL_GATE_START_SLEEP_SECONDS ?= 0.2", config)
        self.assertIn("LOCAL_EVAL_GATE_TEMP_ROOT ?= /tmp", config)
        self.assertIn(
            'LOCAL_EVAL_GATE_TEMP_ROOT="$(LOCAL_EVAL_GATE_TEMP_ROOT)"',
            config,
        )
        self.assertIn(
            'LOCAL_EVAL_GATE_START_ATTEMPTS="$(LOCAL_EVAL_GATE_START_ATTEMPTS)"',
            config,
        )
        self.assertIn(
            'LOCAL_EVAL_GATE_START_SLEEP_SECONDS="$(LOCAL_EVAL_GATE_START_SLEEP_SECONDS)"',
            config,
        )
        self.assertIn(
            "local_eval_gate_start_attempts=${LOCAL_EVAL_GATE_START_ATTEMPTS-100}",
            runner,
        )
        self.assertIn(
            'while [ "$attempt" -lt "$local_eval_gate_start_attempts" ]; do',
            runner,
        )
        self.assertIn('sleep "$local_eval_gate_start_sleep_seconds"', runner)
        self.assertIn(
            '$(temp_artifact_path "polinko-eval-smoke-$$-history.db")',
            runner,
        )
        self.assertIn(
            '$(temp_artifact_path "polinko-eval-smoke-$$-memory.db")',
            runner,
        )
        self.assertIn(
            '$(temp_artifact_path "polinko-eval-smoke-$$-vector.db")',
            runner,
        )

    def _base_env(self, tmp_path: Path) -> tuple[dict[str, str], Path, Path]:
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()

        python_args = tmp_path / "python-args.tsv"
        curl_args = tmp_path / "curl-args.txt"
        server_started = tmp_path / "server-started"
        server_env_path = tmp_path / "server-env.tsv"
        python_script = bin_dir / "python.sh"
        curl_script = bin_dir / "curl"
        sleep_script = bin_dir / "sleep"

        _write_executable(
            python_script,
            """#!/usr/bin/env sh
set -eu
if [ "${1:-}" = "-" ]; then
\tprintf "%s\\n" "${DYNAMIC_PORT:-9993}"
\texit 0
fi
first=1
for arg in "$@"; do
\tif [ "$first" -eq 1 ]; then
\t\tprintf "%s" "$arg" >> "$PYTHON_ARGS"
\t\tfirst=0
\telse
\t\tprintf "\\t%s" "$arg" >> "$PYTHON_ARGS"
\tfi
done
printf "\\n" >> "$PYTHON_ARGS"
if [ "${1:-}" = "-m" ] && [ "${2:-}" = "uvicorn" ]; then
\tif [ -n "${SERVER_ENV_PATH:-}" ]; then
\t\t{
\t\t\tprintf "POLINKO_HISTORY_DB_PATH\\t%s\\n" "${POLINKO_HISTORY_DB_PATH:-}"
\t\t\tprintf "POLINKO_MEMORY_DB_PATH\\t%s\\n" "${POLINKO_MEMORY_DB_PATH:-}"
\t\t\tprintf "POLINKO_VECTOR_DB_PATH\\t%s\\n" "${POLINKO_VECTOR_DB_PATH:-}"
\t\t\tprintf "POLINKO_SESSION_DB_PATH\\t%s\\n" "${POLINKO_SESSION_DB_PATH:-}"
\t\t} >> "$SERVER_ENV_PATH"
\tfi
\t: > "$SERVER_STARTED"
\tprintf "%s" "$$" > "$SERVER_PID_PATH"
\tif [ "${UVICORN_EXIT_IMMEDIATELY:-0}" = "1" ]; then
\t\texit 1
\tfi
\tif [ "${UVICORN_IGNORE_TERM:-0}" = "1" ]; then
\t\texec /bin/sh -c 'trap "" TERM; while :; do /bin/sleep 1; done'
\tfi
\texec /bin/sleep 30
fi
""",
        )
        _write_executable(
            curl_script,
            """#!/usr/bin/env sh
set -eu
printf "%s\\n" "$*" >> "$CURL_ARGS"
if [ "${CURL_EXIT:-0}" = "0" ]; then
\twait_count=0
\twhile [ ! -f "$SERVER_STARTED" ] && [ "$wait_count" -lt 100 ]; do
\t\twait_count=$((wait_count + 1))
\t\t/bin/sleep 0.01
\tdone
fi
exit "${CURL_EXIT:-0}"
""",
        )
        _write_executable(sleep_script, "#!/usr/bin/env sh\nexit 0\n")

        smoke_history_db = tmp_path / "smoke-history.db"
        smoke_memory_db = tmp_path / "smoke-memory.db"
        smoke_vector_db = tmp_path / "smoke-vector.db"
        gate_session_db = tmp_path / "gate-session.db"
        gate_vector_db = tmp_path / "gate-vector.db"
        server_pid_path = tmp_path / "server.pid"
        for path in (
            smoke_history_db,
            smoke_memory_db,
            smoke_vector_db,
            gate_session_db,
            gate_vector_db,
        ):
            path.write_text("stale", encoding="utf-8")

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{bin_dir}{os.pathsep}{env['PATH']}",
                "PYTHON": str(python_script),
                "PYTHON_ARGS": str(python_args),
                "CURL_ARGS": str(curl_args),
                "SERVER_STARTED": str(server_started),
                "SERVER_ENV_PATH": str(server_env_path),
                "SERVER_PID_PATH": str(server_pid_path),
                "ASGI_APP": "custom_server:app",
                "SMOKE_PORT": "9991",
                "SMOKE_BASE_URL": "http://127.0.0.1:9991",
                "SMOKE_HISTORY_DB": str(smoke_history_db),
                "SMOKE_MEMORY_DB": str(smoke_memory_db),
                "SMOKE_VECTOR_DB": str(smoke_vector_db),
                "GATE_PORT": "9992",
                "GATE_BASE_URL": "http://127.0.0.1:9992",
                "GATE_SESSION_DB": str(gate_session_db),
                "GATE_VECTOR_DB": str(gate_vector_db),
                "RETRIEVAL_REQUEST_RETRIES": "4",
                "RETRIEVAL_REQUEST_RETRY_DELAY_MS": "321",
                "RETRIEVAL_CHAT_HARNESS_MODE": "fixture",
                "OCR_EVAL_TIMEOUT": "13",
                "OCR_EVAL_OCR_RETRIES": "5",
                "OCR_EVAL_OCR_RETRY_DELAY_MS": "610",
                "OCR_MAX_CONSEC_RATE_LIMIT_ERRORS": "7",
                "STYLE_CASE_ATTEMPTS": "6",
                "STYLE_MIN_PASS_ATTEMPTS": "2",
                "STYLE_EVAL_MODE": "deterministic",
                "STYLE_CHAT_HARNESS_MODE": "fixture",
                "RESPONSE_BEHAVIOUR_CHAT_HARNESS_MODE": "fixture",
                "GATE_VECTOR_EMBEDDING_PROVIDER": "local",
                "HALLUCINATION_EVAL_MODE": "deterministic",
                "HALLUCINATION_JUDGE_MODEL": "judge-model",
                "HALLUCINATION_JUDGE_API_KEY_ENV": "JUDGE_KEY",
                "HALLUCINATION_JUDGE_BASE_URL": "http://judge.local",
                "HALLUCINATION_MIN_ACCEPTABLE_SCORE": "8",
                "HALLUCINATION_CHAT_HARNESS_MODE": "fixture",
            }
        )
        return env, python_args, server_started

    def _run_suite(
        self, suite: str, env: dict[str, str]
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(RUNNER_SCRIPT.relative_to(REPO_ROOT)), suite],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

    def _read_calls(self, path: Path) -> list[list[str]]:
        return [
            line.split("\t")
            for line in path.read_text(encoding="utf-8").splitlines()
            if line
        ]

    def _read_env_rows(self, env: dict[str, str]) -> dict[str, str]:
        env_path = Path(env["SERVER_ENV_PATH"])
        if not env_path.exists():
            return {}
        return {
            key: value
            for key, value in (
                line.split("\t", 1)
                for line in env_path.read_text(encoding="utf-8").splitlines()
                if line
            )
        }

    def test_local_eval_gate_suites_run_expected_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            expected_calls = {
                "api-smoke": [
                    [
                        "-m",
                        "uvicorn",
                        "custom_server:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "9991",
                    ],
                    ["-m", "tools.api_smoke", "--base-url", "http://127.0.0.1:9991"],
                ],
                "eval-smoke": [
                    [
                        "-m",
                        "uvicorn",
                        "custom_server:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "9991",
                    ],
                    ["-m", "tools.api_smoke", "--base-url", "http://127.0.0.1:9991"],
                    [
                        "-m",
                        "tools.eval_response_behaviour",
                        "--base-url",
                        "http://127.0.0.1:9991",
                        "--strict",
                    ],
                    [
                        "-m",
                        "tools.eval_retrieval",
                        "--base-url",
                        "http://127.0.0.1:9991",
                        "--request-retries",
                        "4",
                        "--request-retry-delay-ms",
                        "321",
                        "--chat-harness-mode",
                        "fixture",
                    ],
                    [
                        "-m",
                        "tools.eval_file_search",
                        "--base-url",
                        "http://127.0.0.1:9991",
                    ],
                ],
                "hallucination-gate": [
                    [
                        "-m",
                        "uvicorn",
                        "custom_server:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "9992",
                    ],
                    [
                        "-m",
                        "tools.eval_hallucination",
                        "--base-url",
                        "http://127.0.0.1:9992",
                        "--strict",
                        "--evaluation-mode",
                        "deterministic",
                        "--judge-model",
                        "judge-model",
                        "--judge-api-key-env",
                        "JUDGE_KEY",
                        "--judge-base-url",
                        "http://judge.local",
                        "--chat-harness-mode",
                        "fixture",
                        "--min-acceptable-score",
                        "8",
                    ],
                ],
                "quality-gate": [
                    [
                        "-m",
                        "uvicorn",
                        "custom_server:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "9992",
                    ],
                    ["-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
                    [
                        "-m",
                        "tools.eval_retrieval",
                        "--base-url",
                        "http://127.0.0.1:9992",
                        "--request-retries",
                        "4",
                        "--request-retry-delay-ms",
                        "321",
                        "--chat-harness-mode",
                        "fixture",
                    ],
                    [
                        "-m",
                        "tools.eval_file_search",
                        "--base-url",
                        "http://127.0.0.1:9992",
                    ],
                    [
                        "-m",
                        "tools.eval_ocr",
                        "--timeout",
                        "13",
                        "--base-url",
                        "http://127.0.0.1:9992",
                        "--strict",
                        "--ocr-retries",
                        "5",
                        "--ocr-retry-delay-ms",
                        "610",
                        "--max-consecutive-rate-limit-errors",
                        "7",
                    ],
                    [
                        "-m",
                        "tools.eval_style",
                        "--base-url",
                        "http://127.0.0.1:9992",
                        "--strict",
                        "--case-attempts",
                        "6",
                        "--min-pass-attempts",
                        "2",
                        "--evaluation-mode",
                        "deterministic",
                        "--chat-harness-mode",
                        "fixture",
                    ],
                    [
                        "-m",
                        "tools.eval_response_behaviour",
                        "--base-url",
                        "http://127.0.0.1:9992",
                        "--strict",
                        "--chat-harness-mode",
                        "fixture",
                    ],
                    [
                        "-m",
                        "tools.eval_hallucination",
                        "--base-url",
                        "http://127.0.0.1:9992",
                        "--strict",
                        "--evaluation-mode",
                        "deterministic",
                        "--judge-model",
                        "judge-model",
                        "--judge-api-key-env",
                        "JUDGE_KEY",
                        "--judge-base-url",
                        "http://judge.local",
                        "--chat-harness-mode",
                        "fixture",
                        "--min-acceptable-score",
                        "8",
                    ],
                ],
            }

            for suite, expected in expected_calls.items():
                with self.subTest(suite=suite):
                    python_args.write_text("", encoding="utf-8")
                    server_started.unlink(missing_ok=True)

                    result = self._run_suite(suite, env)

                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(self._read_calls(python_args), expected)

    def test_temp_root_override_controls_default_smoke_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, _python_args, server_started = self._base_env(Path(tmp))
            temp_root = Path(tmp) / "gate-temp-root"
            env["LOCAL_EVAL_GATE_TEMP_ROOT"] = f"{temp_root}/"
            for name in (
                "SMOKE_HISTORY_DB",
                "SMOKE_MEMORY_DB",
                "SMOKE_VECTOR_DB",
                "GATE_SESSION_DB",
                "GATE_VECTOR_DB",
            ):
                env.pop(name)
            server_started.unlink(missing_ok=True)

            result = self._run_suite("api-smoke", env)

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = self._read_env_rows(env)
            expected_names = {
                "POLINKO_HISTORY_DB_PATH": r"polinko-eval-smoke-\d+-history\.db",
                "POLINKO_MEMORY_DB_PATH": r"polinko-eval-smoke-\d+-memory\.db",
                "POLINKO_VECTOR_DB_PATH": r"polinko-eval-smoke-\d+-vector\.db",
            }
            for key, name_pattern in expected_names.items():
                path = Path(rows[key])
                self.assertEqual(path.parent, temp_root)
                self.assertRegex(path.name, name_pattern)
            self.assertEqual(rows["POLINKO_SESSION_DB_PATH"], "")
            self.assertTrue(temp_root.is_dir())

    def test_reports_blocked_temp_root_before_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            blocked_parent = Path(tmp) / "blocked-parent"
            blocked_parent.write_text("not a directory", encoding="utf-8")
            env["LOCAL_EVAL_GATE_TEMP_ROOT"] = str(blocked_parent / "child")
            server_started.unlink(missing_ok=True)

            result = self._run_suite("api-smoke", env)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                f"local eval gate failed to prepare temp root: {blocked_parent / 'child'}",
                result.stderr,
            )
            self.assertFalse(python_args.exists())

    def test_readiness_failure_stops_before_eval_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env["CURL_EXIT"] = "1"
            server_started.unlink(missing_ok=True)

            result = self._run_suite("api-smoke", env)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "Server failed to start. See /tmp/polinko-api-smoke.log", result.stdout
            )
            self.assertEqual(
                self._read_calls(python_args),
                [
                    [
                        "-m",
                        "uvicorn",
                        "custom_server:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "9991",
                    ]
                ],
            )

    def test_readiness_attempts_are_configurable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env["CURL_EXIT"] = "1"
            env["LOCAL_EVAL_GATE_START_ATTEMPTS"] = "3"
            env["LOCAL_EVAL_GATE_START_SLEEP_SECONDS"] = "0"
            server_started.unlink(missing_ok=True)

            result = self._run_suite("api-smoke", env)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "Server failed to start. See /tmp/polinko-api-smoke.log",
                result.stdout,
            )
            self.assertEqual(len(Path(env["CURL_ARGS"]).read_text().splitlines()), 3)
            self.assertEqual(
                self._read_calls(python_args),
                [
                    [
                        "-m",
                        "uvicorn",
                        "custom_server:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "9991",
                    ]
                ],
            )

    def test_rejects_invalid_readiness_attempts_before_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env["LOCAL_EVAL_GATE_START_ATTEMPTS"] = "abc"
            server_started.unlink(missing_ok=True)

            result = self._run_suite("api-smoke", env)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "LOCAL_EVAL_GATE_START_ATTEMPTS must be a positive integer",
                result.stderr,
            )
            self.assertFalse(python_args.exists())

    def test_rejects_empty_readiness_attempts_before_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env["LOCAL_EVAL_GATE_START_ATTEMPTS"] = ""
            server_started.unlink(missing_ok=True)

            result = self._run_suite("api-smoke", env)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "LOCAL_EVAL_GATE_START_ATTEMPTS must be a positive integer",
                result.stderr,
            )
            self.assertFalse(python_args.exists())

    def test_rejects_invalid_readiness_sleep_before_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env["LOCAL_EVAL_GATE_START_SLEEP_SECONDS"] = "-1"
            server_started.unlink(missing_ok=True)

            result = self._run_suite("api-smoke", env)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "LOCAL_EVAL_GATE_START_SLEEP_SECONDS "
                "must be a non-negative decimal number",
                result.stderr,
            )
            self.assertFalse(python_args.exists())

    def test_rejects_empty_readiness_sleep_before_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env["LOCAL_EVAL_GATE_START_SLEEP_SECONDS"] = ""
            server_started.unlink(missing_ok=True)

            result = self._run_suite("api-smoke", env)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "LOCAL_EVAL_GATE_START_SLEEP_SECONDS "
                "must be a non-negative decimal number",
                result.stderr,
            )
            self.assertFalse(python_args.exists())

    def test_rejects_invalid_smoke_port_before_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env["SMOKE_PORT"] = "abc"
            server_started.unlink(missing_ok=True)

            result = self._run_suite("api-smoke", env)

            self.assertEqual(result.returncode, 1)
            self.assertIn("SMOKE_PORT must be", result.stderr)
            self.assertFalse(python_args.exists())

    def test_api_smoke_ignores_unrelated_invalid_gate_port(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env["GATE_PORT"] = "abc"
            server_started.unlink(missing_ok=True)

            result = self._run_suite("api-smoke", env)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                self._read_calls(python_args),
                [
                    [
                        "-m",
                        "uvicorn",
                        "custom_server:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "9991",
                    ],
                    ["-m", "tools.api_smoke", "--base-url", "http://127.0.0.1:9991"],
                ],
            )

    def test_rejects_invalid_gate_port_before_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env["GATE_PORT"] = "70000"
            server_started.unlink(missing_ok=True)

            result = self._run_suite("quality-gate", env)

            self.assertEqual(result.returncode, 1)
            self.assertIn("GATE_PORT must be", result.stderr)
            self.assertFalse(python_args.exists())

    def test_quality_gate_ignores_unrelated_invalid_smoke_port(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env["SMOKE_PORT"] = "abc"
            server_started.unlink(missing_ok=True)

            result = self._run_suite("quality-gate", env)

            self.assertEqual(result.returncode, 0, result.stderr)
            calls = self._read_calls(python_args)
            self.assertEqual(
                calls[0],
                [
                    "-m",
                    "uvicorn",
                    "custom_server:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "9992",
                ],
            )

    def test_rejects_smoke_base_url_port_mismatch_before_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env["SMOKE_PORT"] = "9991"
            env["SMOKE_BASE_URL"] = "http://127.0.0.1:9992"
            server_started.unlink(missing_ok=True)

            result = self._run_suite("api-smoke", env)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "SMOKE_BASE_URL port must match 9991",
                result.stderr,
            )
            self.assertFalse(python_args.exists())

    def test_rejects_gate_base_url_without_explicit_port_before_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env["GATE_PORT"] = "9992"
            env["GATE_BASE_URL"] = "http://127.0.0.1"
            server_started.unlink(missing_ok=True)

            result = self._run_suite("quality-gate", env)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "GATE_BASE_URL must include an explicit port matching 9992",
                result.stderr,
            )
            self.assertFalse(python_args.exists())

    def test_cleanup_failure_exits_nonzero_when_server_does_not_exit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env["UVICORN_IGNORE_TERM"] = "1"
            server_started.unlink(missing_ok=True)
            self.addCleanup(_kill_pid_file, Path(env["SERVER_PID_PATH"]))

            result = self._run_suite("api-smoke", env)

            self.assertEqual(result.returncode, 1)
            self.assertIn("Server PID", result.stderr)
            self.assertIn("did not exit after stop signal", result.stderr)
            self.assertEqual(
                self._read_calls(python_args),
                [
                    [
                        "-m",
                        "uvicorn",
                        "custom_server:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "9991",
                    ],
                    ["-m", "tools.api_smoke", "--base-url", "http://127.0.0.1:9991"],
                ],
            )

    def test_api_smoke_default_uses_dynamic_port(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env.pop("SMOKE_PORT")
            env.pop("SMOKE_BASE_URL")
            server_started.unlink(missing_ok=True)

            result = self._run_suite("api-smoke", env)

            self.assertEqual(result.returncode, 0, result.stderr)
            calls = self._read_calls(python_args)
            self.assertEqual(
                calls[0][0:5],
                ["-m", "uvicorn", "custom_server:app", "--host", "127.0.0.1"],
            )
            dynamic_port = calls[0][6]
            self.assertNotEqual(dynamic_port, "9991")
            self.assertEqual(calls[0][-2:], ["--port", dynamic_port])
            self.assertEqual(
                calls[1],
                [
                    "-m",
                    "tools.api_smoke",
                    "--base-url",
                    f"http://127.0.0.1:{dynamic_port}",
                ],
            )

    def test_api_smoke_runs_from_subdirectory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            server_started.unlink(missing_ok=True)

            result = subprocess.run(
                ["bash", "../tools/run_local_eval_gate.sh", "api-smoke"],
                cwd=REPO_ROOT / "docs",
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                self._read_calls(python_args),
                [
                    [
                        "-m",
                        "uvicorn",
                        "custom_server:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "9991",
                    ],
                    ["-m", "tools.api_smoke", "--base-url", "http://127.0.0.1:9991"],
                ],
            )

    def test_dead_server_stops_before_eval_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, python_args, server_started = self._base_env(Path(tmp))
            env["UVICORN_EXIT_IMMEDIATELY"] = "1"
            server_started.unlink(missing_ok=True)

            result = self._run_suite("api-smoke", env)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "Server failed to stay running. See /tmp/polinko-api-smoke.log",
                result.stdout,
            )
            self.assertEqual(
                self._read_calls(python_args),
                [
                    [
                        "-m",
                        "uvicorn",
                        "custom_server:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "9991",
                    ]
                ],
            )

    def test_local_eval_gate_rejects_unknown_or_missing_suite(self) -> None:
        for args in ([], ["unknown"]):
            with self.subTest(args=args):
                result = subprocess.run(
                    ["bash", str(RUNNER_SCRIPT.relative_to(REPO_ROOT)), *args],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 2)
                self.assertTrue(
                    "Usage:" in result.stderr
                    or "Unknown local eval gate suite" in result.stderr
                )


if __name__ == "__main__":
    unittest.main()
