import unittest

from tools.manual_eval_ocr_retry_selection_formatters import (
    display_text,
    format_feedback_ids,
    format_input_blocker_state,
    format_plan_source_preview,
    format_plan_thumbnail,
    format_readiness_flags,
    format_terminal_source_path,
    int_value,
    truncate_text,
)


class ManualEvalOcrRetrySelectionFormattersTests(unittest.TestCase):
    def test_common_terminal_formatters_match_selection_report_contracts(self) -> None:
        self.assertEqual(int_value(" 7 "), 7)
        self.assertEqual(int_value(""), 0)
        self.assertEqual(display_text("  source   preview "), "source preview")
        self.assertEqual(truncate_text("abcdef", max_chars=4), "abc...")
        self.assertEqual(format_feedback_ids([1, "2", None]), "1,2,0")
        self.assertEqual(
            format_readiness_flags({"flags": ["exact", "ready"]}), "exact,ready"
        )
        self.assertEqual(
            format_input_blocker_state(
                {
                    "state": "blocked",
                    "reason_code": "missing_source",
                    "next_action": "attach_source",
                }
            ),
            "blocked reason=missing_source next=attach_source",
        )
        self.assertEqual(
            format_plan_thumbnail({"available": True, "width": "120", "height": 40}),
            "120x40",
        )
        self.assertEqual(
            format_terminal_source_path("/tmp/manual-evals/source.png"),
            "source.png",
        )
        self.assertEqual(
            format_plan_source_preview(
                {
                    "feedback_id": "42",
                    "message_id": "msg_1",
                    "source_state": "linked",
                    "source_role": "assistant",
                    "source_preview": "OCR source text",
                }
            ),
            "feedback=42 message=msg_1 source_state=linked "
            "role=assistant preview=OCR source text",
        )


if __name__ == "__main__":
    unittest.main()
