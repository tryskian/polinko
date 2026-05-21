import sqlite3
import unittest
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.build_manual_evals_db import build_manual_evals_db
from tools.manual_evals_db_health import (
    ACTIONABLES_SCHEMA_VERSION,
    COHORTS_SCHEMA_VERSION,
    OCR_RETRY_CANDIDATES_SCHEMA_VERSION,
    build_manual_evals_health_report,
    build_ocr_retry_candidates_report,
    build_open_feedback_actionables_report,
    build_open_feedback_cohorts_report,
    format_manual_evals_health_report,
    format_ocr_retry_candidates_report,
    format_open_feedback_actionables_report,
    format_open_feedback_cohorts_report,
)
from tests.test_build_manual_evals_db import _init_history_db


class ManualEvalsDbHealthTests(unittest.TestCase):
    def test_health_report_summarizes_read_only_quality_signals(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            history_db = tmp / "history.db"
            output_db = tmp / "manual_evals.db"
            _init_history_db(
                history_db,
                feedback_outcome="fail",
                source_name="guardrail-note.txt",
            )
            with closing(sqlite3.connect(history_db)) as conn:
                conn.execute(
                    """
                    UPDATE message_feedback
                    SET status = 'open',
                        recommended_action = 'Retry OCR with a tighter crop and attach fresh image evidence for comparison.'
                    """
                )
                conn.commit()
            build_manual_evals_db(
                history_db=history_db,
                output_db=output_db,
                image_roots=[],
                include_thumbnails=False,
            )

            before_history = history_db.stat().st_mtime_ns
            before_output = output_db.stat().st_mtime_ns
            report = build_manual_evals_health_report(db_path=output_db)
            summary = format_manual_evals_health_report(report)
            actionables = build_open_feedback_actionables_report(
                db_path=output_db,
                outcome="fail",
                limit=10,
            )
            actionables_summary = format_open_feedback_actionables_report(
                actionables,
            )
            cohort_actionables = build_open_feedback_actionables_report(
                db_path=output_db,
                outcome="fail",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            empty_cohort_actionables = build_open_feedback_actionables_report(
                db_path=output_db,
                outcome="fail",
                cohort="style_regression",
                limit=10,
            )
            cohorts = build_open_feedback_cohorts_report(
                db_path=output_db,
                outcome="fail",
            )
            filtered_cohorts = build_open_feedback_cohorts_report(
                db_path=output_db,
                outcome="fail",
                cohort="ocr_retry_evidence",
            )
            cohorts_summary = format_open_feedback_cohorts_report(cohorts)
            retry_candidates = build_ocr_retry_candidates_report(
                db_path=output_db,
                outcome="fail",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            retry_candidates_summary = format_ocr_retry_candidates_report(
                retry_candidates
            )
            after_history = history_db.stat().st_mtime_ns
            after_output = output_db.stat().st_mtime_ns

            self.assertEqual(before_history, after_history)
            self.assertEqual(before_output, after_output)
            self.assertEqual(report["state"], "attention")
            self.assertEqual(report["manual_evals_db"]["integrity"], "ok")
            self.assertEqual(report["counts"]["sessions"], 1)
            self.assertEqual(report["counts"]["feedback"], 1)
            self.assertEqual(report["image_quality"]["missing_assets"], 1)
            self.assertEqual(report["image_quality"]["missing_ocr_runs"], 1)
            self.assertEqual(
                report["image_quality"]["missing_debt_by_family"],
                [
                    {
                        "source_family": "text_fixture",
                        "missing_assets": 1,
                        "missing_ocr_runs": 1,
                    }
                ],
            )
            self.assertEqual(report["feedback_quality"]["linked_to_ocr_result"], 1)
            self.assertEqual(report["feedback_quality"]["unlinked_to_ocr_result"], 0)
            self.assertEqual(
                report["feedback_quality"]["open_debt_by_outcome"],
                [
                    {
                        "era": "current",
                        "outcome": "fail",
                        "status": "open",
                        "rows": 1,
                        "sessions": 1,
                        "rows_with_note": 1,
                        "rows_with_recommended_action": 1,
                        "rows_with_action_taken": 0,
                        "linked_to_ocr_result": 1,
                        "same_session_ocr": 1,
                    }
                ],
            )
            self.assertIn("manual_evals.db health: state=attention", summary)
            self.assertIn("missing image debt:", summary)
            self.assertIn("- text_fixture: assets=1 ocr_runs=1", summary)
            self.assertIn("open feedback debt:", summary)
            self.assertIn(
                "- current fail: rows=1 sessions=1 notes=1 recommended_actions=1 "
                "action_taken=0 linked_to_ocr_result=1 same_session_ocr=1",
                summary,
            )
            self.assertIn("linked_to_ocr_result=1/1", summary)
            self.assertEqual(
                actionables["schema_version"],
                ACTIONABLES_SCHEMA_VERSION,
            )
            self.assertEqual(actionables["state"], "ok")
            self.assertEqual(
                actionables["counts"],
                {
                    "total_rows": 1,
                    "returned_rows": 1,
                    "limit_applied": False,
                },
            )
            self.assertEqual(actionables["filters"]["outcome"], "fail")
            self.assertEqual(actionables["filters"]["cohort"], "")
            self.assertEqual(len(actionables["rows"]), 1)
            actionable = actionables["rows"][0]
            self.assertEqual(actionable["feedback_id"], 1)
            self.assertEqual(actionable["outcome"], "fail")
            self.assertEqual(actionable["status"], "open")
            self.assertEqual(actionable["session_id"], "chat-1")
            self.assertEqual(actionable["message_id"], "m-result-1")
            self.assertEqual(actionable["note"], "manual note")
            self.assertEqual(
                actionable["recommended_action"],
                "Retry OCR with a tighter crop and attach fresh image evidence "
                "for comparison.",
            )
            self.assertTrue(actionable["has_recommended_action"])
            self.assertFalse(actionable["has_action_taken"])
            self.assertEqual(
                actionable["action_cohort"],
                {
                    "id": "ocr_retry_evidence",
                    "description": "Retry OCR/crop and attach fresh image evidence.",
                },
            )
            self.assertEqual(
                actionable["ocr_context"],
                {
                    "linked_to_ocr_result": True,
                    "same_session_ocr_runs": 1,
                    "latest_same_session_ocr": {
                        "run_id": "ocr-1",
                        "source_name": "guardrail-note.txt",
                        "status": "ok",
                    },
                },
            )
            self.assertIn(
                "manual eval open feedback actionables: state=ok rows=1/1 "
                "outcome=fail cohort=all limit=10",
                actionables_summary,
            )
            self.assertIn(
                "feedback=1 era=current outcome=fail status=open "
                "cohort=ocr_retry_evidence",
                actionables_summary,
            )
            self.assertIn(
                "recommended_action=Retry OCR with a tighter crop and attach fresh "
                "image evidence for comparison.",
                actionables_summary,
            )
            self.assertIn(
                "ocr_context: linked_to_ocr_result=yes same_session_ocr_runs=1",
                actionables_summary,
            )
            self.assertEqual(
                cohort_actionables["counts"],
                {
                    "total_rows": 1,
                    "returned_rows": 1,
                    "limit_applied": False,
                },
            )
            self.assertEqual(
                cohort_actionables["filters"]["cohort"],
                "ocr_retry_evidence",
            )
            self.assertEqual(empty_cohort_actionables["counts"]["total_rows"], 0)
            self.assertEqual(empty_cohort_actionables["rows"], [])
            self.assertEqual(cohorts["schema_version"], COHORTS_SCHEMA_VERSION)
            self.assertEqual(cohorts["state"], "ok")
            self.assertEqual(
                cohorts["counts"],
                {
                    "total_rows": 1,
                    "cohorts": 1,
                },
            )
            self.assertEqual(cohorts["filters"]["cohort_basis"], "recommended_action")
            self.assertEqual(cohorts["filters"]["cohort"], "")
            self.assertEqual(
                cohorts["cohorts"],
                [
                    {
                        "cohort_id": "ocr_retry_evidence",
                        "description": (
                            "Retry OCR/crop and attach fresh image evidence."
                        ),
                        "rows": 1,
                        "sessions": 1,
                        "outcomes": {"fail": 1},
                        "rows_with_note": 1,
                        "rows_with_recommended_action": 1,
                        "rows_with_action_taken": 0,
                        "linked_to_ocr_result": 1,
                        "same_session_ocr": 1,
                        "sample_feedback_ids": [1],
                    }
                ],
            )
            self.assertEqual(filtered_cohorts["counts"]["total_rows"], 1)
            self.assertEqual(
                filtered_cohorts["filters"]["cohort"], "ocr_retry_evidence"
            )
            self.assertEqual(filtered_cohorts["cohorts"], cohorts["cohorts"])
            self.assertIn(
                "manual eval open feedback cohorts: state=ok rows=1 cohorts=1 "
                "outcome=fail cohort=all basis=recommended_action",
                cohorts_summary,
            )
            self.assertIn(
                "- ocr_retry_evidence: rows=1 sessions=1 outcomes=fail=1",
                cohorts_summary,
            )
            self.assertIn("sample_feedback=1", cohorts_summary)
            self.assertEqual(
                retry_candidates["schema_version"],
                OCR_RETRY_CANDIDATES_SCHEMA_VERSION,
            )
            self.assertEqual(retry_candidates["state"], "ok")
            self.assertEqual(
                retry_candidates["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "candidate_groups": 1,
                    "limit_applied": False,
                },
            )
            self.assertEqual(retry_candidates["filters"]["outcome"], "fail")
            self.assertEqual(
                retry_candidates["filters"]["cohort"], "ocr_retry_evidence"
            )
            self.assertEqual(
                retry_candidates["filters"]["packet_basis"],
                "recommended_action_and_same_session_ocr",
            )
            self.assertEqual(len(retry_candidates["candidate_groups"]), 1)
            candidate_group = retry_candidates["candidate_groups"][0]
            self.assertEqual(candidate_group["session_id"], "chat-1")
            self.assertEqual(candidate_group["feedback_ids"], [1])
            self.assertEqual(candidate_group["same_session_ocr_runs"], 1)
            self.assertEqual(
                candidate_group["latest_same_session_ocr"]["run_id"],
                "ocr-1",
            )
            self.assertEqual(
                candidate_group["latest_same_session_ocr"]["source_name"],
                "guardrail-note.txt",
            )
            self.assertEqual(
                candidate_group["latest_same_session_ocr"]["image_asset"]["status"],
                "missing",
            )
            self.assertEqual(
                candidate_group["feedback_rows"][0]["feedback_id"],
                1,
            )
            self.assertIn(
                "manual eval OCR retry candidates: state=ok rows=1/1 groups=1 "
                "outcome=fail cohort=ocr_retry_evidence",
                retry_candidates_summary,
            )
            self.assertIn(
                "session=chat-1 source_session=chat-1 feedback=1 ocr_runs=1",
                retry_candidates_summary,
            )
            self.assertIn(
                "latest_run=ocr-1 latest_source=guardrail-note.txt",
                retry_candidates_summary,
            )

            with closing(sqlite3.connect(output_db)) as conn:
                self.assertEqual(
                    conn.execute("PRAGMA integrity_check").fetchone()[0], "ok"
                )

    def test_health_report_handles_missing_warehouse(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_db = Path(tmpdir) / "missing.db"

            report = build_manual_evals_health_report(db_path=output_db)
            summary = format_manual_evals_health_report(report)

            self.assertEqual(report["state"], "error")
            self.assertFalse(report["manual_evals_db"]["exists"])
            self.assertIn("state=error", summary)


if __name__ == "__main__":
    unittest.main()
