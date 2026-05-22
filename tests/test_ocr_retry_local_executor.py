import json
import os
import sqlite3
import unittest
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.build_manual_evals_db import build_manual_evals_db
from tools.manual_evals_db_health import (
    OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
    OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION,
    OCR_RETRY_EXECUTION_SCHEMA_VERSION,
    OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN,
    OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_SCHEMA_VERSION,
    OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION,
    OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION,
    OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN,
    OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_SCHEMA_VERSION,
    OcrRetryExecutionProviderError,
    build_ocr_retry_execution_bundle_report,
    build_ocr_retry_feedback_closure_apply_report,
    build_ocr_retry_feedback_closure_preview_report,
    build_ocr_retry_feedback_closure_restore_preview_report,
    build_ocr_retry_selection_template_report,
    format_ocr_retry_execution_bundle_report,
    format_ocr_retry_execution_report,
    format_ocr_retry_feedback_closure_apply_report,
    format_ocr_retry_feedback_closure_apply_verification_report,
    format_ocr_retry_feedback_closure_preview_report,
    format_ocr_retry_feedback_closure_restore_report,
    format_ocr_retry_selection_template_report,
    write_ocr_retry_execution_bundle,
    write_ocr_retry_feedback_closure_apply,
    write_ocr_retry_feedback_closure_restore,
)
from tests.test_build_manual_evals_db import _PNG_1X1, _init_history_db


def _build_ready_selection_fixture(
    tmp: Path,
    *,
    duplicate_artifacts: bool = False,
) -> tuple[Path, Path, list[str]]:
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
                recommended_action = 'Retry OCR with a tighter crop and attach fresh image evidence.'
            """
        )
        conn.execute(
            """
            UPDATE ocr_runs
            SET source_message_id = NULL,
                result_message_id = NULL
            """
        )
        if duplicate_artifacts:
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
    template = build_ocr_retry_selection_template_report(
        db_path=output_db,
        outcome="partial",
        cohort="ocr_retry_evidence",
        limit=10,
    )
    template_item = template["selection_template"]["items"][0]
    artifact_ids = sorted(
        candidate["artifact_id"] for candidate in template_item["candidate_artifacts"]
    )
    selected_artifact_ids = artifact_ids if duplicate_artifacts else [artifact_ids[0]]
    selection_path = tmp / "ocr_retry_selection.json"
    selection_path.write_text(
        json.dumps(
            {
                "schema_version": "polinko.manual_eval_ocr_retry_selection_decisions.v1",
                "decisions": [
                    {
                        "shortlist_id": template_item["shortlist_id"],
                        "selected_action": "rerun_input",
                        "selected_artifact_ids": selected_artifact_ids,
                        "rationale": "Execute the selected OCR retry artifact.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return output_db, selection_path, selected_artifact_ids


def _feedback_statuses(db_path: Path) -> list[str]:
    with closing(sqlite3.connect(db_path)) as conn:
        return [
            str(row[0])
            for row in conn.execute(
                "SELECT status FROM feedback ORDER BY id"
            ).fetchall()
        ]


def _feedback_rows(db_path: Path) -> list[dict[str, object]]:
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        return [
            dict(row)
            for row in conn.execute("SELECT * FROM feedback ORDER BY id").fetchall()
        ]


class OcrRetryLocalExecutorTests(unittest.TestCase):
    def test_selection_template_terminal_output_hides_absolute_source_paths(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, _selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )

            report = build_ocr_retry_selection_template_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            summary = format_ocr_retry_selection_template_report(report)

            self.assertIn(
                "manual eval OCR retry selection template: state=ok",
                summary,
            )
            self.assertIn("source_path=image1.png", summary)
            self.assertNotIn(str(tmp / "images" / "image1.png"), summary)

    def test_missing_confirmation_blocks_before_provider_call(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            provider_calls: list[dict[str, object]] = []

            report = write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token="",
                execution_dir=tmp / "runs",
                run_id="run-missing-confirm",
                ocr_runner=lambda request: provider_calls.append(request) or {},
            )

            self.assertEqual(
                report["schema_version"], OCR_RETRY_EXECUTION_SCHEMA_VERSION
            )
            self.assertEqual(report["state"], "blocked")
            self.assertEqual(
                [blocker["code"] for blocker in report["execution_blockers"]],
                ["missing_confirmation"],
            )
            self.assertEqual(provider_calls, [])
            self.assertFalse((tmp / "runs").exists())

    def test_execution_recomputes_readiness_and_writes_local_bundle(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            provider_calls: list[dict[str, object]] = []

            def fake_runner(request: dict[str, object]) -> dict[str, object]:
                provider_calls.append(request)
                return {
                    "status": "ok",
                    "provider": "mock",
                    "model": "mock-ocr",
                    "extracted_text": "fresh OCR text",
                    "extracted_text_preview": "fresh OCR text",
                    "chars": 14,
                }

            report = write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                ocr_provider="scaffold",
                ocr_model="mock-ocr",
                run_id="run-ok",
                ocr_runner=fake_runner,
            )
            summary = format_ocr_retry_execution_report(report)

            self.assertEqual(report["state"], "completed")
            self.assertEqual(report["readiness_state"], "ready")
            self.assertEqual(report["counts"]["requests"], 1)
            self.assertEqual(report["counts"]["responses"], 1)
            self.assertEqual(report["counts"]["succeeded"], 1)
            self.assertEqual(
                report["mutation_boundary"]["manual_eval_warehouse"], "none"
            )
            self.assertEqual(len(provider_calls), 1)
            self.assertEqual(provider_calls[0]["artifact_id"], artifact_ids[0])
            self.assertIn(
                "manual eval OCR retry execution: state=completed readiness=ready",
                summary,
            )

            run_dir = tmp / "runs" / "run-ok"
            manifest = json.loads((run_dir / "manifest.json").read_text("utf-8"))
            requests = [
                json.loads(line)
                for line in (run_dir / "requests.jsonl").read_text("utf-8").splitlines()
            ]
            responses = [
                json.loads(line)
                for line in (run_dir / "responses.jsonl")
                .read_text("utf-8")
                .splitlines()
            ]
            summary_payload = json.loads((run_dir / "summary.json").read_text("utf-8"))

            self.assertEqual(manifest["readiness_state"], "ready")
            self.assertEqual(len(manifest["selection_fingerprint"]), 64)
            self.assertEqual(
                requests[0]["operation"], "ocr_retry_rerun_or_case_curation"
            )
            self.assertEqual(requests[0]["warehouse_mutation"], "none")
            self.assertEqual(responses[0]["status"], "ok")
            self.assertEqual(responses[0]["extracted_text_preview"], "fresh OCR text")
            self.assertEqual(summary_payload["state"], "completed")
            self.assertEqual(
                summary_payload["mutation_boundary"]["manual_eval_warehouse"],
                "none",
            )
            self.assertEqual(_feedback_statuses(output_db), ["open"])

    def test_execution_bundle_report_inspects_local_bundle_without_path_leak(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )

            write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                ocr_provider="scaffold",
                ocr_model="mock-ocr",
                run_id="run-report-ok",
                ocr_runner=lambda request: {
                    "status": "ok",
                    "provider": "mock",
                    "model": "mock-ocr",
                    "extracted_text": "fresh OCR text",
                },
            )

            run_dir = tmp / "runs" / "run-report-ok"
            report = build_ocr_retry_execution_bundle_report(run_dir=run_dir)
            summary = format_ocr_retry_execution_bundle_report(report)

            self.assertEqual(
                report["schema_version"], OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION
            )
            self.assertEqual(report["state"], "ok")
            self.assertEqual(report["run_id"], "run-report-ok")
            self.assertEqual(report["counts"]["requests"], 1)
            self.assertEqual(report["counts"]["responses"], 1)
            self.assertEqual(report["counts"]["succeeded"], 1)
            self.assertEqual(report["counts"]["failed"], 0)
            self.assertEqual(
                report["mutation_boundary"]["manual_eval_warehouse"],
                "none",
            )
            self.assertIn(
                "manual eval OCR retry execution bundle: state=ok run=run-report-ok",
                summary,
            )
            self.assertIn("dir=run-report-ok", summary)
            self.assertNotIn(tmpdir, summary)
            self.assertEqual(_feedback_statuses(output_db), ["open"])

    def test_execution_bundle_report_accepts_repo_relative_bundle_files(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            old_cwd = Path.cwd()
            try:
                os.chdir(tmp)
                write_ocr_retry_execution_bundle(
                    db_path=output_db,
                    selection_path=selection_path,
                    confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                    execution_dir=Path(".local/manual_eval_runs/ocr_retry"),
                    ocr_provider="scaffold",
                    ocr_model="mock-ocr",
                    run_id="run-report-relative",
                    ocr_runner=lambda request: {
                        "status": "ok",
                        "provider": "mock",
                        "model": "mock-ocr",
                        "extracted_text": "fresh OCR text",
                    },
                )

                run_dir = Path(".local/manual_eval_runs/ocr_retry/run-report-relative")
                report = build_ocr_retry_execution_bundle_report(run_dir=run_dir)
                summary = format_ocr_retry_execution_bundle_report(report)
            finally:
                os.chdir(old_cwd)

            self.assertEqual(report["state"], "ok")
            self.assertEqual(report["run_id"], "run-report-relative")
            self.assertEqual(report["counts"]["requests"], 1)
            self.assertEqual(report["counts"]["responses"], 1)
            self.assertEqual(report["inspection_blockers"], [])
            self.assertIn("dir=run-report-relative", summary)
            self.assertNotIn(tmpdir, summary)
            self.assertEqual(_feedback_statuses(output_db), ["open"])

    def test_execution_bundle_report_flags_provider_failure_as_attention(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, artifact_ids = _build_ready_selection_fixture(
                tmp,
                duplicate_artifacts=True,
            )

            def partial_runner(request: dict[str, object]) -> dict[str, object]:
                if request["artifact_id"] == artifact_ids[0]:
                    return {"status": "ok", "extracted_text": "first OCR text"}
                raise OcrRetryExecutionProviderError(
                    "rate limit reached",
                    status="rate_limited",
                    retry_after="7",
                )

            write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                ocr_provider="scaffold",
                ocr_model="mock-ocr",
                run_id="run-report-attention",
                ocr_runner=partial_runner,
            )

            report = build_ocr_retry_execution_bundle_report(
                run_dir=tmp / "runs" / "run-report-attention"
            )

            self.assertEqual(report["state"], "attention")
            self.assertEqual(report["counts"]["requests"], 2)
            self.assertEqual(report["counts"]["responses"], 2)
            self.assertEqual(report["counts"]["failed"], 1)
            self.assertEqual(report["inspection_blockers"], [])
            self.assertIn("provider failures", report["warnings"][0])

    def test_execution_bundle_report_blocks_on_mutation_boundary_drift(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                run_id="run-report-mutated",
                ocr_runner=lambda request: {
                    "status": "ok",
                    "extracted_text": "fresh OCR text",
                },
            )
            run_dir = tmp / "runs" / "run-report-mutated"
            request_rows = [
                json.loads(line)
                for line in (run_dir / "requests.jsonl").read_text("utf-8").splitlines()
            ]
            request_rows[0]["warehouse_mutation"] = "write"
            (run_dir / "requests.jsonl").write_text(
                "\n".join(json.dumps(row) for row in request_rows) + "\n",
                encoding="utf-8",
            )

            report = build_ocr_retry_execution_bundle_report(run_dir=run_dir)

            self.assertEqual(report["state"], "error")
            self.assertIn(
                "warehouse_mutation_not_none",
                [blocker["code"] for blocker in report["inspection_blockers"]],
            )

    def test_feedback_closure_preview_proposes_ready_feedback_without_mutation(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                ocr_provider="scaffold",
                ocr_model="mock-ocr",
                run_id="run-closure-ready",
                ocr_runner=lambda request: {
                    "status": "ok",
                    "provider": "mock",
                    "model": "mock-ocr",
                    "extracted_text": "fresh OCR text",
                },
            )

            report = build_ocr_retry_feedback_closure_preview_report(
                run_dir=tmp / "runs" / "run-closure-ready"
            )
            summary = format_ocr_retry_feedback_closure_preview_report(report)

            self.assertEqual(
                report["schema_version"],
                OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION,
            )
            self.assertEqual(report["state"], "ok")
            self.assertEqual(report["counts"]["feedback_items"], 1)
            self.assertEqual(report["counts"]["ready_feedback"], 1)
            self.assertEqual(
                report["mutation_boundary"]["feedback_closure"],
                "none",
            )
            closure_item = report["closure_items"][0]
            self.assertEqual(closure_item["state"], "ready")
            self.assertEqual(closure_item["proposed_feedback_status"], "closed")
            self.assertEqual(closure_item["mutation"], "none")
            self.assertIn(
                "manual eval OCR retry feedback closure preview: state=ok "
                "run=run-closure-ready",
                summary,
            )
            self.assertIn("dir=run-closure-ready", summary)
            self.assertNotIn(tmpdir, summary)
            self.assertEqual(_feedback_statuses(output_db), ["open"])

    def test_feedback_closure_preview_marks_mixed_response_status_as_attention(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, artifact_ids = _build_ready_selection_fixture(
                tmp,
                duplicate_artifacts=True,
            )

            def partial_runner(request: dict[str, object]) -> dict[str, object]:
                if request["artifact_id"] == artifact_ids[0]:
                    return {"status": "ok", "extracted_text": "first OCR text"}
                raise OcrRetryExecutionProviderError(
                    "rate limit reached",
                    status="rate_limited",
                    retry_after="7",
                )

            write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                run_id="run-closure-attention",
                ocr_runner=partial_runner,
            )

            report = build_ocr_retry_feedback_closure_preview_report(
                run_dir=tmp / "runs" / "run-closure-attention"
            )

            self.assertEqual(report["state"], "attention")
            self.assertEqual(report["counts"]["feedback_items"], 1)
            self.assertEqual(report["counts"]["attention_feedback"], 1)
            self.assertEqual(report["closure_items"][0]["state"], "attention")
            self.assertEqual(
                report["closure_items"][0]["reason"],
                "mixed_ocr_retry_response_status",
            )
            self.assertEqual(
                report["closure_items"][0]["proposed_feedback_status"],
                "open",
            )
            self.assertIn("provider failures", report["warnings"][0])
            self.assertEqual(_feedback_statuses(output_db), ["open"])

    def test_feedback_closure_preview_blocks_when_bundle_inspection_fails(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                run_id="run-closure-blocked",
                ocr_runner=lambda request: {
                    "status": "ok",
                    "extracted_text": "fresh OCR text",
                },
            )
            run_dir = tmp / "runs" / "run-closure-blocked"
            request_rows = [
                json.loads(line)
                for line in (run_dir / "requests.jsonl").read_text("utf-8").splitlines()
            ]
            request_rows[0]["warehouse_mutation"] = "write"
            (run_dir / "requests.jsonl").write_text(
                "\n".join(json.dumps(row) for row in request_rows) + "\n",
                encoding="utf-8",
            )

            report = build_ocr_retry_feedback_closure_preview_report(run_dir=run_dir)

            self.assertEqual(report["state"], "blocked")
            self.assertEqual(report["closure_items"], [])
            self.assertIn(
                "warehouse_mutation_not_none",
                [blocker["code"] for blocker in report["preview_blockers"]],
            )
            self.assertEqual(_feedback_statuses(output_db), ["open"])

    def test_feedback_closure_apply_requires_confirmation_before_backup(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                run_id="run-closure-missing-confirm",
                ocr_runner=lambda request: {
                    "status": "ok",
                    "extracted_text": "fresh OCR text",
                },
            )

            report = write_ocr_retry_feedback_closure_apply(
                db_path=output_db,
                run_dir=tmp / "runs" / "run-closure-missing-confirm",
                confirm_token="",
                backup_root=tmp / "archive",
                applied_at="20260521T010203Z",
            )

            self.assertEqual(
                report["schema_version"],
                OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION,
            )
            self.assertEqual(report["state"], "blocked")
            self.assertIn(
                "missing_confirmation",
                [blocker["code"] for blocker in report["apply_blockers"]],
            )
            self.assertFalse((tmp / "archive").exists())
            self.assertEqual(_feedback_statuses(output_db), ["open"])

    def test_feedback_closure_apply_closes_ready_feedback_after_backup(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            before_rows = _feedback_rows(output_db)
            write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                run_id="run-closure-apply",
                ocr_runner=lambda request: {
                    "status": "ok",
                    "provider": "mock",
                    "model": "mock-ocr",
                    "extracted_text": "fresh OCR text",
                },
            )

            report = write_ocr_retry_feedback_closure_apply(
                db_path=output_db,
                run_dir=tmp / "runs" / "run-closure-apply",
                confirm_token=OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN,
                backup_root=tmp / "archive",
                applied_at="20260521T010203Z",
            )
            summary = format_ocr_retry_feedback_closure_apply_report(report)

            self.assertEqual(report["state"], "applied")
            self.assertEqual(report["bundle_state"], "ok")
            self.assertEqual(report["preview_state"], "ok")
            self.assertEqual(report["counts"]["updated_feedback_rows"], 1)
            self.assertEqual(
                report["mutation_boundary"]["manual_eval_warehouse"],
                "feedback_rows_only",
            )
            self.assertEqual(report["updated_feedback_ids"], [1])
            backup_dir = (
                tmp
                / "archive"
                / ("manual-evals-feedback-closure-apply-20260521T010203Z")
            )
            self.assertTrue((backup_dir / "manual_evals.db").is_file())
            self.assertTrue((backup_dir / "manifest.json").is_file())
            self.assertTrue(
                (
                    tmp
                    / "runs"
                    / "run-closure-apply"
                    / "feedback_closure_apply_summary.json"
                ).is_file()
            )
            with closing(sqlite3.connect(backup_dir / "manual_evals.db")) as conn:
                self.assertEqual(
                    conn.execute("PRAGMA integrity_check").fetchone()[0],
                    "ok",
                )
                self.assertEqual(
                    [
                        str(row[0])
                        for row in conn.execute(
                            "SELECT status FROM feedback ORDER BY id"
                        ).fetchall()
                    ],
                    ["open"],
                )
            after_rows = _feedback_rows(output_db)
            self.assertEqual(after_rows[0]["status"], "closed")
            self.assertIn("run-closure-apply", str(after_rows[0]["action_taken"]))
            self.assertGreater(
                int(after_rows[0]["updated_at"]),
                int(before_rows[0]["updated_at"]),
            )
            for unchanged_column in (
                "source_id",
                "era",
                "source_key",
                "source_label",
                "source_history_db",
                "source_session_id",
                "session_id",
                "message_id",
                "outcome",
                "tags_json",
                "note",
                "recommended_action",
                "created_at",
            ):
                self.assertEqual(
                    after_rows[0][unchanged_column],
                    before_rows[0][unchanged_column],
                    unchanged_column,
                )
            self.assertIn(
                "manual eval OCR retry feedback closure apply: state=applied "
                "run=run-closure-apply",
                summary,
            )
            self.assertIn(
                "backup_dir=manual-evals-feedback-closure-apply-20260521T010203Z",
                summary,
            )
            self.assertNotIn(tmpdir, summary)

            verification = build_ocr_retry_feedback_closure_apply_report(
                db_path=output_db,
                run_dir=tmp / "runs" / "run-closure-apply",
            )
            verification_summary = (
                format_ocr_retry_feedback_closure_apply_verification_report(
                    verification
                )
            )
            self.assertEqual(
                verification["schema_version"],
                OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_SCHEMA_VERSION,
            )
            self.assertEqual(verification["state"], "ok")
            self.assertEqual(verification["counts"]["target_feedback_rows"], 1)
            self.assertEqual(verification["counts"]["active_closed_feedback"], 1)
            self.assertEqual(verification["counts"]["backup_open_feedback"], 1)
            self.assertEqual(verification["counts"]["report_blockers"], 0)
            self.assertEqual(verification["manual_evals_db"]["integrity_check"], "ok")
            self.assertEqual(verification["backup"]["integrity_check"], "ok")
            self.assertEqual(
                verification["feedback_rows"][0]["active_status"],
                "closed",
            )
            self.assertEqual(
                verification["feedback_rows"][0]["backup_status"],
                "open",
            )
            self.assertIn(
                "manual eval OCR retry feedback closure apply report: state=ok "
                "run=run-closure-apply",
                verification_summary,
            )
            self.assertIn(
                "backup_dir=manual-evals-feedback-closure-apply-20260521T010203Z",
                verification_summary,
            )
            self.assertNotIn(tmpdir, verification_summary)

    def test_feedback_closure_apply_and_restore_accept_uppercase_statuses(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            with closing(sqlite3.connect(output_db)) as conn:
                conn.execute("UPDATE feedback SET status = 'OPEN' WHERE id = 1")
                conn.commit()
            write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                run_id="run-closure-uppercase",
                ocr_runner=lambda request: {
                    "status": "ok",
                    "provider": "mock",
                    "model": "mock-ocr",
                    "extracted_text": "fresh OCR text",
                },
            )

            report = write_ocr_retry_feedback_closure_apply(
                db_path=output_db,
                run_dir=tmp / "runs" / "run-closure-uppercase",
                confirm_token=OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN,
                backup_root=tmp / "archive",
                applied_at="20260521T010203Z",
            )
            verification = build_ocr_retry_feedback_closure_apply_report(
                db_path=output_db,
                run_dir=tmp / "runs" / "run-closure-uppercase",
            )
            backup_dir = (
                tmp
                / "archive"
                / ("manual-evals-feedback-closure-apply-20260521T010203Z")
            )
            restore_preview = build_ocr_retry_feedback_closure_restore_preview_report(
                db_path=output_db,
                backup_dir=backup_dir,
            )

            self.assertEqual(report["state"], "applied")
            self.assertEqual(report["apply_items"][0]["status_before"], "OPEN")
            self.assertEqual(report["apply_items"][0]["status_after"], "CLOSED")
            self.assertEqual(_feedback_statuses(output_db), ["CLOSED"])
            self.assertEqual(verification["state"], "ok")
            self.assertEqual(verification["counts"]["active_closed_feedback"], 1)
            self.assertEqual(verification["counts"]["backup_open_feedback"], 1)
            self.assertEqual(
                verification["feedback_rows"][0]["active_status"],
                "CLOSED",
            )
            self.assertEqual(
                verification["feedback_rows"][0]["backup_status"],
                "OPEN",
            )
            self.assertEqual(restore_preview["state"], "ok")
            self.assertEqual(restore_preview["counts"]["active_closed_feedback"], 1)
            self.assertEqual(restore_preview["counts"]["backup_open_feedback"], 1)

            restore = write_ocr_retry_feedback_closure_restore(
                db_path=output_db,
                backup_dir=backup_dir,
                confirm_token=OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN,
                restore_root=tmp / "restore",
                restored_at="20260521T020304Z",
            )
            self.assertEqual(restore["state"], "restored")
            self.assertEqual(restore["restore_items"][0]["status_before"], "CLOSED")
            self.assertEqual(restore["restore_items"][0]["status_after"], "OPEN")
            self.assertEqual(restore["counts"]["restored_feedback_rows"], 1)
            self.assertEqual(_feedback_statuses(output_db), ["OPEN"])

    def test_feedback_closure_restore_preview_and_restore_from_apply_backup(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            before_rows = _feedback_rows(output_db)
            write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                run_id="run-closure-restore",
                ocr_runner=lambda request: {
                    "status": "ok",
                    "provider": "mock",
                    "model": "mock-ocr",
                    "extracted_text": "fresh OCR text",
                },
            )
            write_ocr_retry_feedback_closure_apply(
                db_path=output_db,
                run_dir=tmp / "runs" / "run-closure-restore",
                confirm_token=OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN,
                backup_root=tmp / "archive",
                applied_at="20260521T010203Z",
            )
            backup_dir = (
                tmp / "archive" / "manual-evals-feedback-closure-apply-20260521T010203Z"
            )

            preview = build_ocr_retry_feedback_closure_restore_preview_report(
                db_path=output_db,
                backup_dir=backup_dir,
            )
            preview_summary = format_ocr_retry_feedback_closure_restore_report(preview)

            self.assertEqual(
                preview["schema_version"],
                OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_SCHEMA_VERSION,
            )
            self.assertEqual(preview["state"], "ok")
            self.assertEqual(preview["mode"], "preview")
            self.assertEqual(preview["counts"]["target_feedback_rows"], 1)
            self.assertEqual(preview["counts"]["active_closed_feedback"], 1)
            self.assertEqual(preview["counts"]["backup_open_feedback"], 1)
            self.assertEqual(preview["counts"]["restore_blockers"], 0)
            self.assertIn(
                "manual eval OCR retry feedback closure restore: state=ok "
                "mode=preview run=run-closure-restore",
                preview_summary,
            )
            self.assertIn(
                "backup_dir=manual-evals-feedback-closure-apply-20260521T010203Z",
                preview_summary,
            )
            self.assertNotIn(tmpdir, preview_summary)

            restore = write_ocr_retry_feedback_closure_restore(
                db_path=output_db,
                backup_dir=backup_dir,
                confirm_token=OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN,
                restore_root=tmp / "restore-archive",
                restored_at="20260521T040506Z",
            )
            restore_summary = format_ocr_retry_feedback_closure_restore_report(restore)

            self.assertEqual(restore["state"], "restored")
            self.assertEqual(restore["counts"]["restored_feedback_rows"], 1)
            self.assertEqual(restore["counts"]["backups_written"], 1)
            self.assertEqual(restore["counts"]["restore_blockers"], 0)
            self.assertEqual(_feedback_rows(output_db), before_rows)
            restore_dir = (
                tmp
                / "restore-archive"
                / "manual-evals-feedback-closure-restore-20260521T040506Z"
            )
            self.assertTrue((restore_dir / "manual_evals.pre_restore.db").is_file())
            self.assertTrue((restore_dir / "restore_summary.json").is_file())
            with closing(
                sqlite3.connect(restore_dir / "manual_evals.pre_restore.db")
            ) as conn:
                self.assertEqual(
                    conn.execute("PRAGMA integrity_check").fetchone()[0],
                    "ok",
                )
                self.assertEqual(
                    [
                        str(row[0])
                        for row in conn.execute(
                            "SELECT status FROM feedback ORDER BY id"
                        ).fetchall()
                    ],
                    ["closed"],
                )
            self.assertIn(
                "manual eval OCR retry feedback closure restore: state=restored "
                "mode=restore run=run-closure-restore",
                restore_summary,
            )
            self.assertIn(
                "restore_dir=manual-evals-feedback-closure-restore-20260521T040506Z",
                restore_summary,
            )
            self.assertNotIn(tmpdir, restore_summary)

    def test_feedback_closure_restore_blocks_without_confirmation(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                run_id="run-closure-restore-blocked",
                ocr_runner=lambda request: {
                    "status": "ok",
                    "extracted_text": "fresh OCR text",
                },
            )
            write_ocr_retry_feedback_closure_apply(
                db_path=output_db,
                run_dir=tmp / "runs" / "run-closure-restore-blocked",
                confirm_token=OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN,
                backup_root=tmp / "archive",
                applied_at="20260521T010203Z",
            )
            backup_dir = (
                tmp / "archive" / "manual-evals-feedback-closure-apply-20260521T010203Z"
            )

            report = write_ocr_retry_feedback_closure_restore(
                db_path=output_db,
                backup_dir=backup_dir,
                confirm_token="",
                restore_root=tmp / "restore-archive",
                restored_at="20260521T040506Z",
            )

            self.assertEqual(report["state"], "blocked")
            self.assertIn(
                "missing_confirmation",
                [blocker["code"] for blocker in report["restore_blockers"]],
            )
            self.assertFalse((tmp / "restore-archive").exists())
            self.assertEqual(_feedback_statuses(output_db), ["closed"])

    def test_feedback_closure_apply_report_blocks_when_summary_missing(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, _selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            run_dir = tmp / "runs" / "missing-summary"
            run_dir.mkdir(parents=True)

            report = build_ocr_retry_feedback_closure_apply_report(
                db_path=output_db,
                run_dir=run_dir,
            )

            self.assertEqual(report["state"], "error")
            self.assertIn(
                "missing_apply_summary",
                [blocker["code"] for blocker in report["report_blockers"]],
            )
            self.assertEqual(_feedback_statuses(output_db), ["open"])

    def test_feedback_closure_apply_report_flags_active_status_drift(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                run_id="run-closure-report-drift",
                ocr_runner=lambda request: {
                    "status": "ok",
                    "extracted_text": "fresh OCR text",
                },
            )
            write_ocr_retry_feedback_closure_apply(
                db_path=output_db,
                run_dir=tmp / "runs" / "run-closure-report-drift",
                confirm_token=OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN,
                backup_root=tmp / "archive",
                applied_at="20260521T010203Z",
            )
            with closing(sqlite3.connect(output_db)) as conn:
                conn.execute("UPDATE feedback SET status = 'open' WHERE id = 1")
                conn.commit()

            report = build_ocr_retry_feedback_closure_apply_report(
                db_path=output_db,
                run_dir=tmp / "runs" / "run-closure-report-drift",
            )

            self.assertEqual(report["state"], "error")
            self.assertIn(
                "active_feedback_not_closed",
                [blocker["code"] for blocker in report["report_blockers"]],
            )
            self.assertEqual(report["counts"]["backup_open_feedback"], 1)

    def test_feedback_closure_apply_blocks_when_feedback_is_no_longer_open(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                run_id="run-closure-stale",
                ocr_runner=lambda request: {
                    "status": "ok",
                    "extracted_text": "fresh OCR text",
                },
            )
            with closing(sqlite3.connect(output_db)) as conn:
                conn.execute("UPDATE feedback SET status = 'closed' WHERE id = 1")
                conn.commit()

            report = write_ocr_retry_feedback_closure_apply(
                db_path=output_db,
                run_dir=tmp / "runs" / "run-closure-stale",
                confirm_token=OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN,
                backup_root=tmp / "archive",
                applied_at="20260521T010203Z",
            )

            self.assertEqual(report["state"], "blocked")
            self.assertIn(
                "feedback_rows_not_open",
                [blocker["code"] for blocker in report["apply_blockers"]],
            )
            self.assertFalse((tmp / "archive").exists())
            self.assertEqual(_feedback_statuses(output_db), ["closed"])

    def test_feedback_closure_apply_blocks_when_preview_needs_attention(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, artifact_ids = _build_ready_selection_fixture(
                tmp,
                duplicate_artifacts=True,
            )

            def partial_runner(request: dict[str, object]) -> dict[str, object]:
                if request["artifact_id"] == artifact_ids[0]:
                    return {"status": "ok", "extracted_text": "first OCR text"}
                raise OcrRetryExecutionProviderError(
                    "rate limit reached",
                    status="rate_limited",
                    retry_after="7",
                )

            write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                run_id="run-closure-apply-attention",
                ocr_runner=partial_runner,
            )

            report = write_ocr_retry_feedback_closure_apply(
                db_path=output_db,
                run_dir=tmp / "runs" / "run-closure-apply-attention",
                confirm_token=OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN,
                backup_root=tmp / "archive",
                applied_at="20260521T010203Z",
            )

            self.assertEqual(report["state"], "blocked")
            self.assertIn(
                "bundle_report_not_ok",
                [blocker["code"] for blocker in report["apply_blockers"]],
            )
            self.assertIn(
                "preview_not_ok",
                [blocker["code"] for blocker in report["apply_blockers"]],
            )
            self.assertFalse((tmp / "archive").exists())
            self.assertEqual(_feedback_statuses(output_db), ["open"])

    def test_context_only_selection_blocks_without_provider_call(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, _artifact_ids = _build_ready_selection_fixture(
                tmp
            )
            template = build_ocr_retry_selection_template_report(
                db_path=output_db,
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=10,
            )
            template_item = template["selection_template"]["items"][0]
            selection_path.write_text(
                json.dumps(
                    {
                        "decisions": [
                            {
                                "shortlist_id": template_item["shortlist_id"],
                                "selected_action": "context_only",
                                "rationale": "Keep as context.",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            provider_calls: list[dict[str, object]] = []

            report = write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                run_id="run-context",
                ocr_runner=lambda request: provider_calls.append(request) or {},
            )

            self.assertEqual(report["state"], "blocked")
            self.assertIn(
                "no_executable_items",
                [blocker["code"] for blocker in report["execution_blockers"]],
            )
            self.assertEqual(provider_calls, [])
            self.assertFalse((tmp / "runs").exists())

    def test_provider_failure_writes_local_evidence_without_warehouse_mutation(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            output_db, selection_path, artifact_ids = _build_ready_selection_fixture(
                tmp,
                duplicate_artifacts=True,
            )

            def partial_runner(request: dict[str, object]) -> dict[str, object]:
                if request["artifact_id"] == artifact_ids[0]:
                    return {
                        "status": "ok",
                        "provider": "mock",
                        "model": "mock-ocr",
                        "extracted_text": "first OCR text",
                    }
                raise OcrRetryExecutionProviderError(
                    "rate limit reached",
                    status="rate_limited",
                    retry_after="7",
                )

            report = write_ocr_retry_execution_bundle(
                db_path=output_db,
                selection_path=selection_path,
                confirm_token=OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
                execution_dir=tmp / "runs",
                ocr_provider="scaffold",
                ocr_model="mock-ocr",
                run_id="run-partial",
                ocr_runner=partial_runner,
            )

            self.assertEqual(report["state"], "partial_failure")
            self.assertEqual(report["counts"]["requests"], 2)
            self.assertEqual(report["counts"]["responses"], 2)
            self.assertEqual(report["counts"]["succeeded"], 1)
            self.assertEqual(report["counts"]["failed"], 1)
            self.assertEqual(report["stop_reason"], "rate_limited")

            run_dir = tmp / "runs" / "run-partial"
            responses = [
                json.loads(line)
                for line in (run_dir / "responses.jsonl")
                .read_text("utf-8")
                .splitlines()
            ]
            self.assertEqual(
                [response["status"] for response in responses], ["ok", "rate_limited"]
            )
            self.assertEqual(responses[1]["retry_after"], "7")
            self.assertEqual(
                json.loads((run_dir / "summary.json").read_text("utf-8"))[
                    "mutation_boundary"
                ]["manual_eval_warehouse"],
                "none",
            )
            self.assertEqual(_feedback_statuses(output_db), ["open"])


if __name__ == "__main__":
    unittest.main()
