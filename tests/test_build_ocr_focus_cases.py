import unittest
from typing import Any

from tools.build_ocr_focus_cases import build_focus_cases


class BuildOcrFocusCasesTests(unittest.TestCase):
    def test_builds_from_persistent_and_fail_history(self) -> None:
        cohort_payload = {
            "cases": [{"id": "gx-1"}, {"id": "gx-2"}],
            "fail_history_cases": [{"id": "gx-3"}, {"id": "gx-2"}],
        }
        source_cases_payload: dict[str, Any] = {
            "cases": [
                {"id": "gx-1", "lane": "handwriting"},
                {"id": "gx-2", "lane": "typed"},
                {"id": "gx-3", "lane": "illustration"},
                {"id": "gx-4", "lane": "typed"},
            ]
        }

        report = build_focus_cases(
            cohort_payload=cohort_payload,
            source_cases_payload=source_cases_payload,
            include_fail_history=True,
            max_cases=0,
        )

        self.assertEqual(report["summary"]["requested_ids"], 3)
        self.assertEqual(report["summary"]["selected_cases"], 3)
        self.assertEqual(report["summary"]["missing_ids"], 0)
        selected_ids = [row["id"] for row in report["cases"]]
        self.assertEqual(selected_ids, ["gx-1", "gx-2", "gx-3"])

    def test_can_exclude_fail_history(self) -> None:
        cohort_payload = {
            "cases": [{"id": "gx-1"}],
            "fail_history_cases": [{"id": "gx-2"}],
        }
        source_cases_payload: dict[str, Any] = {
            "cases": [
                {"id": "gx-1", "lane": "handwriting"},
                {"id": "gx-2", "lane": "typed"},
            ]
        }

        report = build_focus_cases(
            cohort_payload=cohort_payload,
            source_cases_payload=source_cases_payload,
            include_fail_history=False,
            max_cases=0,
        )

        self.assertEqual(report["summary"]["requested_ids"], 1)
        self.assertEqual(report["summary"]["selected_cases"], 1)
        self.assertEqual([row["id"] for row in report["cases"]], ["gx-1"])

    def test_respects_max_cases_and_tracks_missing(self) -> None:
        cohort_payload = {
            "cases": [{"id": "gx-1"}, {"id": "gx-missing"}, {"id": "gx-2"}],
            "fail_history_cases": [],
        }
        source_cases_payload: dict[str, Any] = {
            "cases": [
                {"id": "gx-1", "lane": "handwriting"},
                {"id": "gx-2", "lane": "typed"},
            ]
        }

        report = build_focus_cases(
            cohort_payload=cohort_payload,
            source_cases_payload=source_cases_payload,
            include_fail_history=True,
            max_cases=1,
        )

        self.assertEqual(report["summary"]["requested_ids"], 3)
        self.assertEqual(report["summary"]["missing_ids"], 1)
        self.assertEqual(report["summary"]["selected_cases"], 1)
        self.assertEqual([row["id"] for row in report["cases"]], ["gx-1"])
        self.assertEqual(report["missing_ids"], ["gx-missing"])


if __name__ == "__main__":
    unittest.main()
