import sqlite3
import unittest
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.build_manual_evals_db import build_manual_evals_db
from tools.manual_evals_db_health import (
    ACTIONABLES_SCHEMA_VERSION,
    build_manual_evals_health_report,
    build_open_feedback_actionables_report,
    format_manual_evals_health_report,
    format_open_feedback_actionables_report,
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
                        recommended_action = 'Review this case before closure.'
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
                "Review this case before closure.",
            )
            self.assertTrue(actionable["has_recommended_action"])
            self.assertFalse(actionable["has_action_taken"])
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
                "outcome=fail limit=10",
                actionables_summary,
            )
            self.assertIn("feedback=1 era=current outcome=fail", actionables_summary)
            self.assertIn(
                "recommended_action=Review this case before closure.",
                actionables_summary,
            )
            self.assertIn(
                "ocr_context: linked_to_ocr_result=yes same_session_ocr_runs=1",
                actionables_summary,
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
