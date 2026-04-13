import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from api.portfolio_sankey import build_portfolio_sankey_payload


def _init_manual_evals_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript(
            """
            CREATE TABLE sessions (
              session_id TEXT PRIMARY KEY,
              era TEXT NOT NULL,
              source_key TEXT NOT NULL,
              source_label TEXT NOT NULL,
              source_history_db TEXT NOT NULL,
              source_session_id TEXT NOT NULL,
              title TEXT NOT NULL,
              status TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL,
              deprecated_at INTEGER,
              message_count INTEGER NOT NULL,
              feedback_count INTEGER NOT NULL,
              checkpoint_count INTEGER NOT NULL,
              ocr_runs_count INTEGER NOT NULL,
              last_feedback_at INTEGER,
              last_checkpoint_at INTEGER,
              last_ocr_at INTEGER
            );
            CREATE TABLE feedback (
              id INTEGER PRIMARY KEY,
              source_id INTEGER NOT NULL,
              era TEXT NOT NULL,
              source_key TEXT NOT NULL,
              source_label TEXT NOT NULL,
              source_history_db TEXT NOT NULL,
              source_session_id TEXT NOT NULL,
              session_id TEXT NOT NULL,
              message_id TEXT NOT NULL,
              outcome TEXT NOT NULL,
              tags_json TEXT NOT NULL,
              note TEXT,
              recommended_action TEXT,
              action_taken TEXT,
              status TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL
            );
            CREATE TABLE ocr_runs (
              id INTEGER PRIMARY KEY,
              source_id INTEGER NOT NULL,
              source_run_id TEXT NOT NULL,
              era TEXT NOT NULL,
              source_key TEXT NOT NULL,
              source_label TEXT NOT NULL,
              source_history_db TEXT NOT NULL,
              source_session_id TEXT NOT NULL,
              run_id TEXT UNIQUE NOT NULL,
              session_id TEXT NOT NULL,
              source_name TEXT,
              mime_type TEXT,
              source_message_id TEXT,
              result_message_id TEXT,
              status TEXT NOT NULL,
              extracted_text TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              image_asset_id INTEGER
            );
            """
        )
        conn.execute(
            """
            INSERT INTO sessions (
              session_id, era, source_key, source_label, source_history_db,
              source_session_id, title, status, created_at, updated_at,
              deprecated_at, message_count, feedback_count, checkpoint_count,
              ocr_runs_count, last_feedback_at, last_checkpoint_at, last_ocr_at
            ) VALUES (
              'beta_1_0:chat-1', 'beta_1_0', 'beta_1_0', 'beta_1_0',
              '/tmp/beta.db', 'chat-1', 'Beta OCR', 'active', 100, 300,
              NULL, 3, 3, 0, 1, 290, NULL, 250
            )
            """
        )
        conn.execute(
            """
            INSERT INTO ocr_runs (
              id, source_id, source_run_id, era, source_key, source_label,
              source_history_db, source_session_id, run_id, session_id,
              source_name, mime_type, source_message_id, result_message_id,
              status, extracted_text, created_at, image_asset_id
            ) VALUES (
              1, 1, 'ocr-legacy-1', 'beta_1_0', 'beta_1_0', 'beta_1_0',
              '/tmp/beta.db', 'chat-1', 'beta_1_0:ocr-legacy-1',
              'beta_1_0:chat-1', 'legacy.png', 'image/png', NULL, NULL,
              'ok', 'legacy text', 250, NULL
            )
            """
        )
        feedback_rows = [
            (
                1,
                "PASS",
                {"positive": ["ocr_accurate"], "negative": [], "all": ["ocr_accurate"]},
                "good OCR",
                170,
            ),
            (
                2,
                "FAIL",
                {
                    "positive": [],
                    "negative": ["ocr_miss", "grounding_gap"],
                    "all": ["ocr_miss", "grounding_gap"],
                },
                "missed evidence",
                180,
            ),
            (
                3,
                "PARTIAL",
                {"positive": [], "negative": ["style_mismatch"], "all": ["style_mismatch"]},
                "voice was off",
                190,
            ),
        ]
        conn.executemany(
            """
            INSERT INTO feedback (
              id, source_id, era, source_key, source_label, source_history_db,
              source_session_id, session_id, message_id, outcome, tags_json,
              note, recommended_action, action_taken, status, created_at, updated_at
            ) VALUES (
              ?, 1, 'beta_1_0', 'beta_1_0', 'beta_1_0', '/tmp/beta.db',
              'chat-1', 'beta_1_0:chat-1', 'm-result-1', ?, ?, ?, NULL,
              NULL, 'logged', ?, ?
            )
            """,
            [
                (row_id, outcome, json.dumps(tags), note, created_at, created_at)
                for row_id, outcome, tags, note, created_at in feedback_rows
            ],
        )
        conn.commit()


def _write_binary_reports(root: Path) -> None:
    report_dir = root / "ocr_growth_stability_runs"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "run_id": "1711000000-r01",
        "summary": {"passed": 2, "failed": 2, "attempted": 4},
        "cases": [
            {
                "id": "typed-pass",
                "lane": "typed",
                "status": "pass",
                "source_name": "typed.png",
                "extracted_text": "typed pass",
            },
            {
                "id": "typed-fail",
                "lane": "typed",
                "status": "fail",
                "source_name": "typed-fail.png",
                "extracted_text": "typed fail",
            },
            {
                "id": "handwriting-fail",
                "lane": "handwriting",
                "status": "fail",
                "source_name": "handwriting.png",
                "extracted_text": "handwriting fail",
            },
            {
                "id": "illustration-pass",
                "lane": "illustration",
                "status": "pass",
                "source_name": "diagram.png",
                "extracted_text": "illustration pass",
            },
        ],
    }
    (report_dir / "ocr-1711000000-r01.json").write_text(json.dumps(report), encoding="utf-8")


class PortfolioSankeyTests(unittest.TestCase):
    def test_payload_requires_real_legacy_and_current_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            payload = build_portfolio_sankey_payload(
                manual_db_path=root / "missing-manual.db",
                report_root=root / "missing-reports",
            )

            self.assertFalse(payload["available"])
            self.assertEqual(payload["mode"], "no_data")
            self.assertEqual(payload["source_integrity"], "real_data_only")
            self.assertEqual(payload["graphs"]["legacy"]["links"], [])
            self.assertEqual(payload["graphs"]["bridge"]["links"], [])
            self.assertEqual(payload["graphs"]["current"]["links"], [])

    def test_payload_builds_twin_sankey_from_provenanced_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            manual_db = root / "manual_evals.db"
            report_root = root / "reports"
            _init_manual_evals_db(manual_db)
            _write_binary_reports(report_root)

            payload = build_portfolio_sankey_payload(
                manual_db_path=manual_db,
                report_root=report_root,
            )

            self.assertTrue(payload["available"])
            self.assertEqual(payload["mode"], "real_data")
            self.assertEqual(payload["summary"]["legacy_feedback_rows"], 3)
            self.assertEqual(payload["summary"]["legacy_signal_mentions"], 4)
            self.assertEqual(payload["summary"]["current_binary_cases"], 4)
            self.assertEqual(payload["summary"]["current_binary_reports"], 1)
            self.assertEqual(payload["sources"]["legacy"]["outcome_counts"]["FAIL"], 1)
            self.assertEqual(payload["sources"]["legacy"]["signal_counts"]["ocr_signal"], 2)
            self.assertEqual(payload["sources"]["current"]["lane_counts"]["text"], 2)
            self.assertEqual(payload["sources"]["current"]["outcome_counts"]["FAIL"], 2)

            all_node_ids = {
                node["id"]
                for graph in payload["graphs"].values()
                for node in graph["nodes"]
            }
            self.assertNotIn("prompt_router", all_node_ids)
            self.assertNotIn("noise_bucket", all_node_ids)

            legacy_links = payload["graphs"]["legacy"]["links"]
            current_links = payload["graphs"]["current"]["links"]
            self.assertIn(
                {
                    "source": "legacy_manual_feedback",
                    "target": "legacy_outcome_fail",
                    "value": 2,
                    "kind": "legacy_feedback_to_outcome",
                    "provenance": "manual_evals.feedback.outcome",
                },
                legacy_links,
            )
            self.assertIn(
                {
                    "source": "current_lane_text",
                    "target": "current_outcome_fail",
                    "value": 1,
                    "kind": "current_lane_to_outcome",
                    "provenance": "eval_reports.cases.outcome",
                },
                current_links,
            )


if __name__ == "__main__":
    unittest.main()
