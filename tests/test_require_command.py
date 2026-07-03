from __future__ import annotations

import contextlib
import io
import unittest
from unittest import mock

from tools import require_command


class RequireCommandTests(unittest.TestCase):
    def test_available_command_passes(self) -> None:
        with mock.patch("tools.require_command.shutil.which", return_value="/bin/tool"):
            self.assertEqual(
                require_command.validate_command("tool", label="test helper"),
                0,
            )

    def test_missing_command_reports_helper_label(self) -> None:
        stderr = io.StringIO()

        with mock.patch("tools.require_command.shutil.which", return_value=None):
            with contextlib.redirect_stderr(stderr):
                status = require_command.validate_command(
                    "missing-tool",
                    label="test helper",
                )

        self.assertEqual(status, 127)
        self.assertEqual(
            stderr.getvalue(),
            "test helper: missing required command: missing-tool\n",
        )

    def test_main_uses_supplied_label(self) -> None:
        stderr = io.StringIO()

        with mock.patch("tools.require_command.shutil.which", return_value=None):
            with contextlib.redirect_stderr(stderr):
                status = require_command.main(
                    [
                        "--command",
                        "act",
                        "--label",
                        "act helper",
                    ]
                )

        self.assertEqual(status, 127)
        self.assertEqual(
            stderr.getvalue(),
            "act helper: missing required command: act\n",
        )


if __name__ == "__main__":
    unittest.main()
