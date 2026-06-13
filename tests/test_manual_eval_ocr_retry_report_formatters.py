from __future__ import annotations

import unittest

from tools.manual_eval_ocr_retry_report_formatters import int_value, terminal_path_name


class ManualEvalOcrRetryReportFormatterTests(unittest.TestCase):
    def test_int_value_normalizes_numeric_like_values(self) -> None:
        self.assertEqual(int_value(None), 0)
        self.assertEqual(int_value(""), 0)
        self.assertEqual(int_value(" 7 "), 7)
        self.assertEqual(int_value(8), 8)
        self.assertEqual(int_value(9.9), 9)
        self.assertEqual(int_value(object()), 0)

    def test_terminal_path_name_returns_leaf_name_or_none(self) -> None:
        self.assertEqual(terminal_path_name(None), "none")
        self.assertEqual(terminal_path_name(""), "none")
        self.assertEqual(terminal_path_name("   "), "none")
        self.assertEqual(terminal_path_name("/tmp/polinko/run-001"), "run-001")
        self.assertEqual(terminal_path_name("relative/run-002"), "run-002")
        self.assertEqual(terminal_path_name("/"), "none")


if __name__ == "__main__":
    unittest.main()
