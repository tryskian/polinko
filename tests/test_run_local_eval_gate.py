import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_local_eval_gate.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class RunLocalEvalGateTests(unittest.TestCase):
    def _base_env(self, tmp_path: Path) -> tuple[dict[str, str], Path, Path]:
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()

        python_args = tmp_path / "python-args.tsv"
        curl_args = tmp_path / "curl-args.txt"
        server_started = tmp_path / "server-started"
        python_script = bin_dir / "python.sh"
        curl_script = bin_dir / "curl"
        sleep_script = bin_dir / "sleep"

        _write_executable(
            python_script,
            """#!/usr/bin/env sh
set -eu
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
\t: > "$SERVER_STARTED"
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
