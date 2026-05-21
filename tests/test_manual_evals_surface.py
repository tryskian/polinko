import base64
from contextlib import closing
import json
import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from polinko.api.manual_eval_contracts import (
    MANUAL_EVALS_DB_SCHEMA_VERSION,
    SOURCE_FIRST_SCHEMA_VERSION,
)
from polinko.api.manual_evals_surface import build_manual_evals_surface_payload
from tools.build_manual_evals_db import build_manual_evals_db
from tests.test_build_manual_evals_db import _init_history_db

_PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+lmR8AAAAASUVORK5CYII="
)


class ManualEvalsSurfaceTests(unittest.TestCase):
    def test_returns_unavailable_when_db_missing(self) -> None:
        payload = build_manual_evals_surface_payload(
            db_path=Path("/tmp/non-existent-manual-evals.db"),
        )
        self.assertFalse(payload["available"])
        self.assertEqual(payload["summary"]["ocr_runs"], 0)
        self.assertEqual(payload["runs"], [])
        self.assertEqual(
            payload["source_first"]["schema_version"], SOURCE_FIRST_SCHEMA_VERSION
        )
        self.assertEqual(payload["source_first"]["exclusions"], [])
        self.assertEqual(payload["data_freshness"]["state"], "missing")
        self.assertFalse(payload["data_freshness"]["manual_evals_db"]["exists"])

    def test_returns_runs_sessions_and_image_preview_fields(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            history_db = root / "history.db"
            output_db = root / "manual_evals.db"
            image_dir = root / "images"
            image_dir.mkdir(parents=True, exist_ok=True)
            (image_dir / "image1.png").write_bytes(_PNG_1X1)

            _init_history_db(history_db)
            build_manual_evals_db(
                history_db=history_db,
                output_db=output_db,
                image_roots=[image_dir],
                include_thumbnails=True,
                thumbnail_size=64,
            )

            payload = build_manual_evals_surface_payload(
                db_path=output_db,
                max_runs=20,
                max_sessions=10,
            )
            self.assertTrue(payload["available"])
            self.assertEqual(payload["summary"]["sessions"], 1)
            self.assertEqual(payload["summary"]["ocr_runs"], 1)
            self.assertEqual(len(payload["sessions"]), 1)
            self.assertEqual(len(payload["runs"]), 1)
            self.assertEqual(
                payload["source_first"]["contract"]["chain"],
                ["source_artifact", "row_or_case_judgment", "lane_summary"],
            )
            self.assertEqual(
                payload["source_first"]["schema_version"], SOURCE_FIRST_SCHEMA_VERSION
            )
            self.assertEqual(
                payload["metadata"]["schema_version"], MANUAL_EVALS_DB_SCHEMA_VERSION
            )
            self.assertEqual(payload["data_freshness"]["state"], "current")
            self.assertTrue(
                payload["data_freshness"]["manual_evals_db"]["schema_current"]
            )
            self.assertEqual(
                payload["source_first"]["data_freshness"]["state"], "current"
            )
            self.assertEqual(
                payload["source_first"]["contract"]["promotion_gate"],
                "repeated_lane_signal",
            )
            self.assertEqual(
                payload["source_first"]["contract"]["summary_unit"], "lane_summary"
            )
            self.assertNotIn("rollup_unit", payload["source_first"]["contract"])
            self.assertNotIn("rejected_rollup", payload["source_first"]["contract"])
            self.assertNotIn(
                "pulse", json.dumps(payload["source_first"]["contract"]).lower()
            )
            exclusions = {
                row["key"]: row for row in payload["source_first"]["exclusions"]
            }
            self.assertEqual(exclusions["ocr_without_manual_feedback"]["count"], 1)
            self.assertEqual(exclusions["session_without_judgment"]["count"], 1)
            self.assertEqual(exclusions["open_manual_feedback"]["count"], 0)
            self.assertIn(
                "row-level manual judgment",
                exclusions["ocr_without_manual_feedback"]["reason"],
            )
            run = payload["runs"][0]
            self.assertEqual(run["run_id"], "ocr-1")
            self.assertEqual(run["source_run_id"], "ocr-1")
            self.assertEqual(run["era"], "current")
            self.assertEqual(run["session_id"], "chat-1")
            self.assertEqual(run["source_session_id"], "chat-1")
            self.assertIn("image", run)
            self.assertIn("session_eval", run)
            self.assertEqual(run["session_eval"]["feedback_count"], 0)
            image = run["image"]
            self.assertTrue(str(image["source_filename"]).endswith("image1.png"))
            self.assertEqual(image["display_filename"], "image1.png")
            self.assertIn(
                image["status"],
                {"thumbnail_ready", "resolved_no_pillow", "thumbnail_error"},
            )
            if image["status"] == "thumbnail_ready":
                self.assertTrue(
                    str(image["thumbnail_data_url"]).startswith(
                        "data:image/png;base64,"
                    )
                )

    def test_data_freshness_reports_stale_source_counts_without_rebuild(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            history_db = root / "history.db"
            output_db = root / "manual_evals.db"

            _init_history_db(history_db)
            build_manual_evals_db(
                history_db=history_db,
                output_db=output_db,
                include_thumbnails=False,
            )
            with closing(sqlite3.connect(history_db)) as conn:
                conn.execute(
                    """
                    INSERT INTO chats (session_id, title, created_at, updated_at, status, deprecated_at)
                    VALUES ('chat-2', 'Fresh manual source', 300, 400, 'active', NULL)
                    """
                )
                conn.execute(
                    """
                    INSERT INTO ocr_runs (
                      run_id, session_id, source_name, mime_type,
                      source_message_id, result_message_id, status, extracted_text, created_at
                    ) VALUES (
                      'ocr-2', 'chat-2', 'image2.png', 'image/png',
                      'm-source-2', 'm-result-2', 'ok', 'new source text', 350
                    )
                    """
                )
                conn.commit()

            payload = build_manual_evals_surface_payload(db_path=output_db)
            freshness = payload["data_freshness"]
            source = freshness["source_history_dbs"][0]

            self.assertEqual(freshness["state"], "stale")
            self.assertTrue(freshness["warnings"])
            self.assertEqual(source["recorded_counts"]["sessions"], 1)
            self.assertEqual(source["current_counts"]["sessions"], 2)
            self.assertEqual(source["count_deltas"]["sessions"], 1)
            self.assertEqual(source["count_deltas"]["ocr_runs"], 1)

    def test_data_freshness_ignores_chats_outside_manual_eval_import_scope(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            history_db = root / "history.db"
            output_db = root / "manual_evals.db"

            _init_history_db(history_db)
            build_manual_evals_db(
                history_db=history_db,
                output_db=output_db,
                include_thumbnails=False,
            )
            with closing(sqlite3.connect(history_db)) as conn:
                conn.execute(
                    """
                    INSERT INTO chats (session_id, title, created_at, updated_at, status, deprecated_at)
                    VALUES ('chat-idle', 'Idle chat', 9999999999990, 9999999999999, 'active', NULL)
                    """
                )
                conn.commit()

            payload = build_manual_evals_surface_payload(db_path=output_db)
            freshness = payload["data_freshness"]
            source = freshness["source_history_dbs"][0]

            self.assertEqual(freshness["state"], "current")
            self.assertEqual(freshness["warnings"], [])
            self.assertEqual(source["count_scope"], "manual_eval_import")
            self.assertEqual(source["recorded_counts"]["sessions"], 1)
            self.assertEqual(source["current_counts"]["sessions"], 1)
            self.assertEqual(source["count_deltas"]["sessions"], 0)
            self.assertFalse(source["is_newer_than_generated"])

    def test_data_freshness_reports_old_manual_eval_schema_metadata(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            history_db = root / "history.db"
            output_db = root / "manual_evals.db"

            _init_history_db(history_db)
            build_manual_evals_db(
                history_db=history_db,
                output_db=output_db,
                include_thumbnails=False,
            )
            with closing(sqlite3.connect(output_db)) as conn:
                conn.execute("DELETE FROM metadata WHERE key = 'schema_version'")
                conn.commit()

            payload = build_manual_evals_surface_payload(db_path=output_db)

            self.assertEqual(payload["data_freshness"]["state"], "stale")
            self.assertFalse(
                payload["data_freshness"]["manual_evals_db"]["schema_current"]
            )
            self.assertIn(
                "manual_evals.db schema_version is missing or not current",
                payload["data_freshness"]["warnings"],
            )

    def test_source_first_payload_links_feedback_to_source_artifact(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            history_db = root / "history.db"
            output_db = root / "manual_evals.db"

            _init_history_db(history_db, feedback_outcome="FAIL")
            build_manual_evals_db(
                history_db=history_db,
                output_db=output_db,
                include_thumbnails=False,
            )

            payload = build_manual_evals_surface_payload(
                db_path=output_db,
                max_runs=20,
                max_sessions=10,
            )

            source_first = payload["source_first"]
            self.assertEqual(source_first["judgments"]["manual_feedback"]["total"], 1)
            self.assertEqual(source_first["judgments"]["manual_feedback"]["fail"], 1)
            self.assertEqual(source_first["judgments"]["manual_feedback"]["closed"], 1)
            self.assertEqual(
                source_first["lane_summaries"][0]["lane"], "manual_feedback"
            )
            self.assertEqual(
                source_first["lane_summaries"][0]["summary_unit"], "lane_summary"
            )
            self.assertNotIn("rollup_unit", source_first["lane_summaries"][0])
            exclusions = {row["key"]: row for row in source_first["exclusions"]}
            self.assertEqual(exclusions["ocr_without_manual_feedback"]["count"], 0)
            self.assertEqual(exclusions["session_without_judgment"]["count"], 0)
            self.assertEqual(len(source_first["evidence_rows"]), 1)

            evidence_row = source_first["evidence_rows"][0]
            self.assertEqual(evidence_row["row_kind"], "manual_feedback")
            self.assertEqual(evidence_row["source_artifact"]["type"], "chat_message")
            self.assertEqual(
                evidence_row["source_artifact"]["message_id"], "m-result-1"
            )
            self.assertEqual(evidence_row["judgment"]["unit"], "row")
            self.assertEqual(evidence_row["judgment"]["outcome"], "fail")
            self.assertEqual(
                evidence_row["linked_case"]["match_type"], "feedback_result_message"
            )
            self.assertEqual(evidence_row["linked_case"]["source_run_id"], "ocr-1")
            self.assertEqual(
                evidence_row["linked_case"]["result_message_id"], "m-result-1"
            )

    def test_source_first_links_feedback_to_matching_ocr_result_not_latest_session_run(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            history_db = root / "history.db"
            output_db = root / "manual_evals.db"

            _init_history_db(history_db, feedback_outcome="FAIL")
            with closing(sqlite3.connect(history_db)) as conn:
                conn.execute(
                    """
                    INSERT INTO ocr_runs (
                      run_id, session_id, source_name, mime_type,
                      source_message_id, result_message_id, status, extracted_text, created_at
                    ) VALUES (
                      'ocr-2', 'chat-1', 'file-abc123-image2.png', 'image/png',
                      'm-source-2', 'm-result-2', 'ok', 'newer unrelated ocr text', 250
                    )
                    """
                )
                conn.commit()

            build_manual_evals_db(
                history_db=history_db,
                output_db=output_db,
                include_thumbnails=False,
            )

            payload = build_manual_evals_surface_payload(
                db_path=output_db,
                max_runs=20,
                max_sessions=10,
            )

            evidence_row = payload["source_first"]["evidence_rows"][0]
            linked_case = evidence_row["linked_case"]

            self.assertEqual(
                evidence_row["source_artifact"]["message_id"], "m-result-1"
            )
            self.assertEqual(linked_case["match_type"], "feedback_result_message")
            self.assertEqual(linked_case["source_run_id"], "ocr-1")
            self.assertEqual(linked_case["result_message_id"], "m-result-1")
            self.assertNotEqual(linked_case["source_run_id"], "ocr-2")


if __name__ == "__main__":
    unittest.main()
