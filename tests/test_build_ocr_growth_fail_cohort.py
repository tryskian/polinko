import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from tools.build_ocr_growth_fail_cohort import build_fail_cohort
from tools.build_ocr_growth_fail_cohort import _load_run_case_map


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
        growth_case_map: dict[str, dict[str, Any]] = {
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
            run_case_map={},
            metrics_map=metrics_map,
            review_index={},
            min_runs=3,
            include_unstable=False,
            require_ocr_framing=False,
        )

        self.assertEqual(report["summary"]["selected_fail_cases"], 1)
        self.assertEqual(report["summary"]["lane_counts"], {"handwriting": 1})
        self.assertEqual(report["summary"]["failure_pattern_counts"], {"ordered_phrase_missing": 1})
        self.assertEqual(len(report["cases"]), 1)
        selected = report["cases"][0]
        self.assertEqual(selected["id"], "gx-1")
        self.assertEqual(selected["lane"], "handwriting")
        self.assertEqual(selected["source_name"], "sample-1.png")
        self.assertEqual(selected["image_path"], "/tmp/sample-1.png")
        self.assertEqual(selected["must_contain_any"], ["abc"])
        self.assertEqual(selected["must_appear_in_order"], ["abc", "def"])
        self.assertEqual(selected["failure_patterns"], ["ordered_phrase_missing"])
        self.assertEqual(selected["primary_failure_pattern"], "ordered_phrase_missing")
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
        growth_case_map: dict[str, dict[str, Any]] = {
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
            run_case_map={},
            metrics_map={},
            review_index={},
            min_runs=3,
            include_unstable=False,
            require_ocr_framing=False,
        )
        self.assertEqual(strict_report["summary"]["selected_fail_cases"], 0)

        relaxed_report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            run_case_map={},
            metrics_map={},
            review_index={},
            min_runs=3,
            include_unstable=True,
            require_ocr_framing=False,
        )
        self.assertEqual(relaxed_report["summary"]["selected_fail_cases"], 1)
        self.assertEqual(relaxed_report["cases"][0]["id"], "gx-3")

    def test_require_ocr_framing_filters_non_framed_rows(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-1",
                    "observed_runs": 5,
                    "pass_runs": 0,
                    "fail_runs": 5,
                    "decision_stable": True,
                    "always_fail": True,
                    "statuses": ["FAIL"] * 5,
                }
            ]
        }
        growth_case_map: dict[str, dict[str, Any]] = {
            "gx-1": {
                "id": "gx-1",
                "lane": "handwriting",
                "source_name": "sample-1.png",
                "image_path": "/tmp/sample-1.png",
            }
        }
        review_index = {
            "/tmp/sample-1.png": [
                {"ocr_framing_signal": False},
                {"ocr_framing_signal": False},
            ]
        }

        report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            run_case_map={},
            metrics_map={},
            review_index=review_index,
            min_runs=3,
            include_unstable=False,
            require_ocr_framing=True,
        )
        self.assertEqual(report["summary"]["selected_fail_cases"], 0)
        self.assertEqual(report["summary"]["skipped_non_framed"], 1)

    def test_require_ocr_framing_keeps_framed_rows(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-1",
                    "observed_runs": 5,
                    "pass_runs": 0,
                    "fail_runs": 5,
                    "decision_stable": True,
                    "always_fail": True,
                    "statuses": ["FAIL"] * 5,
                }
            ]
        }
        growth_case_map: dict[str, dict[str, Any]] = {
            "gx-1": {
                "id": "gx-1",
                "lane": "handwriting",
                "source_name": "sample-1.png",
                "image_path": "/tmp/sample-1.png",
            }
        }
        review_index = {
            "/tmp/sample-1.png": [
                {"ocr_framing_signal": False},
                {"ocr_framing_signal": True},
            ]
        }

        report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            run_case_map={},
            metrics_map={},
            review_index=review_index,
            min_runs=3,
            include_unstable=False,
            require_ocr_framing=True,
        )
        self.assertEqual(report["summary"]["selected_fail_cases"], 1)
        self.assertEqual(report["summary"]["skipped_non_framed"], 0)
        self.assertEqual(report["cases"][0]["framing_episode_count"], 1)

    def test_run_case_map_image_mismatch_is_skipped(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-1",
                    "observed_runs": 5,
                    "pass_runs": 0,
                    "fail_runs": 5,
                    "decision_stable": True,
                    "always_fail": True,
                    "statuses": ["FAIL"] * 5,
                }
            ]
        }
        growth_case_map: dict[str, dict[str, Any]] = {
            "gx-1": {
                "id": "gx-1",
                "lane": "typed",
                "source_name": "growth.png",
                "image_path": "/tmp/growth.png",
            }
        }
        run_case_map: dict[str, dict[str, Any]] = {
            "gx-1": {
                "id": "gx-1",
                "source_name": "run.png",
                "image_path": "/tmp/run.png",
                "must_contain_any": ["alpha"],
                "must_appear_in_order": ["alpha", "beta"],
            }
        }
        report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            run_case_map=run_case_map,
            metrics_map={},
            review_index={},
            min_runs=3,
            include_unstable=False,
            require_ocr_framing=False,
        )
        self.assertEqual(report["summary"]["selected_fail_cases"], 0)
        self.assertEqual(report["summary"]["skipped_case_map_mismatch"], 1)

    def test_unknown_lane_falls_back_to_review_lane(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-1",
                    "observed_runs": 5,
                    "pass_runs": 0,
                    "fail_runs": 5,
                    "decision_stable": True,
                    "always_fail": True,
                    "statuses": ["FAIL"] * 5,
                }
            ]
        }
        growth_case_map: dict[str, dict[str, Any]] = {
            "gx-1": {
                "id": "gx-1",
                "lane": "unknown",
                "source_name": "sample-1.png",
                "image_path": "/tmp/sample-1.png",
            }
        }
        review_index = {
            "/tmp/sample-1.png": [
                {"lane": "handwriting", "ocr_framing_signal": True},
                {"lane": "handwriting", "ocr_framing_signal": True},
            ]
        }
        report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            run_case_map={},
            metrics_map={},
            review_index=review_index,
            min_runs=3,
            include_unstable=False,
            require_ocr_framing=True,
        )
        self.assertEqual(report["summary"]["selected_fail_cases"], 1)
        self.assertEqual(report["summary"]["lane_counts"], {"handwriting": 1})
        self.assertEqual(report["cases"][0]["lane"], "handwriting")

    def test_rate_limited_cases_are_reported_separately(self) -> None:
        stability_payload = {
            "runs": [
                {
                    "summary": {"aborted_due_to_rate_limit": True},
                }
            ],
            "cases": [
                {
                    "id": "gx-rate-1",
                    "observed_runs": 1,
                    "pass_runs": 0,
                    "fail_runs": 0,
                    "error_runs": 1,
                    "statuses": ["ERROR"],
                    "decision_stable": False,
                    "always_fail": False,
                }
            ],
        }
        growth_case_map: dict[str, dict[str, Any]] = {
            "gx-rate-1": {
                "id": "gx-rate-1",
                "lane": "handwriting",
                "source_name": "rate.png",
                "image_path": "/tmp/rate.png",
            }
        }

        report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            run_case_map={},
            metrics_map={},
            review_index={},
            min_runs=1,
            include_unstable=False,
            require_ocr_framing=False,
        )
        self.assertEqual(report["summary"]["selected_fail_cases"], 0)
        self.assertEqual(report["summary"]["rate_limited_cases"], 1)
        self.assertEqual(report["summary"]["rate_limit_abort_runs"], 1)
        self.assertEqual(len(report["rate_limited_cases"]), 1)
        self.assertEqual(report["rate_limited_cases"][0]["id"], "gx-rate-1")

    def test_load_run_case_map_accepts_repo_relative_report_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            run_report_path = tmp / ".local" / "eval_reports" / "ocr_growth_stability_runs" / "r1.json"
            run_report_path.parent.mkdir(parents=True, exist_ok=True)
            run_report_path.write_text(
                """{
                  "cases": [
                    {"id": "gx-1", "source_name": "s.png", "image_path": "/tmp/s.png"}
                  ]
                }""",
                encoding="utf-8",
            )

            stability_payload = {
                "runs": [
                    {
                        "report_json": ".local/eval_reports/ocr_growth_stability_runs/r1.json",
                    }
                ]
            }
            stability_report_path = tmp / ".local" / "eval_reports" / "ocr_growth_stability.json"
            stability_report_path.parent.mkdir(parents=True, exist_ok=True)
            stability_report_path.write_text("{}", encoding="utf-8")

            previous_cwd = Path.cwd()
            try:
                # Repo-relative report_json should resolve from cwd first.
                import os

                os.chdir(tmp)
                run_case_map = _load_run_case_map(
                    stability_payload=stability_payload,
                    stability_report_path=stability_report_path,
                )
            finally:
                os.chdir(previous_cwd)

            self.assertIn("gx-1", run_case_map)
            self.assertEqual(run_case_map["gx-1"]["source_name"], "s.png")


if __name__ == "__main__":
    unittest.main()
