from __future__ import annotations

import contextlib
import io
import unittest
from unittest import mock

from tools import local_url


class LocalUrlTests(unittest.TestCase):
    def test_none_mode_prints_url_without_launch(self) -> None:
        stdout = io.StringIO()

        with mock.patch("tools.local_url.subprocess.run") as run:
            with contextlib.redirect_stdout(stdout):
                status = local_url.run_local_url(
                    url="http://127.0.0.1:8000/docs",
                    label="API docs URL",
                    mode="none",
                )

        self.assertEqual(status, 0)
        run.assert_not_called()
        self.assertEqual(
            stdout.getvalue(), "API docs URL: http://127.0.0.1:8000/docs\n"
        )

    def test_system_mode_uses_launcher_before_printing_url(self) -> None:
        stdout = io.StringIO()
        completed = mock.Mock(returncode=0)

        with mock.patch(
            "tools.local_url.subprocess.run", return_value=completed
        ) as run:
            with contextlib.redirect_stdout(stdout):
                status = local_url.run_local_url(
                    url="http://127.0.0.1:8000/docs",
                    label="API docs URL",
                    mode="system",
                    launcher="./tools/open_local_url.sh",
                )

        self.assertEqual(status, 0)
        run.assert_called_once_with(
            ["bash", "./tools/open_local_url.sh", "http://127.0.0.1:8000/docs"],
            check=False,
        )
        self.assertEqual(
            stdout.getvalue(), "API docs URL: http://127.0.0.1:8000/docs\n"
        )

    def test_system_mode_returns_launcher_failure(self) -> None:
        completed = mock.Mock(returncode=24)

        with mock.patch("tools.local_url.subprocess.run", return_value=completed):
            status = local_url.run_local_url(
                url="http://127.0.0.1:8000/docs",
                label="API docs URL",
                mode="system",
                launcher="./tools/open_local_url.sh",
            )

        self.assertEqual(status, 24)

    def test_invalid_mode_reports_operator_error(self) -> None:
        stderr = io.StringIO()

        with contextlib.redirect_stderr(stderr):
            status = local_url.run_local_url(
                url="http://127.0.0.1:8000/docs",
                label="API docs URL",
                mode="browser",
            )

        self.assertEqual(status, 2)
        self.assertEqual(
            stderr.getvalue(),
            "Invalid LOCAL_BROWSER_LAUNCH='browser' (expected none or system).\n",
        )


if __name__ == "__main__":
    unittest.main()
