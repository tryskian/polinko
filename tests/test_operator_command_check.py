from __future__ import annotations

import subprocess
import sys
import unittest

from tools import check_operator_commands


class OperatorCommandCheckTests(unittest.TestCase):
    def test_current_repo_passes_operator_command_check(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "tools.check_operator_commands"],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("[ok] operator command check passed", result.stdout)

    def test_duplicate_manualdb_target_is_reported(self) -> None:
        failures = check_operator_commands.check_canonical_operator_targets(
            "\n".join(
                [
                    ".PHONY: manual-evals-feedback-actionables manualdb-feedback-actionables",
                    "manual-evals-feedback-actionables manualdb-feedback-actionables:",
                    "\t@true",
                ]
            )
        )

        self.assertEqual(
            failures,
            [
                "manualdb-feedback-actionables: non-canonical operator target is active",
                "manualdb-feedback-actionables: non-canonical operator rule is active on line 2",
            ],
        )

    def test_duplicate_closeout_target_is_reported(self) -> None:
        failures = check_operator_commands.check_canonical_operator_targets(
            "\n".join(
                [
                    ".PHONY: end eod",
                    "end:",
                    "\t@true",
                    "eod: end",
                ]
            )
        )

        self.assertEqual(
            failures,
            [
                "eod: non-canonical operator target is active",
                "eod: non-canonical operator rule is active on line 4",
            ],
        )

    def test_duplicate_closeout_stop_target_is_reported(self) -> None:
        failures = check_operator_commands.check_canonical_operator_targets(
            "\n".join(
                [
                    ".PHONY: end-stop eod-stop",
                    "end-stop:",
                    "\t@true",
                    "eod-stop: end-stop",
                ]
            )
        )

        self.assertEqual(
            failures,
            [
                "eod-stop: non-canonical operator target is active",
                "eod-stop: non-canonical operator rule is active on line 4",
            ],
        )

    def test_openai_account_alias_targets_are_reported(self) -> None:
        failures = check_operator_commands.check_canonical_operator_targets(
            "\n".join(
                [
                    ".PHONY: openai-limits open-limits",
                    "openai-limits:",
                    "\t@true",
                    "open-limits: openai-limits",
                ]
            )
        )

        self.assertEqual(
            failures,
            [
                "open-limits: non-canonical operator target is active",
                "open-limits: non-canonical operator rule is active on line 4",
            ],
        )

    def test_dependency_refresh_alias_target_is_reported(self) -> None:
        failures = check_operator_commands.check_canonical_operator_targets(
            "\n".join(
                [
                    ".PHONY: deps-refresh refresh-deps",
                    "deps-refresh:",
                    "\t@true",
                    "refresh-deps: deps-refresh",
                ]
            )
        )

        self.assertEqual(
            failures,
            [
                "refresh-deps: non-canonical operator target is active",
                "refresh-deps: non-canonical operator rule is active on line 4",
            ],
        )

    def test_interactive_env_alias_target_is_reported(self) -> None:
        failures = check_operator_commands.check_canonical_operator_targets(
            "\n".join(
                [
                    ".PHONY: venv env",
                    "venv:",
                    "\t@true",
                    "env: venv",
                ]
            )
        )

        self.assertEqual(
            failures,
            [
                "env: non-canonical operator target is active",
                "env: non-canonical operator rule is active on line 4",
            ],
        )

    def test_parked_ocr_shortcut_cannot_enter_automation_entrypoint(self) -> None:
        failures = check_operator_commands.check_parked_ocr_shortcuts(
            "\n".join(
                [
                    "start: doctor-env ocrall",
                    "ocr-inventory:",
                    "\t@true",
                    "ocr-inventory-json: ocr-inventory",
                ]
            )
        )

        self.assertEqual(
            failures,
            [
                "start: automation dependency includes parked OCR eval shortcut(s): ocrall"
            ],
        )

    def test_parked_ocr_shortcut_cannot_enter_closeout_helper(self) -> None:
        failures = check_operator_commands.check_parked_ocr_shortcuts(
            "\n".join(
                [
                    "end-stop: eval-sidecar-stop ocrstable",
                    "ocr-inventory:",
                    "\t@true",
                    "ocr-inventory-json: ocr-inventory",
                ]
            )
        )

        self.assertEqual(
            failures,
            [
                "end-stop: automation dependency includes parked OCR eval "
                "shortcut(s): ocrstable"
            ],
        )


if __name__ == "__main__":
    unittest.main()
