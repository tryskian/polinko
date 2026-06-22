from __future__ import annotations

import subprocess
import sys
import unittest

from tools import check_operator_aliases


class OperatorAliasCheckTests(unittest.TestCase):
    def test_current_repo_passes_operator_alias_check(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "tools.check_operator_aliases"],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("[ok] operator alias check passed", result.stdout)

    def test_manual_eval_alias_must_share_recipe_line(self) -> None:
        failures = check_operator_aliases.check_manual_eval_aliases(
            "\n".join(
                [
                    ".PHONY: manual-evals-feedback-actionables manualdb-feedback-actionables",
                    "manual-evals-feedback-actionables:",
                    "\t@true",
                    "manualdb-feedback-actionables:",
                    "\t@true",
                ]
            )
        )

        self.assertEqual(
            failures,
            [
                "manual-evals-feedback-actionables: alias "
                "manualdb-feedback-actionables is not on the same recipe line "
                "(canonical line(s): 2)"
            ],
        )

    def test_missing_manualdb_alias_is_reported(self) -> None:
        failures = check_operator_aliases.check_manual_eval_aliases(
            "\n".join(
                [
                    ".PHONY: manual-evals-feedback-actionables",
                    "manual-evals-feedback-actionables:",
                    "\t@true",
                ]
            )
        )

        self.assertEqual(
            failures,
            [
                "manual-evals-feedback-actionables: missing .PHONY "
                "compatibility alias manualdb-feedback-actionables"
            ],
        )

    def test_parked_ocr_alias_cannot_enter_automation_entrypoint(self) -> None:
        failures = check_operator_aliases.check_parked_ocr_aliases(
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
            ["start: automation dependency includes parked OCR eval alias(es): ocrall"],
        )


if __name__ == "__main__":
    unittest.main()
