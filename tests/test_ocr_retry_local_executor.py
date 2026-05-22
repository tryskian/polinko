import json
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
    OcrRetryExecutionProviderError,
    build_ocr_retry_execution_bundle_report,
    build_ocr_retry_selection_template_report,
    format_ocr_retry_execution_bundle_report,
    format_ocr_retry_execution_report,
    write_ocr_retry_execution_bundle,
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


class OcrRetryLocalExecutorTests(unittest.TestCase):
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
