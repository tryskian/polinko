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
            },
            "gx-2": {
                "id": "gx-2",
                "fail_to_pass_converted": True,
                "first_status": "FAIL",
                "latest_status": "PASS",
            },
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
        self.assertEqual(report["summary"]["stability_cases_total"], 2)
        self.assertEqual(report["summary"]["metrics_rows_added"], 0)
        self.assertEqual(report["summary"]["fail_history_cases"], 1)
        self.assertEqual(report["summary"]["fail_to_pass_cases"], 1)
        self.assertEqual(report["summary"]["lane_counts"], {"handwriting": 1})
        self.assertEqual(report["summary"]["fail_history_lane_counts"], {"typed": 1})
        self.assertEqual(report["summary"]["failure_pattern_counts"].get("ordered_phrase_missing"), 1)
        self.assertEqual(report["summary"]["failure_pattern_counts"].get("recovered_after_fail"), 1)
        self.assertEqual(len(report["cases"]), 1)
        selected = report["cases"][0]
        self.assertEqual(selected["id"], "gx-1")
        self.assertEqual(selected["lane"], "handwriting")
        self.assertEqual(selected["source_name"], "sample-1.png")
        self.assertEqual(selected["image_path"], "/tmp/sample-1.png")
        self.assertEqual(selected["must_contain_any"], ["abc"])
        self.assertEqual(selected["must_appear_in_order"], ["abc", "def"])
        self.assertEqual(selected["effective_must_contain_any"], ["abc"])
        self.assertEqual(selected["effective_must_appear_in_order"], ["abc", "def"])
        self.assertEqual(selected["gate_probe_summary"], "any[abc] order[abc, def]")
        self.assertEqual(selected["failure_patterns"], ["ordered_phrase_missing"])
        self.assertEqual(selected["primary_failure_pattern"], "ordered_phrase_missing")
        self.assertEqual(selected["unresolved_fail_age_hours"], 12.345)
        self.assertEqual(len(report["fail_history_cases"]), 1)
        fail_history = report["fail_history_cases"][0]
        self.assertEqual(fail_history["id"], "gx-2")
        self.assertEqual(fail_history["lane"], "typed")
        self.assertEqual(fail_history["fail_to_pass_converted"], True)
        self.assertEqual(fail_history["first_status"], "FAIL")
        self.assertEqual(fail_history["latest_status"], "PASS")
        self.assertEqual(fail_history["gate_probe_summary"], "any[-] order[-]")

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

    def test_metrics_observed_rows_are_merged_when_stability_is_partial(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-1",
                    "observed_runs": 1,
                    "pass_runs": 1,
                    "fail_runs": 0,
                    "error_runs": 0,
                    "statuses": ["PASS"],
                    "decision_stable": True,
                    "always_fail": False,
                }
            ]
        }
        growth_case_map: dict[str, dict[str, Any]] = {
            "gx-1": {
                "id": "gx-1",
                "lane": "typed",
                "source_name": "one.png",
                "image_path": "/tmp/one.png",
            },
            "gx-2": {
                "id": "gx-2",
                "lane": "handwriting",
                "source_name": "two.png",
                "image_path": "/tmp/two.png",
            },
        }
        metrics_map = {
            "gx-1": {"id": "gx-1", "observed_runs": 1, "pass_runs": 1, "fail_runs": 0, "error_runs": 0},
            "gx-2": {"id": "gx-2", "observed_runs": 2, "pass_runs": 0, "fail_runs": 2, "error_runs": 0},
        }

        report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            run_case_map={},
            metrics_map=metrics_map,
            review_index={},
            min_runs=1,
            include_unstable=True,
            require_ocr_framing=False,
        )
        self.assertEqual(report["summary"]["stability_cases_total"], 1)
        self.assertEqual(report["summary"]["metrics_rows_added"], 1)
        self.assertEqual(report["summary"]["cases_total"], 2)
        self.assertEqual(report["summary"]["selected_fail_cases"], 1)
        self.assertEqual(report["cases"][0]["id"], "gx-2")
        self.assertEqual(report["cases"][0]["primary_failure_pattern"], "persistent_fail")
        self.assertEqual(report["summary"]["failure_pattern_counts"], {"persistent_fail": 1})

    def test_fallback_pattern_prefers_ordered_proxy_when_gate_fields_exist(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-ord",
                    "observed_runs": 4,
                    "pass_runs": 0,
                    "fail_runs": 4,
                    "error_runs": 0,
                    "statuses": ["FAIL"] * 4,
                    "decision_stable": True,
                    "always_fail": True,
                    "sample_reasons": [],
                }
            ]
        }
        growth_case_map: dict[str, dict[str, Any]] = {
            "gx-ord": {
                "id": "gx-ord",
                "lane": "typed",
                "source_name": "ord.png",
                "image_path": "/tmp/ord.png",
                "must_appear_in_order": ["foo", "bar"],
                "must_contain_any": ["foo"],
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

        self.assertEqual(report["summary"]["selected_fail_cases"], 1)
        self.assertEqual(report["cases"][0]["primary_failure_pattern"], "ordered_phrase_missing_proxy")
        self.assertEqual(
            report["summary"]["failure_pattern_counts"],
            {"ordered_phrase_missing_proxy": 1},
        )

    def test_run_case_gate_terms_override_growth_case_terms(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-override",
                    "observed_runs": 4,
                    "pass_runs": 0,
                    "fail_runs": 4,
                    "error_runs": 0,
                    "statuses": ["FAIL"] * 4,
                    "decision_stable": True,
                    "always_fail": True,
                    "sample_reasons": [],
                }
            ]
        }
        growth_case_map: dict[str, dict[str, Any]] = {
            "gx-override": {
                "id": "gx-override",
                "lane": "typed",
                "source_name": "growth.png",
                "image_path": "/tmp/growth.png",
                "must_contain_any": ["growth-any"],
                "must_appear_in_order": ["growth-order-a", "growth-order-b"],
            }
        }
        run_case_map: dict[str, dict[str, Any]] = {
            "gx-override": {
                "id": "gx-override",
                "source_name": "run.png",
                "image_path": "/tmp/growth.png",
                "must_contain_any": ["run-any"],
                "must_appear_in_order": ["run-order-a", "run-order-b"],
            }
        }

        report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            run_case_map=run_case_map,
            metrics_map={},
            review_index={},
            min_runs=1,
            include_unstable=False,
            require_ocr_framing=False,
        )

        self.assertEqual(report["summary"]["selected_fail_cases"], 1)
        selected = report["cases"][0]
        self.assertEqual(selected["effective_must_contain_any"], ["run-any"])
        self.assertEqual(
            selected["effective_must_appear_in_order"],
            ["run-order-a", "run-order-b"],
        )
        self.assertEqual(
            selected["gate_probe_summary"],
            "any[run-any] order[run-order-a, run-order-b]",
        )

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

    def test_include_exploratory_selects_stable_pass_probes(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-pass-1",
                    "observed_runs": 3,
                    "pass_runs": 3,
                    "fail_runs": 0,
                    "error_runs": 0,
                    "pass_rate": 1.0,
                    "decision_stable": True,
                    "always_fail": False,
                    "statuses": ["PASS"] * 3,
                    "text_variant_count": 2,
                    "char_count_span": 11,
                }
            ]
        }
        growth_case_map: dict[str, dict[str, Any]] = {
            "gx-pass-1": {
                "id": "gx-pass-1",
                "lane": "handwriting",
                "source_name": "sample-pass.png",
                "image_path": "/tmp/sample-pass.png",
                "must_contain_any": ["gyro folds within", "field notes", "origin"],
            }
        }
        review_index = {
            "/tmp/sample-pass.png": [
                {"ocr_framing_signal": True, "lane": "handwriting"},
            ]
        }

        report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            run_case_map={},
            metrics_map={},
            review_index=review_index,
            min_runs=1,
            include_unstable=True,
            require_ocr_framing=True,
            include_exploratory=True,
            exploratory_max_cases=5,
        )

        self.assertEqual(report["summary"]["selected_fail_cases"], 0)
        self.assertEqual(report["summary"]["exploratory_cases"], 1)
        self.assertEqual(report["summary"]["exploratory_lane_counts"], {"handwriting": 1})
        exploratory = report["exploratory_cases"][0]
        self.assertEqual(exploratory["id"], "gx-pass-1")
        self.assertEqual(exploratory["primary_failure_pattern"], "exploratory_stress_probe")
        overrides = exploratory.get("focus_overrides")
        self.assertIsInstance(overrides, dict)
        self.assertGreaterEqual(len(overrides.get("must_appear_in_order", [])), 2)
        self.assertGreater(int(overrides.get("min_chars", 0) or 0), 0)

    def test_exploratory_prefers_anchor_derived_order_over_stale_source_order(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-pass-2",
                    "observed_runs": 2,
                    "pass_runs": 2,
                    "fail_runs": 0,
                    "error_runs": 0,
                    "pass_rate": 1.0,
                    "decision_stable": True,
                    "always_fail": False,
                    "statuses": ["PASS", "PASS"],
                }
            ]
        }
        growth_case_map: dict[str, dict[str, Any]] = {
            "gx-pass-2": {
                "id": "gx-pass-2",
                "lane": "typed",
                "source_name": "sample-pass-2.png",
                "image_path": "/tmp/sample-pass-2.png",
                "must_contain_any": ["field notes measurable record"],
                "must_appear_in_order": ["stale", "sequence", "tokens"],
            }
        }
        review_index = {
            "/tmp/sample-pass-2.png": [{"ocr_framing_signal": True, "lane": "typed"}]
        }

        report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            run_case_map={},
            metrics_map={},
            review_index=review_index,
            min_runs=1,
            include_unstable=True,
            require_ocr_framing=True,
            include_exploratory=True,
            exploratory_max_cases=5,
        )
        self.assertEqual(report["summary"]["exploratory_cases"], 1)
        exploratory = report["exploratory_cases"][0]
        overrides = exploratory.get("focus_overrides")
        self.assertIsInstance(overrides, dict)
        self.assertEqual(
            overrides.get("must_appear_in_order"),
            ["field", "measurable"],
        )

    def test_exploratory_prefers_run_extracted_tokens_over_anchor_guess_tokens(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-pass-ocr-order",
                    "observed_runs": 2,
                    "pass_runs": 2,
                    "fail_runs": 0,
                    "error_runs": 0,
                    "pass_rate": 1.0,
                    "decision_stable": True,
                    "always_fail": False,
                    "statuses": ["PASS", "PASS"],
                }
            ]
        }
        growth_case_map: dict[str, dict[str, Any]] = {
            "gx-pass-ocr-order": {
                "id": "gx-pass-ocr-order",
                "lane": "typed",
                "source_name": "sample-pass-ocr-order.png",
                "image_path": "/tmp/sample-pass-ocr-order.png",
                "must_contain_any": ["instance", "engineering", "design", "informed"],
            }
        }
        run_case_map: dict[str, dict[str, Any]] = {
            "gx-pass-ocr-order": {
                "id": "gx-pass-ocr-order",
                "source_name": "sample-pass-ocr-order.png",
                "image_path": "/tmp/sample-pass-ocr-order.png",
                "extracted_text": (
                    "impact on human psyche design increases risk and improves clarity"
                ),
            }
        }
        review_index = {
            "/tmp/sample-pass-ocr-order.png": [{"ocr_framing_signal": True, "lane": "typed"}]
        }

        report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            run_case_map=run_case_map,
            metrics_map={},
            review_index=review_index,
            min_runs=1,
            include_unstable=True,
            require_ocr_framing=True,
            include_exploratory=True,
            exploratory_max_cases=5,
        )
        self.assertEqual(report["summary"]["exploratory_cases"], 1)
        exploratory = report["exploratory_cases"][0]
        overrides = exploratory.get("focus_overrides")
        self.assertIsInstance(overrides, dict)
        self.assertEqual(
            overrides.get("must_appear_in_order"),
            ["impact", "human"],
        )

    def test_exploratory_collapses_plural_singular_probe_duplicates(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-pass-3",
                    "observed_runs": 2,
                    "pass_runs": 2,
                    "fail_runs": 0,
                    "error_runs": 0,
                    "pass_rate": 1.0,
                    "decision_stable": True,
                    "always_fail": False,
                    "statuses": ["PASS", "PASS"],
                }
            ]
        }
        growth_case_map: dict[str, dict[str, Any]] = {
            "gx-pass-3": {
                "id": "gx-pass-3",
                "lane": "illustration",
                "source_name": "sample-pass-3.png",
                "image_path": "/tmp/sample-pass-3.png",
                "must_contain_any": ["tumbles tumble restore spectral"],
            }
        }
        review_index = {
            "/tmp/sample-pass-3.png": [{"ocr_framing_signal": True, "lane": "illustration"}]
        }

        report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            run_case_map={},
            metrics_map={},
            review_index=review_index,
            min_runs=1,
            include_unstable=True,
            require_ocr_framing=True,
            include_exploratory=True,
            exploratory_max_cases=5,
        )
        self.assertEqual(report["summary"]["exploratory_cases"], 1)
        exploratory = report["exploratory_cases"][0]
        overrides = exploratory.get("focus_overrides")
        self.assertIsInstance(overrides, dict)
        self.assertEqual(
            overrides.get("must_appear_in_order"),
            ["tumbles", "restore"],
        )

    def test_exploratory_balances_lane_selection_round_robin(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-hand-a",
                    "observed_runs": 2,
                    "pass_runs": 2,
                    "fail_runs": 0,
                    "error_runs": 0,
                    "pass_rate": 1.0,
                    "decision_stable": True,
                    "always_fail": False,
                    "statuses": ["PASS", "PASS"],
                    "text_variant_count": 9,
                },
                {
                    "id": "gx-hand-b",
                    "observed_runs": 2,
                    "pass_runs": 2,
                    "fail_runs": 0,
                    "error_runs": 0,
                    "pass_rate": 1.0,
                    "decision_stable": True,
                    "always_fail": False,
                    "statuses": ["PASS", "PASS"],
                    "text_variant_count": 8,
                },
                {
                    "id": "gx-type-a",
                    "observed_runs": 2,
                    "pass_runs": 2,
                    "fail_runs": 0,
                    "error_runs": 0,
                    "pass_rate": 1.0,
                    "decision_stable": True,
                    "always_fail": False,
                    "statuses": ["PASS", "PASS"],
                    "text_variant_count": 2,
                },
                {
                    "id": "gx-illu-a",
                    "observed_runs": 2,
                    "pass_runs": 2,
                    "fail_runs": 0,
                    "error_runs": 0,
                    "pass_rate": 1.0,
                    "decision_stable": True,
                    "always_fail": False,
                    "statuses": ["PASS", "PASS"],
                    "text_variant_count": 1,
                },
            ]
        }
        growth_case_map: dict[str, dict[str, Any]] = {
            "gx-hand-a": {
                "id": "gx-hand-a",
                "lane": "handwriting",
                "source_name": "hand-a.png",
                "image_path": "/tmp/hand-a.png",
                "must_contain_any": ["mechanical checking fingers"],
            },
            "gx-hand-b": {
                "id": "gx-hand-b",
                "lane": "handwriting",
                "source_name": "hand-b.png",
                "image_path": "/tmp/hand-b.png",
                "must_contain_any": ["restore deleted spectral"],
            },
            "gx-type-a": {
                "id": "gx-type-a",
                "lane": "typed",
                "source_name": "type-a.png",
                "image_path": "/tmp/type-a.png",
                "must_contain_any": ["instance engineering design"],
            },
            "gx-illu-a": {
                "id": "gx-illu-a",
                "lane": "illustration",
                "source_name": "illu-a.png",
                "image_path": "/tmp/illu-a.png",
                "must_contain_any": ["correcting simulacra reality"],
            },
        }
        review_index = {
            "/tmp/hand-a.png": [{"ocr_framing_signal": True, "lane": "handwriting"}],
            "/tmp/hand-b.png": [{"ocr_framing_signal": True, "lane": "handwriting"}],
            "/tmp/type-a.png": [{"ocr_framing_signal": True, "lane": "typed"}],
            "/tmp/illu-a.png": [{"ocr_framing_signal": True, "lane": "illustration"}],
        }

        report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            run_case_map={},
            metrics_map={},
            review_index=review_index,
            min_runs=1,
            include_unstable=True,
            require_ocr_framing=True,
            include_exploratory=True,
            exploratory_max_cases=3,
        )

        self.assertEqual(report["summary"]["exploratory_cases"], 3)
        self.assertEqual(
            report["summary"]["exploratory_lane_counts"],
            {"handwriting": 1, "illustration": 1, "typed": 1},
        )

    def test_exploratory_refines_anchor_any_terms(self) -> None:
        stability_payload = {
            "cases": [
                {
                    "id": "gx-pass-4",
                    "observed_runs": 2,
                    "pass_runs": 2,
                    "fail_runs": 0,
                    "error_runs": 0,
                    "pass_rate": 1.0,
                    "decision_stable": True,
                    "always_fail": False,
                    "statuses": ["PASS", "PASS"],
                }
            ]
        }
        growth_case_map: dict[str, dict[str, Any]] = {
            "gx-pass-4": {
                "id": "gx-pass-4",
                "lane": "handwriting",
                "source_name": "sample-pass-4.png",
                "image_path": "/tmp/sample-pass-4.png",
                "must_contain_any": [
                    "thing",
                    "1102",
                    "archival",
                    "tumbles",
                    "tumble",
                    "increas",
                    "increases",
                    "field notes",
                    "restore deleted spectral",
                ],
            }
        }
        review_index = {
            "/tmp/sample-pass-4.png": [{"ocr_framing_signal": True, "lane": "handwriting"}]
        }

        report = build_fail_cohort(
            stability_payload=stability_payload,
            growth_case_map=growth_case_map,
            run_case_map={},
            metrics_map={},
            review_index=review_index,
            min_runs=1,
            include_unstable=True,
            require_ocr_framing=True,
            include_exploratory=True,
            exploratory_max_cases=5,
        )

        self.assertEqual(report["summary"]["exploratory_cases"], 1)
        exploratory = report["exploratory_cases"][0]
        overrides = exploratory.get("focus_overrides")
        self.assertIsInstance(overrides, dict)
        self.assertEqual(
            overrides.get("must_contain_any"),
            ["archival", "tumbles", "increases", "restore deleted spectral"],
        )


if __name__ == "__main__":
    unittest.main()
