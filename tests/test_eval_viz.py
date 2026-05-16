import json
import sqlite3
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from api.eval_viz import build_pass_fail_viz_payload, render_pass_fail_viz_html
from tools.build_manual_evals_db import build_manual_evals_db


def _init_viz_history_db(path: Path, *, include_feedback: bool = False) -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript(
            """
            CREATE TABLE chats (
              session_id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL,
              status TEXT NOT NULL DEFAULT 'active',
              deprecated_at INTEGER
            );
            CREATE TABLE chat_messages (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT NOT NULL,
              role TEXT NOT NULL,
              content TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              message_id TEXT,
              parent_message_id TEXT
            );
            CREATE TABLE message_feedback (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT NOT NULL,
              message_id TEXT NOT NULL,
              outcome TEXT NOT NULL,
              tags_json TEXT NOT NULL DEFAULT '[]',
              note TEXT,
              recommended_action TEXT,
              action_taken TEXT,
              status TEXT NOT NULL DEFAULT 'logged',
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL
            );
            CREATE TABLE eval_checkpoints (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              checkpoint_id TEXT UNIQUE NOT NULL,
              session_id TEXT NOT NULL,
              total_count INTEGER NOT NULL,
              pass_count INTEGER NOT NULL,
              fail_count INTEGER NOT NULL,
              other_count INTEGER NOT NULL,
              created_at INTEGER NOT NULL
            );
            CREATE TABLE ocr_runs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT UNIQUE NOT NULL,
              session_id TEXT NOT NULL,
              source_name TEXT,
              mime_type TEXT,
              source_message_id TEXT,
              result_message_id TEXT,
              status TEXT NOT NULL,
              extracted_text TEXT NOT NULL,
              created_at INTEGER NOT NULL
            );
            """
        )
        conn.execute(
            """
            INSERT INTO chats (session_id, title, created_at, updated_at, status, deprecated_at)
            VALUES ('chat-1', 'Manual OCR', 1774900000000, 1774904000000, 'active', NULL)
            """
        )
        conn.executemany(
            """
            INSERT INTO ocr_runs (
              run_id, session_id, source_name, mime_type, source_message_id,
              result_message_id, status, extracted_text, created_at
            ) VALUES (?, 'chat-1', ?, ?, NULL, NULL, ?, ?, ?)
            """,
            [
                ("ocr-1", "Screenshot-1.png", "image/png", "ok", "hello world", 1774901000000),
                ("ocr-2", "IMG_0001.jpeg", "image/jpeg", "ok", "notes on paper", 1774902000000),
                ("ocr-3", "diagram-card.png", "image/png", "error", "NODE\nEDGE\nGRAPH", 1774903000000),
            ],
        )
        if include_feedback:
            conn.execute(
                """
                INSERT INTO message_feedback (
                  session_id, message_id, outcome, tags_json, note, recommended_action,
                  action_taken, status, created_at, updated_at
                ) VALUES (
                  'chat-1', 'm-result-1', 'PASS', '[]', 'manual beta note',
                  NULL, NULL, 'closed', 1774902500000, 1774902600000
                )
                """
            )
        conn.commit()


def _init_tracked_eval_root(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "style-20260328-184149.json").write_text(
        json.dumps(
            {
                "run_id": "20260328-184149",
                "summary": {"total": 11, "passed": 11, "failed": 0},
                "cases": [],
                "generated_at": "2026-03-28T18:41:49Z",
            }
        ),
        encoding="utf-8",
    )
    (path / "operator_burden_rows.json").write_text(
        json.dumps(
            {
                "updated_at": "2026-05-09",
                "rows": [
                    {"verdict": "pass"},
                    {"verdict": "pass"},
                    {"verdict": "fail", "failure_disposition": "retain"},
                    {"verdict": "fail", "failure_disposition": "evict"},
                ],
            }
        ),
        encoding="utf-8",
    )


class EvalVizTests(unittest.TestCase):
    def test_payload_uses_manual_evals_db_for_points_and_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            history_db = root / "history.db"
            manual_db = root / "manual_evals.db"
            tracked_root = root / "tracked"
            _init_viz_history_db(history_db)
            _init_tracked_eval_root(tracked_root)
            build_manual_evals_db(
                history_db=history_db,
                output_db=manual_db,
                include_thumbnails=False,
            )

            payload = build_pass_fail_viz_payload(
                db_path=manual_db,
                max_evals=10,
                max_history_runs=50,
                tracked_eval_root=tracked_root,
            )

            self.assertEqual(payload["chart_mode"], "ocr_lanes")
            self.assertEqual(payload["runs_total"], 3)
            self.assertEqual(payload["summary"]["run_id"], "ocr-3")
            self.assertEqual(payload["summary"]["errors"], 1)
            self.assertEqual(payload["summary"]["text"], 0)
            self.assertEqual(payload["summary"]["handwriting"], 0)
            self.assertEqual(payload["summary"]["illustration"], 1)
            self.assertEqual(payload["points"][0]["text"], 1)
            self.assertEqual(payload["points"][1]["handwriting"], 1)
            self.assertEqual(payload["points"][-1]["illustration"], 1)
            self.assertEqual(payload["evals"][0]["lane"], "illustration")
            self.assertEqual(payload["evals"][0]["outcome"], "ERROR")
            self.assertEqual(len(payload["lane_summaries"]), 2)

    def test_payload_can_filter_eval_rows_by_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            history_db = root / "history.db"
            manual_db = root / "manual_evals.db"
            tracked_root = root / "tracked"
            _init_viz_history_db(history_db, include_feedback=True)
            _init_tracked_eval_root(tracked_root)
            build_manual_evals_db(
                history_db=history_db,
                output_db=manual_db,
                include_thumbnails=False,
            )

            payload = build_pass_fail_viz_payload(
                db_path=manual_db,
                max_evals=10,
                max_history_runs=50,
                run_id="ocr-2",
                tracked_eval_root=tracked_root,
            )

            self.assertEqual(payload["chart_mode"], "ocr_lanes")
            self.assertEqual(payload["runs_total"], 3)
            self.assertEqual(len(payload["evals"]), 1)
            self.assertEqual(payload["evals"][0]["source_run_id"], "ocr-2")
            self.assertEqual(payload["evals"][0]["outcome"], "PASS")
            self.assertIn("session feedback", payload["evals"][0]["expected"])

    def test_payload_prefers_fail_focused_feedback_chart_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            history_db = root / "history.db"
            manual_db = root / "manual_evals.db"
            tracked_root = root / "tracked"
            _init_viz_history_db(history_db, include_feedback=True)
            _init_tracked_eval_root(tracked_root)
            with sqlite3.connect(history_db) as conn:
                conn.executemany(
                    """
                    INSERT INTO message_feedback (
                      session_id, message_id, outcome, tags_json, note, recommended_action,
                      action_taken, status, created_at, updated_at
                    ) VALUES (
                      'chat-1', ?, ?, '[]', ?, NULL, NULL, 'closed', ?, ?
                    )
                    """,
                    [
                        ("m-result-2", "FAIL", "missed handwriting context", 1774902700000, 1774902800000),
                        ("m-result-3", "PARTIAL", "illustration text was incomplete", 1774902900000, 1774903000000),
                    ],
                )
                conn.commit()
            build_manual_evals_db(
                history_db=history_db,
                output_db=manual_db,
                include_thumbnails=False,
            )

            payload = build_pass_fail_viz_payload(
                db_path=manual_db,
                max_evals=10,
                max_history_runs=50,
                tracked_eval_root=tracked_root,
            )

            self.assertEqual(payload["chart_mode"], "feedback")
            self.assertEqual(payload["runs_total"], 3)
            self.assertEqual(Counter(point["outcome"] for point in payload["points"]), {
                "PASS": 1,
                "FAIL": 1,
                "PARTIAL": 1,
            })
            self.assertEqual(payload["evals"][0]["outcome"], "FAIL")
            self.assertIn("missed handwriting context", payload["evals"][0]["expected"])

    def test_payload_uses_latest_report_and_builds_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            stability_dir = root / "ocr_stability_runs"
            growth_dir = root / "ocr_growth_stability_runs"
            stability_dir.mkdir(parents=True, exist_ok=True)
            growth_dir.mkdir(parents=True, exist_ok=True)

            first = {
                "run_id": "1711000000-r1",
                "summary": {"passed": 2, "failed": 1, "errors": 0, "attempted": 3},
                "cases": [],
            }
            second = {
                "run_id": "1711003600-r1",
                "summary": {"passed": 4, "failed": 2, "errors": 0, "attempted": 6},
                "cases": [
                    {
                        "id": "case-a",
                        "status": "pass",
                        "must_contain": ["alpha"],
                        "must_contain_any": ["beta", "gamma"],
                        "must_appear_in_order": ["one", "two"],
                        "must_match_regex": [r"\\d+"],
                        "extracted_text": "alpha and beta",
                        "source_name": "sample-a.png",
                        "image_path": "/tmp/sample-a.png",
                    }
                ],
            }

            (stability_dir / "1711000000-r1.json").write_text(json.dumps(first), encoding="utf-8")
            (growth_dir / "1711003600-r1.json").write_text(json.dumps(second), encoding="utf-8")

            payload = build_pass_fail_viz_payload(
                report_root=root,
                max_evals=10,
                tracked_eval_root=root / "tracked",
            )
            self.assertEqual(payload["chart_mode"], "binary_gates")
            self.assertEqual(payload["runs_total"], 2)
            self.assertEqual(payload["summary"]["run_id"], "1711003600-r1")
            self.assertEqual(payload["summary"]["pass"], 4)
            self.assertEqual(payload["summary"]["fail"], 2)
            self.assertEqual(payload["summary"]["point_kind"], "binary_gate_report")
            self.assertEqual(len(payload["evals"]), 1)
            row = payload["evals"][0]
            self.assertEqual(row["item"], "case-a")
            self.assertEqual(row["outcome"], "PASS")
            self.assertIn("contain: alpha", row["expected"])
            self.assertIn("contain any: beta | gamma", row["expected"])
            self.assertIn("ordered: one -> two", row["expected"])
            self.assertIn("regex: \\\\d+", row["expected"])
            self.assertEqual(row["observed"], "alpha and beta")
            self.assertTrue(row["row_key"].startswith("1711003600-r1::case-a::"))

    def test_payload_without_reports_has_safe_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            payload = build_pass_fail_viz_payload(
                report_root=root,
                tracked_eval_root=root / "tracked",
            )
            self.assertEqual(payload["runs_total"], 0)
            self.assertEqual(payload["summary"]["pass"], 0)
            self.assertEqual(payload["summary"]["fail"], 0)
            self.assertEqual(payload["evals"], [])
            self.assertEqual(payload["lane_summaries"], [])

    def test_payload_includes_tracked_lane_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            tracked_root = root / "tracked"
            _init_tracked_eval_root(tracked_root)

            payload = build_pass_fail_viz_payload(
                report_root=root,
                tracked_eval_root=tracked_root,
            )

            self.assertEqual(payload["runs_total"], 0)
            summaries = {row["lane_key"]: row for row in payload["lane_summaries"]}
            self.assertIn("co_reasoning", summaries)
            self.assertIn("operator_burden", summaries)
            self.assertEqual(summaries["co_reasoning"]["pass"], 11)
            self.assertEqual(summaries["co_reasoning"]["fail"], 0)
            self.assertIn("/viz/pass-fail/artifact?path=", summaries["co_reasoning"]["source_url"])
            self.assertIn(
                "docs/research/co-reasoning-promotion-2026-05-08.md",
                summaries["co_reasoning"]["research_note_path"],
            )
            self.assertEqual(summaries["operator_burden"]["pass"], 2)
            self.assertEqual(summaries["operator_burden"]["fail"], 2)
            self.assertEqual(summaries["operator_burden"]["retain"], 1)
            self.assertEqual(summaries["operator_burden"]["evict"], 1)
            self.assertIn(
                "docs/research/operator-burden-promotion-2026-05-09.md",
                summaries["operator_burden"]["research_note_path"],
            )

    def test_html_contains_live_viz_markup(self) -> None:
        html = render_pass_fail_viz_html(refresh_ms=2500, chart_max_points=20)
        self.assertIn("Polinko Eval Pulse", html)
        self.assertIn("See the balance move.", html)
        self.assertIn('id="passRate"', html)
        self.assertIn('id="healthState"', html)
        self.assertIn('id="latestMix"', html)
        self.assertIn('id="windowLabel"', html)
        self.assertIn('id="chartTip"', html)
        self.assertIn('id="laneSummaries"', html)
        self.assertIn("Tracked Lane Snapshots", html)
        self.assertIn("lane-card-state", html)
        self.assertIn("lane-card-links", html)
        self.assertIn("lane-card-link", html)
        self.assertIn("bucketed binary gate report history", html)
        self.assertIn("bucketed manual eval outcome history", html)
        self.assertIn("bucketed active-lane mix history", html)
        self.assertIn("function clipId(runId)", html)
        self.assertIn("function bucketPoints(points, desiredBuckets = DEFAULT_MAX_CHART_POINTS)", html)
        self.assertIn("function computeFailState(rate, total)", html)
        self.assertIn("function sumPoints(points)", html)
        self.assertIn("Latest Bucket", html)
        self.assertIn("Current strict gate window", html)
        self.assertIn("Current evaluated window", html)
        self.assertIn("Recent active-lane mix", html)
        self.assertIn("0 fail · 0 pass", html)
        self.assertIn("fail rate in live gate window", html)
        self.assertIn("fail/partial rate in evaluated window", html)
        self.assertIn("chart_mode", html)
        self.assertIn("--lane-handwriting", html)
        self.assertIn("const REFRESH_MS = 2500;", html)
        self.assertIn("const DEFAULT_MAX_CHART_POINTS = 20;", html)
        self.assertIn('id="evalRows"', html)
        self.assertIn('id="evalEmpty"', html)
        self.assertIn('id="pollStatus"', html)
        self.assertIn('id="refreshNow"', html)
        self.assertNotIn('id="detailCard"', html)


if __name__ == "__main__":
    unittest.main()
