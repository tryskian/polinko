import json
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
    OVERLAY_OCR_COMPARISON_READINESS_SCHEMA_VERSION,
    OVERLAY_SOURCE_CONTEXT_INDEX_SCHEMA_VERSION,
    OCR_RETRY_RERUN_MANIFEST_SCHEMA_VERSION,
    OCR_RETRY_RERUN_PLAN_SCHEMA_VERSION,
    OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION,
    OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION,
    OCR_RETRY_EXECUTION_READINESS_SCHEMA_VERSION,
    OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION,
    OCR_RETRY_SELECTION_TEMPLATE_SCHEMA_VERSION,
    OCR_RETRY_SELECTION_REVIEW_SCHEMA_VERSION,
    OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION,
    OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION,
    build_manual_evals_health_report,
    build_ocr_retry_candidates_report,
    build_ocr_retry_input_packet_report,
    build_overlay_ocr_comparison_readiness_report,
    build_ocr_retry_rerun_manifest_report,
    build_ocr_retry_rerun_plan_report,
    build_ocr_retry_selection_apply_preview_report,
    build_ocr_retry_selection_decision_draft_payload,
    build_ocr_retry_execution_readiness_report,
    build_ocr_retry_selection_validation_report,
    build_ocr_retry_selection_template_report,
    build_ocr_retry_selection_review_report,
    build_ocr_retry_source_provenance_report,
    build_ocr_retry_source_verification_report,
    build_open_feedback_actionables_report,
    build_open_feedback_cohorts_report,
    format_manual_evals_health_report,
    format_ocr_retry_candidates_report,
    format_ocr_retry_input_packet_report,
    format_overlay_ocr_comparison_readiness_report,
    format_ocr_retry_rerun_manifest_report,
    format_ocr_retry_rerun_plan_report,
    format_ocr_retry_selection_apply_preview_report,
    format_ocr_retry_selection_decision_draft_report,
    format_ocr_retry_execution_readiness_report,
    format_ocr_retry_selection_validation_report,
    format_ocr_retry_selection_template_report,
    format_ocr_retry_selection_review_report,
    format_ocr_retry_source_provenance_report,
    format_ocr_retry_source_verification_report,
    format_open_feedback_actionables_report,
    format_open_feedback_cohorts_report,
    write_ocr_retry_selection_decision_draft,
)
from tests.test_build_manual_evals_db import _PNG_1X1, _init_history_db


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
                        tags_json = ?,
                        recommended_action = 'Retry OCR with a tighter crop and attach fresh image evidence for comparison.'
                    """,
                    (
                        json.dumps(
                            {
                                "positive": [],
                                "negative": ["ocr_miss", "grounding_gap"],
                                "all": ["ocr_miss", "grounding_gap"],
                            }
                        ),
                    ),
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
            rerun_manifest = build_ocr_retry_rerun_manifest_report(
                db_path=output_db,
                outcome="fail",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            rerun_manifest_summary = format_ocr_retry_rerun_manifest_report(
                rerun_manifest
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
            self.assertEqual(actionable["tags"], ["ocr_miss", "grounding_gap"])
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
            self.assertIn("tags=ocr_miss, grounding_gap", actionables_summary)
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
            self.assertEqual(
                rerun_manifest["schema_version"],
                OCR_RETRY_RERUN_MANIFEST_SCHEMA_VERSION,
            )
            self.assertEqual(
                rerun_manifest["input_packet_schema_version"],
                OCR_RETRY_INPUT_PACKET_SCHEMA_VERSION,
            )
            self.assertEqual(
                rerun_manifest["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "manifest_items": 1,
                    "selection_ready_items": 0,
                    "feedback_closure_blocked_items": 0,
                    "feedback_inputs": 1,
                    "source_artifacts": 1,
                    "resolved_source_artifacts": 0,
                    "unresolved_source_artifacts": 1,
                    "artifacts_with_thumbnail": 0,
                    "ocr_source_message_ids_present": 1,
                    "ocr_result_message_ids_present": 1,
                    "exact_feedback_result_links": 1,
                    "limit_applied": False,
                },
            )
            manifest_item = rerun_manifest["manifest_items"][0]
            self.assertEqual(
                manifest_item["selection_gate"]["reason_code"],
                "no_resolved_source_artifacts",
            )
            self.assertEqual(
                manifest_item["feedback_closure_state"]["state"],
                "ready",
            )
            self.assertEqual(
                manifest_item["source_artifacts"][0]["run_id"],
                "ocr-1",
            )
            self.assertEqual(
                manifest_item["feedback_source_previews"][0]["source_preview"],
                "hello world response that received manual feedback",
            )
            self.assertIn(
                "manual eval OCR retry rerun manifest: state=ok rows=1/1 "
                "items=1 selection_ready=0 closure_blocked=0 feedback_inputs=1 "
                "source_artifacts=1 resolved=0/1 thumbnails=0 "
                "source_message_ids=1 result_message_ids=1 exact_links=1",
                rerun_manifest_summary,
            )
            self.assertIn(
                "selection=blocked reason=no_resolved_source_artifacts",
                rerun_manifest_summary,
            )
            self.assertIn(
                "closure=ready next=review_exact_link_before_feedback_closure",
                rerun_manifest_summary,
            )
            self.assertIn(
                "feedback=1 message=m-result-1 source_state=found role=assistant",
                rerun_manifest_summary,
            )
            self.assertIn(
                "ocr=ocr-1 source_image=guardrail-note.txt image_status=missing",
                rerun_manifest_summary,
            )

            with closing(sqlite3.connect(output_db)) as conn:
                self.assertEqual(
                    conn.execute("PRAGMA integrity_check").fetchone()[0], "ok"
                )

    def test_overlay_comparison_readiness_blocks_without_source_image_context(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            history_db = tmp / "history.db"
            output_db = tmp / "manual_evals.db"
            _init_history_db(
                history_db,
                feedback_outcome="fail",
                source_name="overlay-source.png",
            )
            with closing(sqlite3.connect(history_db)) as conn:
                conn.execute("DELETE FROM ocr_runs")
                conn.execute(
                    """
                    UPDATE message_feedback
                    SET status = 'open',
                        tags_json = ?,
                        recommended_action = ?
                    """,
                    (
                        json.dumps(
                            {
                                "positive": [],
                                "negative": ["ocr_miss", "grounding_gap"],
                                "all": ["ocr_miss", "grounding_gap"],
                            }
                        ),
                        (
                            "Preserve as overlay-assisted OCR hypothesis evidence; "
                            "attach the overlay/source image context before rerunning "
                            "OCR for comparison."
                        ),
                    ),
                )
                conn.execute(
                    """
                    INSERT INTO chat_messages (
                      session_id, role, content, created_at, message_id,
                      parent_message_id
                    ) VALUES (
                      'chat-1', 'user', 'What does the overlay show?', 120,
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
                      'No new image evidence in this turn. Attach a new image.',
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

            readiness = build_overlay_ocr_comparison_readiness_report(
                db_path=output_db,
                outcome="fail",
                cohort="ocr_overlay_hypothesis",
                limit=5,
            )
            summary = format_overlay_ocr_comparison_readiness_report(readiness)

            self.assertEqual(
                readiness["schema_version"],
                OVERLAY_OCR_COMPARISON_READINESS_SCHEMA_VERSION,
            )
            self.assertEqual(readiness["state"], "blocked")
            self.assertEqual(
                readiness["filters"]["packet_basis"],
                "source_context_and_overlay_source_image_readiness",
            )
            self.assertEqual(
                readiness["counts"],
                {
                    "total_rows": 1,
                    "returned_rows": 1,
                    "limit_applied": False,
                    "source_messages_found": 1,
                    "source_images": 0,
                    "ocr_source_images": 0,
                    "indexed_source_images": 0,
                    "source_index_entries": 0,
                    "ready_items": 0,
                    "blocked_items": 1,
                    "payload_previews": 1,
                    "blockers": 1,
                },
            )
            self.assertEqual(
                readiness["mutation_boundary"]["manual_evals_db"],
                "read_only",
            )
            self.assertEqual(
                readiness["mutation_boundary"]["ocr_execution"],
                "none",
            )
            item = readiness["items"][0]
            self.assertEqual(item["state"], "blocked")
            self.assertEqual(item["source_context"]["state"], "found")
            self.assertEqual(item["source_images"], [])
            self.assertEqual(
                item["blockers"][0]["code"],
                "missing_overlay_source_image_context",
            )
            self.assertEqual(item["payload_preview"]["execution"], "none")
            self.assertEqual(item["payload_preview"]["mutation"], "none")
            self.assertIn(
                "manual eval overlay/OCR comparison readiness: "
                "state=blocked rows=1/1 ready=0 blocked=1 source_images=0",
                summary,
            )
            self.assertIn("source_index=missing index_entries=0", summary)
            self.assertIn(
                "payload_preview=manual_eval_overlay_ocr_comparison_preview "
                "execution=none mutation=none",
                summary,
            )
            self.assertIn(
                "code=missing_overlay_source_image_context",
                summary,
            )
            self.assertEqual(history_db.stat().st_mtime_ns, before_history)
            self.assertEqual(output_db.stat().st_mtime_ns, before_output)

    def test_overlay_comparison_readiness_uses_local_source_index(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            history_db = tmp / "history.db"
            output_db = tmp / "manual_evals.db"
            index_path = tmp / "overlay_source_context_index.json"
            overlay_image = tmp / "overlay-source.png"
            overlay_image.write_bytes(_PNG_1X1)
            _init_history_db(
                history_db,
                feedback_outcome="fail",
                source_name="overlay-source.png",
            )
            with closing(sqlite3.connect(history_db)) as conn:
                conn.execute("DELETE FROM ocr_runs")
                conn.execute(
                    """
                    UPDATE message_feedback
                    SET status = 'open',
                        tags_json = ?,
                        recommended_action = ?
                    """,
                    (
                        json.dumps(
                            {
                                "positive": [],
                                "negative": ["ocr_miss", "grounding_gap"],
                                "all": ["ocr_miss", "grounding_gap"],
                            }
                        ),
                        (
                            "Preserve as overlay-assisted OCR hypothesis evidence; "
                            "attach the overlay/source image context before rerunning "
                            "OCR for comparison."
                        ),
                    ),
                )
                conn.execute(
                    """
                    INSERT INTO chat_messages (
                      session_id, role, content, created_at, message_id,
                      parent_message_id
                    ) VALUES (
                      'chat-1', 'user', 'What does the overlay show?', 120,
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
                      'No new image evidence in this turn. Attach a new image.',
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
            initial = build_overlay_ocr_comparison_readiness_report(
                db_path=output_db,
                outcome="fail",
                cohort="ocr_overlay_hypothesis",
                limit=5,
            )
            initial_item = initial["items"][0]
            index_path.write_text(
                json.dumps(
                    {
                        "schema_version": OVERLAY_SOURCE_CONTEXT_INDEX_SCHEMA_VERSION,
                        "entries": [
                            {
                                "feedback_id": initial_item["feedback_id"],
                                "source_session_id": initial_item["source_session_id"],
                                "session_id": initial_item["session_id"],
                                "message_id": initial_item["message_id"],
                                "source_context_fingerprint": initial_item[
                                    "source_context"
                                ]["fingerprint"],
                                "source_images": [
                                    {
                                        "role": "overlay_source",
                                        "source_image_name": "overlay-source.png",
                                        "resolved_path": str(overlay_image),
                                        "notes": "human-reviewed overlay source",
                                    }
                                ],
                            }
                        ],
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            before_history = history_db.stat().st_mtime_ns
            before_output = output_db.stat().st_mtime_ns
            before_index = index_path.stat().st_mtime_ns

            readiness = build_overlay_ocr_comparison_readiness_report(
                db_path=output_db,
                outcome="fail",
                cohort="ocr_overlay_hypothesis",
                limit=5,
                overlay_source_index_path=index_path,
            )
            summary = format_overlay_ocr_comparison_readiness_report(readiness)

            self.assertEqual(readiness["state"], "ready")
            self.assertEqual(readiness["source_index"]["state"], "loaded")
            self.assertEqual(readiness["source_index"]["entries"], 1)
            self.assertEqual(
                readiness["counts"],
                {
                    "total_rows": 1,
                    "returned_rows": 1,
                    "limit_applied": False,
                    "source_messages_found": 1,
                    "source_images": 1,
                    "ocr_source_images": 0,
                    "indexed_source_images": 1,
                    "source_index_entries": 1,
                    "ready_items": 1,
                    "blocked_items": 0,
                    "payload_previews": 1,
                    "blockers": 0,
                },
            )
            item = readiness["items"][0]
            self.assertEqual(item["state"], "ready")
            self.assertEqual(item["blockers"], [])
            source_image = item["source_images"][0]
            self.assertEqual(source_image["context_source"], "overlay_source_index")
            self.assertEqual(source_image["source_name"], "overlay-source.png")
            self.assertEqual(source_image["image_asset"]["status"], "resolved")
            self.assertEqual(
                source_image["source_index"]["notes"],
                "human-reviewed overlay source",
            )
            self.assertIn("source_index=loaded index_entries=1", summary)
            self.assertIn(
                "origin=overlay_source_index source=overlay-source.png "
                "image_status=resolved",
                summary,
            )
            self.assertEqual(history_db.stat().st_mtime_ns, before_history)
            self.assertEqual(output_db.stat().st_mtime_ns, before_output)
            self.assertEqual(index_path.stat().st_mtime_ns, before_index)

    def test_overlay_comparison_readiness_blocks_stale_source_index(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            history_db = tmp / "history.db"
            output_db = tmp / "manual_evals.db"
            index_path = tmp / "overlay_source_context_index.json"
            overlay_image = tmp / "overlay-source.png"
            overlay_image.write_bytes(_PNG_1X1)
            _init_history_db(history_db, feedback_outcome="fail")
            with closing(sqlite3.connect(history_db)) as conn:
                conn.execute("DELETE FROM ocr_runs")
                conn.execute(
                    """
                    UPDATE message_feedback
                    SET status = 'open',
                        recommended_action = ?
                    """,
                    (
                        "Preserve as overlay-assisted OCR hypothesis evidence; "
                        "attach the overlay/source image context before rerunning "
                        "OCR for comparison.",
                    ),
                )
                conn.execute(
                    """
                    INSERT INTO chat_messages (
                      session_id, role, content, created_at, message_id,
                      parent_message_id
                    ) VALUES (
                      'chat-1', 'assistant',
                      'No new image evidence in this turn. Attach a new image.',
                      155, 'm-result-1', NULL
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
            initial = build_overlay_ocr_comparison_readiness_report(
                db_path=output_db,
                outcome="fail",
                cohort="ocr_overlay_hypothesis",
                limit=5,
            )
            initial_item = initial["items"][0]
            index_path.write_text(
                json.dumps(
                    {
                        "schema_version": OVERLAY_SOURCE_CONTEXT_INDEX_SCHEMA_VERSION,
                        "entries": [
                            {
                                "feedback_id": initial_item["feedback_id"],
                                "source_session_id": initial_item["source_session_id"],
                                "message_id": initial_item["message_id"],
                                "source_context_fingerprint": "stale",
                                "source_images": [
                                    {
                                        "source_image_name": "overlay-source.png",
                                        "resolved_path": str(overlay_image),
                                    }
                                ],
                            }
                        ],
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            readiness = build_overlay_ocr_comparison_readiness_report(
                db_path=output_db,
                outcome="fail",
                cohort="ocr_overlay_hypothesis",
                limit=5,
                overlay_source_index_path=index_path,
            )
            summary = format_overlay_ocr_comparison_readiness_report(readiness)

            self.assertEqual(readiness["state"], "blocked")
            self.assertEqual(readiness["counts"]["source_images"], 0)
            self.assertEqual(readiness["counts"]["source_index_entries"], 1)
            item = readiness["items"][0]
            blocker_codes = [blocker["code"] for blocker in item["blockers"]]
            self.assertIn("overlay_source_index_fingerprint_mismatch", blocker_codes)
            self.assertIn("missing_overlay_source_image_context", blocker_codes)
            self.assertIn("source_index=loaded index_entries=1", summary)
            self.assertIn("code=overlay_source_index_fingerprint_mismatch", summary)

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
            rerun_manifest = build_ocr_retry_rerun_manifest_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            rerun_manifest_summary = format_ocr_retry_rerun_manifest_report(
                rerun_manifest
            )

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
            self.assertEqual(
                rerun_manifest["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "manifest_items": 1,
                    "selection_ready_items": 0,
                    "feedback_closure_blocked_items": 1,
                    "feedback_inputs": 1,
                    "source_artifacts": 2,
                    "resolved_source_artifacts": 0,
                    "unresolved_source_artifacts": 2,
                    "artifacts_with_thumbnail": 0,
                    "ocr_source_message_ids_present": 2,
                    "ocr_result_message_ids_present": 2,
                    "exact_feedback_result_links": 0,
                    "limit_applied": False,
                },
            )
            manifest_item = rerun_manifest["manifest_items"][0]
            self.assertEqual(
                manifest_item["selection_gate"]["reason_code"],
                "no_resolved_source_artifacts",
            )
            self.assertEqual(
                manifest_item["feedback_closure_state"]["reason_code"],
                "missing_exact_feedback_result_link",
            )
            self.assertEqual(
                manifest_item["source_artifacts"][0]["run_id"],
                "ocr-new",
            )
            self.assertEqual(
                manifest_item["feedback_source_previews"][0]["source_preview"],
                "manual feedback points to an unlinked assistant row",
            )
            self.assertIn(
                "manual eval OCR retry rerun manifest: state=ok rows=1/1 "
                "items=1 selection_ready=0 closure_blocked=1 feedback_inputs=1 "
                "source_artifacts=2 resolved=0/2 thumbnails=0 "
                "source_message_ids=2 result_message_ids=2 exact_links=0",
                rerun_manifest_summary,
            )
            self.assertIn(
                "selection=blocked reason=no_resolved_source_artifacts",
                rerun_manifest_summary,
            )
            self.assertIn(
                "closure=blocked reason=missing_exact_feedback_result_link",
                rerun_manifest_summary,
            )
            self.assertIn(
                "ocr=ocr-new source_image=second.png image_status=missing",
                rerun_manifest_summary,
            )

    def test_ocr_retry_rerun_manifest_selects_resolved_source_artifacts(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            history_db = tmp / "history.db"
            output_db = tmp / "manual_evals.db"
            image_dir = tmp / "images"
            image_dir.mkdir(parents=True, exist_ok=True)
            (image_dir / "image1.png").write_bytes(_PNG_1X1)
            _init_history_db(
                history_db,
                feedback_outcome="partial",
                source_name="file-abc123-image1.png",
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
                    UPDATE ocr_runs
                    SET source_message_id = NULL,
                        result_message_id = NULL
                    """
                )
                conn.execute(
                    """
                    INSERT INTO chat_messages (
                      session_id, role, content, created_at, message_id,
                      parent_message_id
                    ) VALUES (
                      'chat-1', 'assistant',
                      'feedback source row for resolved source artifact',
                      155, 'm-result-1', NULL
                    )
                    """
                )
                conn.commit()
            build_manual_evals_db(
                history_db=history_db,
                output_db=output_db,
                image_roots=[image_dir],
                include_thumbnails=False,
            )

            rerun_manifest = build_ocr_retry_rerun_manifest_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            rerun_manifest_summary = format_ocr_retry_rerun_manifest_report(
                rerun_manifest
            )
            rerun_plan = build_ocr_retry_rerun_plan_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            rerun_plan_summary = format_ocr_retry_rerun_plan_report(rerun_plan)
            artifact_id = rerun_plan["plan_items"][0]["plan_artifacts"][0][
                "artifact_id"
            ]
            filtered_rerun_plan = build_ocr_retry_rerun_plan_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
                artifact_ids=[artifact_id],
            )
            unmatched_rerun_plan = build_ocr_retry_rerun_plan_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
                artifact_ids=["missing-artifact"],
            )

            self.assertEqual(
                rerun_manifest["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "manifest_items": 1,
                    "selection_ready_items": 1,
                    "feedback_closure_blocked_items": 1,
                    "feedback_inputs": 1,
                    "source_artifacts": 1,
                    "resolved_source_artifacts": 1,
                    "unresolved_source_artifacts": 0,
                    "artifacts_with_thumbnail": 0,
                    "ocr_source_message_ids_present": 0,
                    "ocr_result_message_ids_present": 0,
                    "exact_feedback_result_links": 0,
                    "limit_applied": False,
                },
            )
            manifest_item = rerun_manifest["manifest_items"][0]
            self.assertEqual(
                manifest_item["selection_gate"]["state"],
                "ready_for_selection",
            )
            self.assertEqual(
                manifest_item["selection_gate"]["reason_code"],
                "missing_ocr_source_result_message_ids",
            )
            self.assertEqual(
                manifest_item["feedback_closure_state"]["state"],
                "blocked",
            )
            source_artifact = manifest_item["source_artifacts"][0]
            self.assertTrue(source_artifact["image"]["resolved"])
            self.assertEqual(source_artifact["image"]["status"], "resolved")
            self.assertEqual(
                source_artifact["image"]["source_filename"],
                "file-abc123-image1.png",
            )
            self.assertEqual(
                Path(source_artifact["image"]["resolved_path"]).name,
                "image1.png",
            )
            self.assertEqual(
                source_artifact["image"]["source_size_bytes"],
                len(_PNG_1X1),
            )
            self.assertEqual(
                manifest_item["feedback_source_previews"][0]["source_preview"],
                "feedback source row for resolved source artifact",
            )
            self.assertIn(
                "manual eval OCR retry rerun manifest: state=ok rows=1/1 "
                "items=1 selection_ready=1 closure_blocked=1 feedback_inputs=1 "
                "source_artifacts=1 resolved=1/1 thumbnails=0 "
                "source_message_ids=0 result_message_ids=0 exact_links=0",
                rerun_manifest_summary,
            )
            self.assertIn(
                "selection=ready_for_selection "
                "reason=missing_ocr_source_result_message_ids",
                rerun_manifest_summary,
            )
            self.assertIn(
                "closure=blocked reason=missing_ocr_source_result_message_ids",
                rerun_manifest_summary,
            )
            self.assertIn(
                "ocr=ocr-1 source_image=file-abc123-image1.png "
                "image_status=resolved resolved=yes",
                rerun_manifest_summary,
            )
            self.assertEqual(
                rerun_plan["schema_version"],
                OCR_RETRY_RERUN_PLAN_SCHEMA_VERSION,
            )
            self.assertEqual(
                rerun_plan["manifest_schema_version"],
                OCR_RETRY_RERUN_MANIFEST_SCHEMA_VERSION,
            )
            self.assertEqual(
                rerun_plan["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "manifest_items": 1,
                    "plan_items": 1,
                    "source_artifacts": 1,
                    "resolved_source_artifacts": 1,
                    "planned_source_artifacts": 1,
                    "feedback_closure_blocked_items": 1,
                    "ocr_source_message_ids_present": 0,
                    "ocr_result_message_ids_present": 0,
                    "exact_feedback_result_links": 0,
                    "requested_artifact_ids": 0,
                    "unmatched_artifact_ids": 0,
                    "preview_only": True,
                    "limit_applied": False,
                },
            )
            self.assertEqual(
                rerun_plan["filters"]["selection_mode"],
                "all_ready_resolved_source_artifacts",
            )
            self.assertEqual(artifact_id, "chat-1::ocr-1::ocr-1")
            plan_item = rerun_plan["plan_items"][0]
            plan_artifact = plan_item["plan_artifacts"][0]
            self.assertEqual(
                plan_artifact["action"],
                "rerun_or_curate_source_artifact",
            )
            self.assertTrue(plan_artifact["preview_only"])
            self.assertEqual(plan_artifact["feedback_ids"], [1])
            self.assertEqual(plan_artifact["source_session_id"], "chat-1")
            self.assertEqual(plan_artifact["session_id"], "chat-1")
            self.assertEqual(plan_artifact["ocr_run_id"], "ocr-1")
            self.assertEqual(
                plan_artifact["source_image_name"],
                "file-abc123-image1.png",
            )
            self.assertEqual(
                Path(plan_artifact["payload_inputs"]["resolved_path"]).name,
                "image1.png",
            )
            self.assertEqual(
                plan_artifact["command_preview"],
                {
                    "mode": "payload_only",
                    "label": "manual_eval_ocr_retry_rerun_preview",
                    "payload_schema": "source_artifact_selection",
                },
            )
            self.assertEqual(
                plan_artifact["feedback_source_preview"]["source_preview"],
                "feedback source row for resolved source artifact",
            )
            self.assertEqual(
                filtered_rerun_plan["counts"]["planned_source_artifacts"],
                1,
            )
            self.assertEqual(
                filtered_rerun_plan["filters"]["selection_mode"],
                "requested_artifact_ids",
            )
            self.assertEqual(
                filtered_rerun_plan["filters"]["artifact_ids"],
                [artifact_id],
            )
            self.assertEqual(
                unmatched_rerun_plan["counts"]["planned_source_artifacts"],
                0,
            )
            self.assertEqual(
                unmatched_rerun_plan["counts"]["unmatched_artifact_ids"],
                1,
            )
            self.assertEqual(
                unmatched_rerun_plan["unmatched_artifact_ids"],
                ["missing-artifact"],
            )
            self.assertIn(
                "manual eval OCR retry rerun plan: state=ok rows=1/1 "
                "items=1 planned_artifacts=1 resolved=1/1 closure_blocked=1 "
                "source_message_ids=0 result_message_ids=0 exact_links=0 "
                "selection=all_ready_resolved_source_artifacts "
                "requested_artifacts=0 unmatched=0 preview_only=yes",
                rerun_plan_summary,
            )
            self.assertIn(
                "artifact=chat-1::ocr-1::ocr-1 "
                "action=rerun_or_curate_source_artifact preview_only=yes "
                "feedback=1 ocr=ocr-1 source_image=file-abc123-image1.png",
                rerun_plan_summary,
            )
            self.assertIn(
                "source_preview=feedback=1 message=m-result-1 source_state=found",
                rerun_plan_summary,
            )
            self.assertIn(
                "payload=artifact_id=chat-1::ocr-1::ocr-1 "
                "operation=ocr_retry_rerun_or_case_curation",
                rerun_plan_summary,
            )

    def test_ocr_retry_selection_review_collapses_duplicate_source_artifacts(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            history_db = tmp / "history.db"
            output_db = tmp / "manual_evals.db"
            image_dir = tmp / "images"
            image_dir.mkdir(parents=True, exist_ok=True)
            (image_dir / "image1.png").write_bytes(_PNG_1X1)
            _init_history_db(history_db, feedback_outcome="partial")
            with closing(sqlite3.connect(history_db)) as conn:
                conn.execute(
                    """
                    UPDATE message_feedback
                    SET status = 'open',
                        recommended_action = 'Retry OCR with a tighter crop and attach fresh image evidence.',
                        action_taken = NULL
                    """
                )
                conn.execute(
                    """
                    UPDATE ocr_runs
                    SET source_message_id = NULL,
                        result_message_id = NULL
                    """
                )
                conn.execute(
                    """
                    INSERT INTO ocr_runs (
                      run_id, session_id, source_name, mime_type,
                      source_message_id, result_message_id, status,
                      extracted_text, created_at
                    ) VALUES (
                      'ocr-new', 'chat-1', 'file-abc123-image1.png', 'image/png',
                      NULL, NULL, 'ok', 'newer OCR text', 190
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
                      'feedback source row for duplicate source artifact',
                      155, 'm-result-1', NULL
                    )
                    """
                )
                conn.commit()
            build_manual_evals_db(
                history_db=history_db,
                output_db=output_db,
                image_roots=[image_dir],
                include_thumbnails=False,
            )

            selection_review = build_ocr_retry_selection_review_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            summary = format_ocr_retry_selection_review_report(selection_review)

            self.assertEqual(
                selection_review["schema_version"],
                OCR_RETRY_SELECTION_REVIEW_SCHEMA_VERSION,
            )
            self.assertEqual(
                selection_review["rerun_plan_schema_version"],
                OCR_RETRY_RERUN_PLAN_SCHEMA_VERSION,
            )
            self.assertEqual(
                selection_review["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "plan_items": 1,
                    "planned_source_artifacts": 2,
                    "shortlist_items": 1,
                    "collapsed_duplicate_source_artifacts": 1,
                    "candidate_ocr_runs": 2,
                    "decision_pending_items": 1,
                    "feedback_closure_blocked_items": 1,
                    "ocr_source_message_ids_present": 0,
                    "ocr_result_message_ids_present": 0,
                    "exact_feedback_result_links": 0,
                    "requested_artifact_ids": 0,
                    "unmatched_artifact_ids": 0,
                    "preview_only": True,
                    "limit_applied": False,
                },
            )
            item = selection_review["selection_review_items"][0]
            self.assertEqual(item["feedback_ids"], [1])
            self.assertEqual(
                item["selection_decision"]["state"], "needs_human_selection"
            )
            self.assertEqual(
                item["selection_decision"]["allowed_actions"],
                ["rerun_input", "curated_case", "context_only"],
            )
            self.assertEqual(
                item["selection_decision"]["reason_code"],
                "duplicate_source_artifacts_collapsed",
            )
            self.assertEqual(item["feedback_closure_state"]["state"], "blocked")
            self.assertEqual(item["source_image_name"], "file-abc123-image1.png")
            self.assertEqual(Path(item["resolved_path"]).name, "image1.png")
            self.assertEqual(item["counts"]["candidate_ocr_runs"], 2)
            self.assertEqual(item["counts"]["duplicate_source_artifacts"], 1)
            candidate_ids = {
                candidate["ocr_run_id"] for candidate in item["candidate_ocr_runs"]
            }
            self.assertEqual(candidate_ids, {"ocr-1", "ocr-new"})
            artifact_ids = {
                candidate["artifact_id"] for candidate in item["candidate_ocr_runs"]
            }
            self.assertEqual(
                artifact_ids,
                {"chat-1::ocr-new::ocr-1", "chat-1::ocr-new::ocr-new"},
            )

            self.assertIn(
                "manual eval OCR retry selection review: state=ok rows=1/1 "
                "items=1 planned_artifacts=2 collapsed_duplicates=1 "
                "candidate_runs=2 decision_pending=1 closure_blocked=1",
                summary,
            )
            self.assertIn(
                "decision=needs_human_selection "
                "actions=rerun_input,curated_case,context_only",
                summary,
            )
            self.assertIn("candidate_runs=2 duplicate_artifacts=1", summary)
            self.assertIn("ocr=ocr-1", summary)
            self.assertIn("ocr=ocr-new", summary)

            selection_template = build_ocr_retry_selection_template_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            template_summary = format_ocr_retry_selection_template_report(
                selection_template
            )

            self.assertEqual(
                selection_template["schema_version"],
                OCR_RETRY_SELECTION_TEMPLATE_SCHEMA_VERSION,
            )
            self.assertEqual(
                selection_template["selection_review_schema_version"],
                OCR_RETRY_SELECTION_REVIEW_SCHEMA_VERSION,
            )
            self.assertEqual(
                selection_template["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "shortlist_items": 1,
                    "template_items": 1,
                    "candidate_artifacts": 2,
                    "collapsed_duplicate_source_artifacts": 1,
                    "default_undecided_items": 1,
                    "feedback_closure_blocked_items": 1,
                    "ocr_source_message_ids_present": 0,
                    "ocr_result_message_ids_present": 0,
                    "exact_feedback_result_links": 0,
                    "requested_artifact_ids": 0,
                    "unmatched_artifact_ids": 0,
                    "preview_only": True,
                    "limit_applied": False,
                },
            )
            template = selection_template["selection_template"]
            self.assertEqual(template["mutation"], "none")
            self.assertEqual(
                template["allowed_actions"],
                ["rerun_input", "curated_case", "context_only"],
            )
            template_item = template["items"][0]
            self.assertEqual(template_item["feedback_ids"], [1])
            self.assertEqual(
                template_item["decision_input"],
                {
                    "selected_action": "undecided",
                    "allowed_actions": [
                        "rerun_input",
                        "curated_case",
                        "context_only",
                    ],
                    "selected_artifact_ids": [],
                    "rationale": "",
                    "notes": "",
                    "requires_human_selection": True,
                },
            )
            self.assertEqual(
                {
                    candidate["artifact_id"]
                    for candidate in template_item["candidate_artifacts"]
                },
                artifact_ids,
            )
            self.assertIn(
                "manual eval OCR retry selection template: state=ok rows=1/1 "
                "items=1 shortlist=1 candidate_artifacts=2 "
                "collapsed_duplicates=1 undecided=1 closure_blocked=1",
                template_summary,
            )
            self.assertIn(
                "selected_action=undecided "
                "allowed=rerun_input,curated_case,context_only",
                template_summary,
            )
            self.assertIn(
                "fill_template=selected_action=<rerun_input|curated_case|context_only>",
                template_summary,
            )

            decision_draft = build_ocr_retry_selection_decision_draft_payload(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            self.assertEqual(
                decision_draft["schema_version"],
                OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION,
            )
            self.assertEqual(
                decision_draft["selection_template_schema_version"],
                OCR_RETRY_SELECTION_TEMPLATE_SCHEMA_VERSION,
            )
            self.assertEqual(decision_draft["draft_contract"]["mutation"], "none")
            self.assertTrue(decision_draft["draft_contract"]["local_only"])
            self.assertTrue(decision_draft["draft_contract"]["requires_validation"])
            self.assertEqual(decision_draft["counts"]["draft_items"], 1)
            self.assertEqual(decision_draft["counts"]["candidate_artifacts"], 2)
            self.assertEqual(len(decision_draft["template_fingerprint"]), 64)
            draft_template = decision_draft["selection_template"]
            self.assertEqual(
                draft_template["template_fingerprint"],
                decision_draft["template_fingerprint"],
            )
            draft_item = draft_template["items"][0]
            self.assertEqual(len(draft_item["template_item_fingerprint"]), 64)
            self.assertEqual(
                draft_item["decision_input"]["selected_action"],
                "undecided",
            )
            draft_path = tmp / "manual_eval_decisions" / "ocr_retry_selection.json"
            write_report = write_ocr_retry_selection_decision_draft(
                db_path=output_db,
                output_path=draft_path,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            draft_write_summary = format_ocr_retry_selection_decision_draft_report(
                write_report
            )
            self.assertEqual(write_report["state"], "written")
            self.assertEqual(
                write_report["schema_version"],
                OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION,
            )
            self.assertFalse(write_report["output"]["overwritten"])
            self.assertEqual(write_report["output"]["path"], str(draft_path))
            self.assertTrue(draft_path.exists())
            self.assertIn(
                "manual eval OCR retry selection decision draft: state=written "
                "rows=1/1 items=1 shortlist=1 candidate_artifacts=2",
                draft_write_summary,
            )
            self.assertIn(f"output={draft_path}", draft_write_summary)
            self.assertIn(
                "next_validate=make manual-evals-ocr-retry-selection-validate",
                draft_write_summary,
            )
            loaded_draft = json.loads(draft_path.read_text(encoding="utf-8"))
            self.assertEqual(
                loaded_draft["schema_version"],
                OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION,
            )
            self.assertEqual(
                loaded_draft["selection_template"]["items"][0]["shortlist_id"],
                template_item["shortlist_id"],
            )
            draft_validation = build_ocr_retry_selection_validation_report(
                db_path=output_db,
                selection_path=draft_path,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            self.assertEqual(draft_validation["state"], "attention")
            self.assertEqual(draft_validation["decision_source"]["state"], "loaded")
            self.assertEqual(
                draft_validation["decision_source"]["schema_version"],
                OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION,
            )
            self.assertEqual(draft_validation["counts"]["submitted_decisions"], 1)
            self.assertEqual(draft_validation["counts"]["pending_decisions"], 1)
            self.assertEqual(draft_validation["counts"]["missing_decisions"], 0)
            self.assertEqual(
                draft_validation["selection_validation_items"][0]["issues"],
                ["pending_selected_action"],
            )
            blocked_write = write_ocr_retry_selection_decision_draft(
                db_path=output_db,
                output_path=draft_path,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            self.assertEqual(blocked_write["state"], "blocked")
            self.assertIn("already exists", blocked_write["warnings"][0])
            forced_write = write_ocr_retry_selection_decision_draft(
                db_path=output_db,
                output_path=draft_path,
                force=True,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            self.assertEqual(forced_write["state"], "written")
            self.assertTrue(forced_write["output"]["overwritten"])

            missing_validation = build_ocr_retry_selection_validation_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            missing_summary = format_ocr_retry_selection_validation_report(
                missing_validation
            )

            self.assertEqual(
                missing_validation["schema_version"],
                OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION,
            )
            self.assertEqual(
                missing_validation["selection_template_schema_version"],
                OCR_RETRY_SELECTION_TEMPLATE_SCHEMA_VERSION,
            )
            self.assertEqual(missing_validation["state"], "attention")
            self.assertEqual(missing_validation["decision_source"]["state"], "missing")
            self.assertEqual(
                missing_validation["counts"],
                {
                    "total_feedback_rows": 1,
                    "returned_feedback_rows": 1,
                    "shortlist_items": 1,
                    "candidate_artifacts": 2,
                    "submitted_decisions": 0,
                    "valid_decisions": 0,
                    "pending_decisions": 1,
                    "invalid_decisions": 0,
                    "missing_decisions": 1,
                    "stale_decisions": 0,
                    "duplicate_decisions": 0,
                    "selected_artifacts": 0,
                    "invalid_selected_artifacts": 0,
                    "feedback_closure_blocked_items": 1,
                    "ocr_source_message_ids_present": 0,
                    "ocr_result_message_ids_present": 0,
                    "exact_feedback_result_links": 0,
                    "requested_artifact_ids": 0,
                    "unmatched_artifact_ids": 0,
                    "preview_only": True,
                    "limit_applied": False,
                },
            )
            self.assertIn(
                "manual eval OCR retry selection validation: state=attention "
                "rows=1/1 items=1 candidate_artifacts=2 submitted=0 "
                "valid=0 pending=1 invalid=0 missing=1",
                missing_summary,
            )
            self.assertIn("issues=missing_decision", missing_summary)

            missing_apply_preview = build_ocr_retry_selection_apply_preview_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            missing_apply_summary = format_ocr_retry_selection_apply_preview_report(
                missing_apply_preview
            )

            self.assertEqual(
                missing_apply_preview["schema_version"],
                OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION,
            )
            self.assertEqual(
                missing_apply_preview["selection_validation_schema_version"],
                OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION,
            )
            self.assertEqual(missing_apply_preview["state"], "blocked")
            self.assertEqual(missing_apply_preview["validation_state"], "attention")
            self.assertEqual(missing_apply_preview["counts"]["preview_items"], 0)
            self.assertEqual(
                missing_apply_preview["counts"]["blocked_by_validation"],
                1,
            )
            self.assertEqual(
                missing_apply_preview["application_preview"]["items"],
                [],
            )
            self.assertIn(
                "manual eval OCR retry selection apply preview: state=blocked "
                "validation=attention rows=1/1 items=1",
                missing_apply_summary,
            )
            self.assertIn("validation_blockers:", missing_apply_summary)
            self.assertIn("application_preview_items: none", missing_apply_summary)

            selection_path = tmp / "ocr_retry_selection.json"
            selected_artifact_id = sorted(artifact_ids)[0]
            selection_path.write_text(
                json.dumps(
                    {
                        "schema_version": "polinko.manual_eval_ocr_retry_selection_decisions.v1",
                        "decisions": [
                            {
                                "shortlist_id": template_item["shortlist_id"],
                                "selected_action": "rerun_input",
                                "selected_artifact_ids": [selected_artifact_id],
                                "rationale": "Use the selected rerun source.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            valid_validation = build_ocr_retry_selection_validation_report(
                db_path=output_db,
                selection_path=selection_path,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            valid_summary = format_ocr_retry_selection_validation_report(
                valid_validation
            )

            self.assertEqual(valid_validation["state"], "ok")
            self.assertEqual(valid_validation["decision_source"]["state"], "loaded")
            self.assertEqual(valid_validation["counts"]["submitted_decisions"], 1)
            self.assertEqual(valid_validation["counts"]["valid_decisions"], 1)
            self.assertEqual(valid_validation["counts"]["invalid_decisions"], 0)
            self.assertEqual(valid_validation["counts"]["selected_artifacts"], 1)
            self.assertIn("state=valid action=rerun_input issues=none", valid_summary)
            self.assertIn(f"selected_artifacts={selected_artifact_id}", valid_summary)

            valid_apply_preview = build_ocr_retry_selection_apply_preview_report(
                db_path=output_db,
                selection_path=selection_path,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            valid_apply_summary = format_ocr_retry_selection_apply_preview_report(
                valid_apply_preview
            )

            self.assertEqual(valid_apply_preview["state"], "ok")
            self.assertEqual(valid_apply_preview["validation_state"], "ok")
            self.assertEqual(valid_apply_preview["counts"]["preview_items"], 1)
            self.assertEqual(valid_apply_preview["counts"]["rerun_input_items"], 1)
            self.assertEqual(valid_apply_preview["counts"]["curated_case_items"], 0)
            self.assertEqual(valid_apply_preview["counts"]["context_only_items"], 0)
            self.assertEqual(valid_apply_preview["counts"]["selected_artifacts"], 1)
            self.assertEqual(valid_apply_preview["counts"]["blocked_by_validation"], 0)
            apply_item = valid_apply_preview["application_preview"]["items"][0]
            self.assertEqual(apply_item["mutation"], "none")
            self.assertEqual(apply_item["execution"], "none")
            self.assertEqual(apply_item["selected_action"], "rerun_input")
            self.assertEqual(
                apply_item["selected_artifact_ids"], [selected_artifact_id]
            )
            self.assertEqual(
                apply_item["selected_artifacts"][0]["artifact_id"],
                selected_artifact_id,
            )
            self.assertEqual(
                valid_apply_preview["application_preview"]["actions"]["rerun_input"][0][
                    "shortlist_id"
                ],
                template_item["shortlist_id"],
            )
            self.assertIn(
                "manual eval OCR retry selection apply preview: state=ok "
                "validation=ok rows=1/1 items=1",
                valid_apply_summary,
            )
            self.assertIn("action=rerun_input", valid_apply_summary)
            self.assertIn(f"artifact={selected_artifact_id}", valid_apply_summary)

            execution_readiness = build_ocr_retry_execution_readiness_report(
                db_path=output_db,
                selection_path=selection_path,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            execution_readiness_summary = format_ocr_retry_execution_readiness_report(
                execution_readiness
            )

            self.assertEqual(
                execution_readiness["schema_version"],
                OCR_RETRY_EXECUTION_READINESS_SCHEMA_VERSION,
            )
            self.assertEqual(
                execution_readiness["selection_apply_preview_schema_version"],
                OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION,
            )
            self.assertEqual(execution_readiness["state"], "ready")
            self.assertEqual(execution_readiness["validation_state"], "ok")
            self.assertEqual(execution_readiness["apply_preview_state"], "ok")
            self.assertTrue(
                execution_readiness["readiness_contract"][
                    "requires_explicit_follow_up_gate"
                ]
            )
            self.assertEqual(
                execution_readiness["readiness_contract"]["mutation"], "none"
            )
            self.assertEqual(
                execution_readiness["readiness_contract"]["execution"], "none"
            )
            self.assertEqual(execution_readiness["counts"]["readiness_items"], 1)
            self.assertEqual(execution_readiness["counts"]["ready_items"], 1)
            self.assertEqual(execution_readiness["counts"]["blocked_items"], 0)
            self.assertEqual(execution_readiness["counts"]["executable_items"], 1)
            self.assertEqual(execution_readiness["counts"]["source_files_ready"], 1)
            self.assertEqual(execution_readiness["counts"]["source_files_missing"], 0)
            readiness_item = execution_readiness["execution_readiness_items"][0]
            self.assertEqual(readiness_item["state"], "ready")
            self.assertTrue(readiness_item["executable"])
            self.assertEqual(readiness_item["selected_action"], "rerun_input")
            self.assertEqual(
                readiness_item["execution_gate"],
                "explicit_follow_up_required",
            )
            self.assertEqual(readiness_item["mutation"], "none")
            self.assertEqual(readiness_item["execution"], "none")
            readiness_artifact = readiness_item["selected_artifacts"][0]
            self.assertEqual(readiness_artifact["state"], "ready")
            self.assertTrue(readiness_artifact["source_file_exists"])
            self.assertEqual(readiness_artifact["artifact_id"], selected_artifact_id)
            self.assertIn(
                "manual eval OCR retry execution readiness: state=ready "
                "validation=ok apply_preview=ok rows=1/1 items=1",
                execution_readiness_summary,
            )
            self.assertIn("executable=1 blocked=0", execution_readiness_summary)
            self.assertIn("readiness=ready executable=yes", execution_readiness_summary)
            self.assertIn(
                f"artifact={selected_artifact_id} state=ready",
                execution_readiness_summary,
            )

            selection_path.write_text(
                json.dumps(
                    {
                        "decisions": [
                            {
                                "shortlist_id": template_item["shortlist_id"],
                                "selected_action": "context_only",
                                "rationale": "Keep this source as context.",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            context_apply_preview = build_ocr_retry_selection_apply_preview_report(
                db_path=output_db,
                selection_path=selection_path,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )

            self.assertEqual(context_apply_preview["state"], "ok")
            self.assertEqual(context_apply_preview["counts"]["preview_items"], 1)
            self.assertEqual(context_apply_preview["counts"]["rerun_input_items"], 0)
            self.assertEqual(context_apply_preview["counts"]["context_only_items"], 1)
            self.assertEqual(context_apply_preview["counts"]["selected_artifacts"], 0)
            self.assertEqual(
                context_apply_preview["application_preview"]["actions"]["context_only"][
                    0
                ]["selected_artifacts"],
                [],
            )

            selection_path.write_text(
                json.dumps(
                    {
                        "decisions": [
                            {
                                "shortlist_id": template_item["shortlist_id"],
                                "selected_action": "retry",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            invalid_action_validation = build_ocr_retry_selection_validation_report(
                db_path=output_db,
                selection_path=selection_path,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            invalid_action_summary = format_ocr_retry_selection_validation_report(
                invalid_action_validation
            )

            self.assertEqual(invalid_action_validation["state"], "error")
            self.assertEqual(
                invalid_action_validation["counts"]["invalid_decisions"],
                1,
            )
            self.assertIn("issues=invalid_selected_action", invalid_action_summary)

            invalid_action_apply = build_ocr_retry_selection_apply_preview_report(
                db_path=output_db,
                selection_path=selection_path,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )

            self.assertEqual(invalid_action_apply["state"], "blocked")
            self.assertEqual(invalid_action_apply["validation_state"], "error")
            self.assertEqual(invalid_action_apply["counts"]["preview_items"], 0)
            self.assertEqual(
                invalid_action_apply["application_preview"]["items"],
                [],
            )

            invalid_action_readiness = build_ocr_retry_execution_readiness_report(
                db_path=output_db,
                selection_path=selection_path,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )

            self.assertEqual(invalid_action_readiness["state"], "blocked")
            self.assertEqual(invalid_action_readiness["validation_state"], "error")
            self.assertEqual(
                invalid_action_readiness["counts"]["blocked_by_validation"],
                1,
            )
            self.assertEqual(
                invalid_action_readiness["execution_readiness_items"],
                [],
            )

            selection_path.write_text(
                json.dumps(
                    {
                        "decisions": [
                            {
                                "shortlist_id": template_item["shortlist_id"],
                                "selected_action": "rerun_input",
                                "selected_artifact_ids": ["stale-artifact"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            invalid_validation = build_ocr_retry_selection_validation_report(
                db_path=output_db,
                selection_path=selection_path,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            invalid_summary = format_ocr_retry_selection_validation_report(
                invalid_validation
            )

            self.assertEqual(invalid_validation["state"], "error")
            self.assertEqual(invalid_validation["counts"]["invalid_decisions"], 1)
            self.assertEqual(
                invalid_validation["counts"]["invalid_selected_artifacts"],
                1,
            )
            self.assertIn(
                "issues=selected_artifact_not_in_shortlist",
                invalid_summary,
            )
            self.assertIn("invalid_artifacts=stale-artifact", invalid_summary)

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
