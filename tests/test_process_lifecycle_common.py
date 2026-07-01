import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER = REPO_ROOT / "tools" / "process_lifecycle_common.sh"


class ProcessLifecycleCommonTests(unittest.TestCase):
    def test_pid_positive_integer_rejects_unsafe_values(self) -> None:
        for value in ("", "0", "000", "-1", "1 2", "abc"):
            with self.subTest(value=value):
                result = subprocess.run(
                    [
                        "/bin/sh",
                        "-c",
                        (f'. "{HELPER}"; polinko_pid_is_positive_integer "$TEST_PID"'),
                    ],
                    cwd=REPO_ROOT,
                    env={"TEST_PID": value},
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 1)

    def test_pid_is_running_rejects_unsafe_values(self) -> None:
        for value in ("", "0", "000", "-1", "1 2", "abc"):
            with self.subTest(value=value):
                result = subprocess.run(
                    [
                        "/bin/sh",
                        "-c",
                        f'. "{HELPER}"; polinko_pid_is_running "$TEST_PID"',
                    ],
                    cwd=REPO_ROOT,
                    env={"TEST_PID": value},
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 1)

    def test_pid_is_running_accepts_current_shell_pid(self) -> None:
        result = subprocess.run(
            ["/bin/sh", "-c", f'. "{HELPER}"; polinko_pid_is_running "$$"'],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_require_command_accepts_shell_builtins(self) -> None:
        result = subprocess.run(
            [
                "/bin/sh",
                "-c",
                f'. "{HELPER}"; polinko_require_command : "unit test"',
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

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

    def test_require_process_inspection_reports_missing_ps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    "/bin/sh",
                    "-c",
                    (
                        f'. "{HELPER}"; '
                        f'PATH="{tmp}"; '
                        'polinko_require_process_inspection "pid context"'
                    ),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Missing required command for pid context: ps", result.stderr)

    def test_require_positive_integer_rejects_zero_or_non_numeric_value(self) -> None:
        for value in ("0", "abc"):
            with self.subTest(value=value):
                result = subprocess.run(
                    [
                        "/bin/sh",
                        "-c",
                        (
                            f'. "{HELPER}"; '
                            "polinko_require_positive_integer "
                            f"TEST_VALUE {value} 'unit test'"
                        ),
                    ],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    "Invalid numeric value for unit test: "
                    f"TEST_VALUE must be a positive integer (got {value})",
                    result.stderr,
                )

    def test_require_non_negative_integer_accepts_zero_and_positive_value(self) -> None:
        for value in ("0", "12"):
            with self.subTest(value=value):
                result = subprocess.run(
                    [
                        "/bin/sh",
                        "-c",
                        (
                            f'. "{HELPER}"; '
                            "polinko_require_non_negative_integer "
                            f"TEST_VALUE '{value}' 'unit test'"
                        ),
                    ],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")

    def test_require_non_negative_integer_rejects_invalid_value(self) -> None:
        for value in ("", "-1", "1.5", "abc"):
            with self.subTest(value=value):
                result = subprocess.run(
                    [
                        "/bin/sh",
                        "-c",
                        (
                            f'. "{HELPER}"; '
                            "polinko_require_non_negative_integer "
                            f"TEST_VALUE '{value}' 'unit test'"
                        ),
                    ],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    "Invalid numeric value for unit test: "
                    "TEST_VALUE must be a non-negative integer",
                    result.stderr,
                )

    def test_require_non_negative_decimal_rejects_invalid_value(self) -> None:
        for value in ("", "-1", "1.", ".1", "1.2.3", "abc"):
            with self.subTest(value=value):
                result = subprocess.run(
                    [
                        "/bin/sh",
                        "-c",
                        (
                            f'. "{HELPER}"; '
                            "polinko_require_non_negative_decimal "
                            f"TEST_VALUE '{value}' 'unit test'"
                        ),
                    ],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    "Invalid numeric value for unit test: "
                    "TEST_VALUE must be a non-negative decimal number",
                    result.stderr,
                )

    def test_require_tcp_port_rejects_invalid_value(self) -> None:
        for value in ("0", "65536", "100000", "abc"):
            with self.subTest(value=value):
                result = subprocess.run(
                    [
                        "/bin/sh",
                        "-c",
                        (
                            f'. "{HELPER}"; '
                            "polinko_require_tcp_port "
                            f"TEST_PORT '{value}' 'unit test'"
                        ),
                    ],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    "Invalid numeric value for unit test: TEST_PORT must be",
                    result.stderr,
                )

    def test_url_explicit_port_extracts_port(self) -> None:
        result = subprocess.run(
            [
                "/bin/sh",
                "-c",
                (
                    f'. "{HELPER}"; '
                    "polinko_url_explicit_port "
                    "'http://127.0.0.1:8765/path?x=1#fragment'"
                ),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "8765")

    def test_join_path_handles_root_and_trailing_slashes(self) -> None:
        cases = (
            ("/tmp", "artifact.log", "/tmp/artifact.log"),
            ("/tmp/", "artifact.log", "/tmp/artifact.log"),
            ("/", "artifact.log", "/artifact.log"),
            ("/tmp", "/artifact.log", "/tmp/artifact.log"),
        )
        for root, leaf, expected in cases:
            with self.subTest(root=root, leaf=leaf):
                result = subprocess.run(
                    [
                        "/bin/sh",
                        "-c",
                        (f'. "{HELPER}"; polinko_join_path "$TEST_ROOT" "$TEST_LEAF"'),
                    ],
                    cwd=REPO_ROOT,
                    env={"TEST_ROOT": root, "TEST_LEAF": leaf},
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), expected)

    def test_require_url_port_matches_rejects_missing_or_mismatched_port(
        self,
    ) -> None:
        cases = (
            ("http://127.0.0.1/path", "must include an explicit port matching 8765"),
            ("http://127.0.0.1:8766/path", "TEST_URL port must match 8765"),
        )
        for url, expected in cases:
            with self.subTest(url=url):
                result = subprocess.run(
                    [
                        "/bin/sh",
                        "-c",
                        (
                            f'. "{HELPER}"; '
                            "polinko_require_url_port_matches "
                            f"TEST_URL '{url}' 8765 'unit test'"
                        ),
                    ],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 1)
                self.assertIn(expected, result.stderr)


if __name__ == "__main__":
    unittest.main()
