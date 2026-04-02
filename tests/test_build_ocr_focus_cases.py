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
        self.assertEqual(report["summary"]["cases_with_cohort_history"], 3)
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
        self.assertEqual(report["summary"]["cases_with_cohort_history"], 1)
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
        self.assertEqual(report["summary"]["cases_with_cohort_history"], 1)
        self.assertEqual([row["id"] for row in report["cases"]], ["gx-1"])
        self.assertEqual(report["missing_ids"], ["gx-missing"])

    def test_merges_cohort_history_without_overwriting_constraints(self) -> None:
        cohort_payload = {
            "cases": [
                {
                    "id": "gx-1",
                    "observed_runs": 5,
                    "pass_runs": 1,
                    "fail_runs": 4,
                    "sample_reasons": ["missing tokens"],
                }
            ],
            "fail_history_cases": [],
        }
        source_cases_payload: dict[str, Any] = {
            "cases": [
                {
                    "id": "gx-1",
                    "lane": "handwriting",
                    "must_contain_any": ["alpha", "beta"],
                    "sample_reasons": [],
                }
            ]
        }

        report = build_focus_cases(
            cohort_payload=cohort_payload,
            source_cases_payload=source_cases_payload,
            include_fail_history=True,
            max_cases=0,
        )

        self.assertEqual(report["summary"]["cases_with_cohort_history"], 1)
        selected = report["cases"][0]
        self.assertEqual(selected["focus_source"], "persistent_fail")
        self.assertEqual(selected["observed_runs"], 5)
        self.assertEqual(selected["pass_runs"], 1)
        self.assertEqual(selected["fail_runs"], 4)
        self.assertEqual(selected["must_contain_any"], ["alpha", "beta"])
        # Empty source list is backfilled from cohort history.
        self.assertEqual(selected["sample_reasons"], ["missing tokens"])


if __name__ == "__main__":
    unittest.main()
