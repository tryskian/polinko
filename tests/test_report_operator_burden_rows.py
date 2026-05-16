import unittest

from tools.report_operator_burden_rows import build_report
from tools.report_operator_burden_rows import render_markdown


def _payload(rows):
    return {
        "lane": "operator_burden",
        "version": 1,
        "hypothesis_id": "H-001",
        "rows": rows,
    }


class OperatorBurdenRowsReportTests(unittest.TestCase):
    def test_build_report_counts_retained_failure_and_pass(self) -> None:
        report = build_report(
            _payload(
                [
                    {
                        "id": "ob-1",
                        "title": "fail row",
                        "source_note": "docs/research/operator-burden-seed-2026-05-09.md",
                        "source_ids": ["R-D"],
                        "task_shape": "direct_mapping",
                        "expected_boundary": "direct execution",
                        "observed_pattern": "commentary replaced execution",
                        "dimensions": {
                            "reference_binding": "fail",
                            "operation_fidelity": "fail",
                            "decision_clarity": "fail",
                        },
                        "verdict": "fail",
                        "failure_disposition": "retain",
                        "note": "keep it",
                    },
                    {
                        "id": "ob-2",
                        "title": "pass row",
                        "source_note": "docs/research/operator-burden-seed-2026-05-09.md",
                        "source_ids": ["D-158"],
                        "task_shape": "sparse_control_execution",
                        "expected_boundary": "objective + checks",
                        "observed_pattern": "stayed clear",
                        "dimensions": {
                            "reference_binding": "pass",
                            "operation_fidelity": "pass",
                            "decision_clarity": "pass",
                        },
                        "verdict": "pass",
                        "failure_disposition": None,
                        "note": "good row",
                    },
                ]
            )
        )
        self.assertEqual(report["row_count"], 2)
        self.assertEqual(report["verdict_counts"]["pass"], 1)
        self.assertEqual(report["verdict_counts"]["fail"], 1)
        self.assertEqual(report["failure_disposition_counts"]["retain"], 1)
        self.assertEqual(report["failure_disposition_counts"]["evict"], 0)
        self.assertEqual(report["pass_anchors"][0]["id"], "ob-2")
        self.assertEqual(report["retained_failures"][0]["id"], "ob-1")

    def test_build_report_counts_evicted_failure(self) -> None:
        report = build_report(
            _payload(
                [
                    {
                        "id": "ob-1",
                        "title": "evict row",
                        "source_note": "docs/research/operator-burden-promotion-2026-05-09.md",
                        "source_ids": ["x-1"],
                        "task_shape": "duplicate_archive_case",
                        "expected_boundary": "distinct case",
                        "observed_pattern": "quoted duplicate",
                        "dimensions": {
                            "reference_binding": "fail",
                            "operation_fidelity": "fail",
                            "decision_clarity": "fail",
                        },
                        "verdict": "fail",
                        "failure_disposition": "evict",
                        "note": "throw it out",
                    }
                ]
            )
        )
        self.assertEqual(report["verdict_counts"]["fail"], 1)
        self.assertEqual(report["failure_disposition_counts"]["retain"], 0)
        self.assertEqual(report["failure_disposition_counts"]["evict"], 1)
        self.assertEqual(report["evicted_failures"][0]["id"], "ob-1")

    def test_build_report_rejects_fail_without_disposition(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "failure_disposition"):
            build_report(
                _payload(
                    [
                        {
                            "id": "ob-1",
                            "title": "fail row",
                            "source_note": "docs/research/operator-burden-seed-2026-05-09.md",
                            "source_ids": ["R-D"],
                            "task_shape": "direct_mapping",
                            "expected_boundary": "direct execution",
                            "observed_pattern": "commentary replaced execution",
                            "dimensions": {"reference_binding": "fail"},
                            "verdict": "fail",
                            "note": "bad row",
                        }
                    ]
                )
            )

    def test_build_report_rejects_pass_with_disposition(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "must not set failure_disposition"):
            build_report(
                _payload(
                    [
                        {
                            "id": "ob-1",
                            "title": "pass row",
                            "source_note": "docs/research/operator-burden-seed-2026-05-09.md",
                            "source_ids": ["D-158"],
                            "task_shape": "sparse_control_execution",
                            "expected_boundary": "objective + checks",
                            "observed_pattern": "stayed clear",
                            "dimensions": {"reference_binding": "pass"},
                            "verdict": "pass",
                            "failure_disposition": "retain",
                            "note": "bad row",
                        }
                    ]
                )
            )

    def test_render_markdown_includes_retained_failures(self) -> None:
        report = build_report(
            _payload(
                [
                    {
                        "id": "ob-1",
                        "title": "fail row",
                        "source_note": "docs/research/operator-burden-seed-2026-05-09.md",
                        "source_ids": ["R-D"],
                        "task_shape": "direct_mapping",
                        "expected_boundary": "direct execution",
                        "observed_pattern": "commentary replaced execution",
                        "dimensions": {"reference_binding": "fail"},
                        "verdict": "fail",
                        "failure_disposition": "retain",
                        "note": "keep it",
                    }
                ]
            )
        )
        markdown = render_markdown(report)
        self.assertIn("Retained Failures", markdown)
        self.assertIn("ob-1", markdown)

    def test_render_markdown_includes_pass_anchors(self) -> None:
        report = build_report(
            _payload(
                [
                    {
                        "id": "ob-1",
                        "title": "pass row",
                        "source_note": "docs/research/operator-burden-seed-2026-05-09.md",
                        "source_ids": ["D-158"],
                        "task_shape": "sparse_control_execution",
                        "expected_boundary": "objective + checks",
                        "observed_pattern": "stayed clear",
                        "dimensions": {"reference_binding": "pass"},
                        "verdict": "pass",
                        "failure_disposition": None,
                        "note": "good row",
                    }
                ]
            )
        )
        markdown = render_markdown(report)
        self.assertIn("Pass Anchors", markdown)
        self.assertIn("ob-1", markdown)

    def test_render_markdown_includes_evicted_failures(self) -> None:
        report = build_report(
            _payload(
                [
                    {
                        "id": "ob-1",
                        "title": "evict row",
                        "source_note": "docs/research/operator-burden-promotion-2026-05-09.md",
                        "source_ids": ["x-1"],
                        "task_shape": "duplicate_archive_case",
                        "expected_boundary": "distinct case",
                        "observed_pattern": "quoted duplicate",
                        "dimensions": {"reference_binding": "fail"},
                        "verdict": "fail",
                        "failure_disposition": "evict",
                        "note": "throw it out",
                    }
                ]
            )
        )
        markdown = render_markdown(report)
        self.assertIn("Evicted Failures", markdown)
        self.assertIn("ob-1", markdown)


if __name__ == "__main__":
    unittest.main()
