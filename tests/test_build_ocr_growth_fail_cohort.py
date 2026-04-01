import unittest

from tools.build_ocr_growth_fail_cohort import build_fail_cohort


class OcrGrowthFailCohortTests(unittest.TestCase):
    def test_selects_stable_always_fail_cases_with_metadata_join(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-1",
                    "observed_runs": 5,
                    "pass_runs": 0,
                    "fail_runs": 5,
                    "error_runs": 0,
                    "pass_rate": 0.0,
                    "decision_stable": True,
                    "always_fail": True,
                    "statuses": ["FAIL"] * 5,
                    "sample_reasons": ["missing ordered phrase: 'abc'"],
                    "text_variant_count": 3,
                    "char_count_span": 10,
                },
                {
                    "id": "gx-2",
                    "observed_runs": 5,
                    "pass_runs": 2,
                    "fail_runs": 3,
                    "error_runs": 0,
                    "pass_rate": 0.4,
                    "decision_stable": False,
                    "always_fail": False,
                    "statuses": ["FAIL", "PASS", "FAIL", "PASS", "FAIL"],
                },
            ]
        }
        growth_case_map = {
            "gx-1": {
                "id": "gx-1",
                "lane": "handwriting",
                "source_name": "sample-1.png",
                "image_path": "/tmp/sample-1.png",
                "must_contain_any": ["abc"],
                "must_appear_in_order": ["abc", "def"],
            },
            "gx-2": {
                "id": "gx-2",
                "lane": "typed",
                "source_name": "sample-2.png",
                "image_path": "/tmp/sample-2.png",
            },
        }
        metrics_map = {
            "gx-1": {
                "id": "gx-1",
                "unresolved_fail_age_hours": 12.345,
            }
        }

        report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            metrics_map=metrics_map,
            min_runs=3,
            include_unstable=False,
        )

        self.assertEqual(report["summary"]["selected_fail_cases"], 1)
        self.assertEqual(report["summary"]["lane_counts"], {"handwriting": 1})
        self.assertEqual(len(report["cases"]), 1)
        selected = report["cases"][0]
        self.assertEqual(selected["id"], "gx-1")
        self.assertEqual(selected["lane"], "handwriting")
        self.assertEqual(selected["source_name"], "sample-1.png")
        self.assertEqual(selected["image_path"], "/tmp/sample-1.png")
        self.assertEqual(selected["must_contain_any"], ["abc"])
        self.assertEqual(selected["must_appear_in_order"], ["abc", "def"])
        self.assertEqual(selected["unresolved_fail_age_hours"], 12.345)

    def test_include_unstable_adds_unstable_persistent_fail(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-3",
                    "observed_runs": 5,
                    "pass_runs": 0,
                    "fail_runs": 5,
                    "error_runs": 0,
                    "pass_rate": 0.0,
                    "decision_stable": False,
                    "always_fail": False,
                    "statuses": ["FAIL", "FAIL", "FAIL", "FAIL", "FAIL"],
                }
            ]
        }
        growth_case_map = {
            "gx-3": {
                "id": "gx-3",
                "lane": "illustration",
                "source_name": "sample-3.png",
                "image_path": "/tmp/sample-3.png",
            }
        }

        strict_report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            metrics_map={},
            min_runs=3,
            include_unstable=False,
        )
        self.assertEqual(strict_report["summary"]["selected_fail_cases"], 0)

        relaxed_report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            metrics_map={},
            min_runs=3,
            include_unstable=True,
        )
        self.assertEqual(relaxed_report["summary"]["selected_fail_cases"], 1)
        self.assertEqual(relaxed_report["cases"][0]["id"], "gx-3")


if __name__ == "__main__":
    unittest.main()
