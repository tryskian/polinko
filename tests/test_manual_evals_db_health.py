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
    OCR_RETRY_INPUT_PACKET_SCHEMA_VERSION,
    OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION,
    OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION,
    build_manual_evals_health_report,
    build_ocr_retry_candidates_report,
    build_ocr_retry_input_packet_report,
    build_ocr_retry_source_provenance_report,
    build_ocr_retry_source_verification_report,
    build_open_feedback_actionables_report,
    build_open_feedback_cohorts_report,
    format_manual_evals_health_report,
    format_ocr_retry_candidates_report,
    format_ocr_retry_input_packet_report,
    format_ocr_retry_source_provenance_report,
    format_ocr_retry_source_verification_report,
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
                conn.execute(
                    """
                    INSERT INTO chat_messages (
                      session_id, role, content, created_at, message_id,
                      parent_message_id
                    ) VALUES (
                      'chat-1', 'user', 'source upload prompt', 120,
                      'm-source-1', NULL
                    )
                    """
                )
                conn.execute(
                    """
                    INSERT INTO chat_messages (
                      session_id, role, content, created_at, message_id,
                      parent_message_id
                    ) VALUES (
                      'chat-1', 'assistant',
                      'hello world response that received manual feedback',
                      155, 'm-result-1', 'm-source-1'
                    )
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
            source_verification = build_ocr_retry_source_verification_report(
                db_path=output_db,
                outcome="fail",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            source_verification_summary = format_ocr_retry_source_verification_report(
                source_verification
            )
            source_provenance = build_ocr_retry_source_provenance_report(
                db_path=output_db,
                outcome="fail",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            source_provenance_summary = format_ocr_retry_source_provenance_report(
                source_provenance
            )
            input_packet = build_ocr_retry_input_packet_report(
                db_path=output_db,
                outcome="fail",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            input_packet_summary = format_ocr_retry_input_packet_report(input_packet)
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
                    "ready_candidate_groups": 1,
                    "needs_review_candidate_groups": 0,
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
            self.assertEqual(
                candidate_group["readiness"],
                {
                    "state": "ready",
                    "flags": [],
                    "basis": ("explicit_result_message_match_and_same_session_context"),
                    "explicit_feedback_to_result_links": 1,
                    "unlinked_feedback_rows": 0,
                    "same_session_ocr_runs": 1,
                    "linked_ocr_run_ids": ["ocr-1"],
                    "latest_ocr_is_confirmed_feedback_result": True,
                },
            )
            self.assertIn(
                "manual eval OCR retry candidates: state=ok rows=1/1 groups=1 "
                "needs_review=0 outcome=fail cohort=ocr_retry_evidence",
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
            self.assertIn(
                "readiness=ready flags=none explicit_links=1 "
                "unlinked_feedback=0 latest_confirmed=yes",
                retry_candidates_summary,
            )
            self.assertEqual(
                source_verification["schema_version"],
                OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION,
            )
            self.assertEqual(
                source_verification["candidate_schema_version"],
                OCR_RETRY_CANDIDATES_SCHEMA_VERSION,
            )
            self.assertEqual(
                source_verification["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "verification_items": 1,
                    "ready_verification_items": 1,
                    "needs_review_verification_items": 0,
                    "source_candidates": 1,
                    "limit_applied": False,
                },
            )
            verification_item = source_verification["verification_items"][0]
            self.assertEqual(
                verification_item["confirmation"],
                {
                    "state": "confirmed",
                    "basis": "explicit_feedback_result_links_before_rerun",
                    "reasons": [],
                },
            )
            self.assertEqual(
                verification_item["feedback_rows"][0]["recommended_action"],
                "Retry OCR with a tighter crop and attach fresh image evidence "
                "for comparison.",
            )
            self.assertEqual(
                verification_item["source_candidates"][0]["source_image_name"],
                "guardrail-note.txt",
            )
            self.assertIn(
                "manual eval OCR retry source verification: state=ok rows=1/1 "
                "items=1 needs_review=0 source_candidates=1",
                source_verification_summary,
            )
            self.assertIn(
                "confirmation=confirmed ocr_runs=1",
                source_verification_summary,
            )
            self.assertIn("reasons=none", source_verification_summary)
            self.assertIn(
                "recommended_action=Retry OCR with a tighter crop and attach fresh "
                "image evidence for comparison.",
                source_verification_summary,
            )
            self.assertIn(
                "ocr=ocr-1 source_image=guardrail-note.txt",
                source_verification_summary,
            )
            self.assertEqual(
                source_provenance["schema_version"],
                OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION,
            )
            self.assertEqual(
                source_provenance["verification_schema_version"],
                OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION,
            )
            self.assertEqual(
                source_provenance["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "provenance_items": 1,
                    "source_history_available": 1,
                    "feedback_messages": 1,
                    "feedback_messages_found": 1,
                    "ocr_runs": 1,
                    "ocr_source_message_ids_present": 1,
                    "ocr_result_message_ids_present": 1,
                    "exact_feedback_result_links": 1,
                    "limit_applied": False,
                },
            )
            provenance_item = source_provenance["provenance_items"][0]
            self.assertEqual(provenance_item["source_history"]["state"], "ok")
            self.assertEqual(
                provenance_item["feedback_messages"][0]["source_message"]["state"],
                "found",
            )
            self.assertEqual(
                provenance_item["ocr_message_provenance"][0][
                    "exact_feedback_result_link"
                ],
                True,
            )
            self.assertEqual(
                provenance_item["ocr_message_provenance"][0]["source_message"][
                    "content_preview"
                ],
                "source upload prompt",
            )
            self.assertEqual(
                provenance_item["ocr_message_provenance"][0]["result_message"][
                    "content_preview"
                ],
                "hello world response that received manual feedback",
            )
            self.assertIn(
                "manual eval OCR retry source provenance: state=ok rows=1/1 "
                "items=1 source_history=1/1 feedback_sources=1/1 ocr_runs=1 "
                "source_message_ids=1 result_message_ids=1 exact_links=1",
                source_provenance_summary,
            )
            self.assertIn(
                "feedback=1 message=m-result-1 source_state=found role=assistant",
                source_provenance_summary,
            )
            self.assertIn(
                "ocr=ocr-1 source_image=guardrail-note.txt source_message=m-source-1",
                source_provenance_summary,
            )
            self.assertIn("exact_feedback_link=yes", source_provenance_summary)
            self.assertEqual(
                input_packet["schema_version"],
                OCR_RETRY_INPUT_PACKET_SCHEMA_VERSION,
            )
            self.assertEqual(
                input_packet["verification_schema_version"],
                OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION,
            )
            self.assertEqual(
                input_packet["provenance_schema_version"],
                OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION,
            )
            self.assertEqual(
                input_packet["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "input_items": 1,
                    "blocked_input_items": 0,
                    "feedback_inputs": 1,
                    "feedback_sources_found": 1,
                    "rerun_inputs": 1,
                    "resolved_rerun_inputs": 0,
                    "unresolved_rerun_inputs": 1,
                    "ocr_source_message_ids_present": 1,
                    "ocr_result_message_ids_present": 1,
                    "exact_feedback_result_links": 1,
                    "limit_applied": False,
                },
            )
            input_item = input_packet["input_items"][0]
            self.assertEqual(
                input_item["blocker_state"],
                {
                    "state": "ready",
                    "reason_code": "",
                    "reason": "",
                    "next_action": "review_exact_link_before_feedback_closure",
                },
            )
            self.assertEqual(
                input_item["feedback_inputs"][0]["source_message"]["content_preview"],
                "hello world response that received manual feedback",
            )
            self.assertEqual(input_item["rerun_inputs"][0]["run_id"], "ocr-1")
            self.assertTrue(input_item["rerun_inputs"][0]["exact_feedback_result_link"])
            self.assertEqual(
                input_item["rerun_inputs"][0]["image_asset"]["status"], "missing"
            )
            self.assertIn(
                "manual eval OCR retry input packet: state=ok rows=1/1 items=1 "
                "blocked=0 feedback_inputs=1/1 rerun_inputs=1 resolved=0/1 "
                "source_message_ids=1 result_message_ids=1 exact_links=1",
                input_packet_summary,
            )
            self.assertIn(
                "blocker=ready next=review_exact_link_before_feedback_closure",
                input_packet_summary,
            )
            self.assertIn(
                "feedback=1 message=m-result-1 source_state=found role=assistant",
                input_packet_summary,
            )
            self.assertIn(
                "ocr=ocr-1 source_image=guardrail-note.txt image_status=missing",
                input_packet_summary,
            )

            with closing(sqlite3.connect(output_db)) as conn:
                self.assertEqual(
                    conn.execute("PRAGMA integrity_check").fetchone()[0], "ok"
                )

    def test_ocr_retry_candidates_flag_ambiguous_same_session_context(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            history_db = tmp / "history.db"
            output_db = tmp / "manual_evals.db"
            _init_history_db(
                history_db,
                feedback_outcome="partial",
                source_name="first.png",
                run_id="ocr-old",
            )
            with closing(sqlite3.connect(history_db)) as conn:
                conn.execute(
                    """
                    UPDATE message_feedback
                    SET message_id = 'm-feedback-unlinked',
                        status = 'open',
                        recommended_action = 'Retry OCR with a tighter crop and attach fresh image evidence for comparison.'
                    """
                )
                conn.execute(
                    """
                    INSERT INTO ocr_runs (
                      run_id, session_id, source_name, mime_type, source_message_id,
                      result_message_id, status, extracted_text, created_at
                    ) VALUES (
                      'ocr-new', 'chat-1', 'second.png', 'image/png', 'm-source-2',
                      'm-result-2', 'ok', 'second OCR text for ambiguity review', 190
                    )
                    """
                )
                conn.executemany(
                    """
                    INSERT INTO chat_messages (
                      session_id, role, content, created_at, message_id,
                      parent_message_id
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            "chat-1",
                            "assistant",
                            "manual feedback points to an unlinked assistant row",
                            170,
                            "m-feedback-unlinked",
                            None,
                        ),
                        (
                            "chat-1",
                            "user",
                            "first source image upload",
                            120,
                            "m-source-1",
                            None,
                        ),
                        (
                            "chat-1",
                            "assistant",
                            "first OCR text",
                            151,
                            "m-result-1",
                            "m-source-1",
                        ),
                        (
                            "chat-1",
                            "user",
                            "second source image upload",
                            180,
                            "m-source-2",
                            None,
                        ),
                        (
                            "chat-1",
                            "assistant",
                            "second OCR text for ambiguity review",
                            191,
                            "m-result-2",
                            "m-source-2",
                        ),
                    ],
                )
                conn.commit()
            build_manual_evals_db(
                history_db=history_db,
                output_db=output_db,
                image_roots=[],
                include_thumbnails=False,
            )

            retry_candidates = build_ocr_retry_candidates_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            retry_candidates_summary = format_ocr_retry_candidates_report(
                retry_candidates
            )
            source_verification = build_ocr_retry_source_verification_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            source_verification_summary = format_ocr_retry_source_verification_report(
                source_verification
            )
            source_provenance = build_ocr_retry_source_provenance_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            source_provenance_summary = format_ocr_retry_source_provenance_report(
                source_provenance
            )
            input_packet = build_ocr_retry_input_packet_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            input_packet_summary = format_ocr_retry_input_packet_report(input_packet)

            self.assertEqual(
                retry_candidates["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "candidate_groups": 1,
                    "ready_candidate_groups": 0,
                    "needs_review_candidate_groups": 1,
                    "limit_applied": False,
                },
            )
            candidate_group = retry_candidates["candidate_groups"][0]
            self.assertEqual(
                candidate_group["readiness"],
                {
                    "state": "needs_review",
                    "flags": [
                        "multiple_same_session_ocr_runs",
                        "missing_feedback_to_result_link",
                        "latest_ocr_is_context_only",
                    ],
                    "basis": ("explicit_result_message_match_and_same_session_context"),
                    "explicit_feedback_to_result_links": 0,
                    "unlinked_feedback_rows": 1,
                    "same_session_ocr_runs": 2,
                    "linked_ocr_run_ids": [],
                    "latest_ocr_is_confirmed_feedback_result": False,
                },
            )
            self.assertEqual(
                candidate_group["latest_same_session_ocr"]["run_id"],
                "ocr-new",
            )
            self.assertEqual(len(candidate_group["ocr_runs"]), 2)
            self.assertIn(
                "manual eval OCR retry candidates: state=ok rows=1/1 groups=1 "
                "needs_review=1 outcome=partial cohort=ocr_retry_evidence",
                retry_candidates_summary,
            )
            self.assertIn(
                "readiness=needs_review "
                "flags=multiple_same_session_ocr_runs,missing_feedback_to_result_link,"
                "latest_ocr_is_context_only explicit_links=0 "
                "unlinked_feedback=1 latest_confirmed=no",
                retry_candidates_summary,
            )
            self.assertIn("same_session_ocr_context:", retry_candidates_summary)
            self.assertIn(
                "ocr=ocr-new source=second.png status=ok",
                retry_candidates_summary,
            )
            self.assertIn(
                "preview=second OCR text for ambiguity review",
                retry_candidates_summary,
            )
            self.assertEqual(
                source_verification["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "verification_items": 1,
                    "ready_verification_items": 0,
                    "needs_review_verification_items": 1,
                    "source_candidates": 2,
                    "limit_applied": False,
                },
            )
            verification_item = source_verification["verification_items"][0]
            self.assertEqual(
                verification_item["confirmation"]["state"],
                "not_confirmed",
            )
            self.assertEqual(
                [item["code"] for item in verification_item["confirmation"]["reasons"]],
                [
                    "multiple_same_session_ocr_runs",
                    "missing_feedback_to_result_link",
                    "latest_ocr_is_context_only",
                ],
            )
            self.assertEqual(
                verification_item["source_candidates"][0]["run_id"],
                "ocr-new",
            )
            self.assertEqual(
                verification_item["source_candidates"][0]["source_image_name"],
                "second.png",
            )
            self.assertIn(
                "manual eval OCR retry source verification: state=ok rows=1/1 "
                "items=1 needs_review=1 source_candidates=2",
                source_verification_summary,
            )
            self.assertIn(
                "confirmation=not_confirmed ocr_runs=2",
                source_verification_summary,
            )
            self.assertIn(
                "multiple_same_session_ocr_runs: same source session has multiple",
                source_verification_summary,
            )
            self.assertIn(
                "missing_feedback_to_result_link: feedback message_id does not "
                "match any OCR result_message_id",
                source_verification_summary,
            )
            self.assertIn(
                "latest_ocr_is_context_only: latest same-session OCR run is context "
                "only",
                source_verification_summary,
            )
            self.assertIn(
                "ocr=ocr-new source_image=second.png",
                source_verification_summary,
            )
            self.assertEqual(
                source_provenance["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "provenance_items": 1,
                    "source_history_available": 1,
                    "feedback_messages": 1,
                    "feedback_messages_found": 1,
                    "ocr_runs": 2,
                    "ocr_source_message_ids_present": 2,
                    "ocr_result_message_ids_present": 2,
                    "exact_feedback_result_links": 0,
                    "limit_applied": False,
                },
            )
            provenance_item = source_provenance["provenance_items"][0]
            self.assertEqual(
                provenance_item["feedback_messages"][0]["source_message"][
                    "content_preview"
                ],
                "manual feedback points to an unlinked assistant row",
            )
            self.assertEqual(
                provenance_item["ocr_message_provenance"][0]["run_id"],
                "ocr-new",
            )
            self.assertEqual(
                provenance_item["ocr_message_provenance"][0]["result_message"][
                    "content_preview"
                ],
                "second OCR text for ambiguity review",
            )
            self.assertFalse(
                provenance_item["ocr_message_provenance"][0][
                    "exact_feedback_result_link"
                ]
            )
            self.assertIn(
                "manual eval OCR retry source provenance: state=ok rows=1/1 "
                "items=1 source_history=1/1 feedback_sources=1/1 ocr_runs=2 "
                "source_message_ids=2 result_message_ids=2 exact_links=0",
                source_provenance_summary,
            )
            self.assertIn(
                "feedback=1 message=m-feedback-unlinked source_state=found",
                source_provenance_summary,
            )
            self.assertIn(
                "ocr=ocr-new source_image=second.png source_message=m-source-2",
                source_provenance_summary,
            )
            self.assertIn("exact_feedback_link=no", source_provenance_summary)
            self.assertEqual(
                input_packet["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "input_items": 1,
                    "blocked_input_items": 1,
                    "feedback_inputs": 1,
                    "feedback_sources_found": 1,
                    "rerun_inputs": 2,
                    "resolved_rerun_inputs": 0,
                    "unresolved_rerun_inputs": 2,
                    "ocr_source_message_ids_present": 2,
                    "ocr_result_message_ids_present": 2,
                    "exact_feedback_result_links": 0,
                    "limit_applied": False,
                },
            )
            input_item = input_packet["input_items"][0]
            self.assertEqual(
                input_item["blocker_state"]["reason_code"],
                "missing_exact_feedback_result_link",
            )
            self.assertEqual(
                input_item["feedback_inputs"][0]["source_message"]["content_preview"],
                "manual feedback points to an unlinked assistant row",
            )
            self.assertEqual(input_item["rerun_inputs"][0]["run_id"], "ocr-new")
            self.assertEqual(
                input_item["rerun_inputs"][0]["result_message"]["content_preview"],
                "second OCR text for ambiguity review",
            )
            self.assertFalse(
                input_item["rerun_inputs"][0]["exact_feedback_result_link"]
            )
            self.assertIn(
                "manual eval OCR retry input packet: state=ok rows=1/1 items=1 "
                "blocked=1 feedback_inputs=1/1 rerun_inputs=2 resolved=0/2 "
                "source_message_ids=2 result_message_ids=2 exact_links=0",
                input_packet_summary,
            )
            self.assertIn(
                "blocker=blocked reason=missing_exact_feedback_result_link",
                input_packet_summary,
            )
            self.assertIn(
                "ocr=ocr-new source_image=second.png image_status=missing",
                input_packet_summary,
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
