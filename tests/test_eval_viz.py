import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from api.eval_viz import build_pass_fail_viz_payload, render_pass_fail_viz_html


class EvalVizTests(unittest.TestCase):
    def test_payload_prefers_eval_viz_db_lane_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "eval_viz.db"
            conn = sqlite3.connect(db_path)
            conn.executescript(
                """
                CREATE TABLE eval_points (
                    point_id TEXT PRIMARY KEY,
                    suite TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    case_id TEXT NOT NULL,
                    lane TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    pass_rate REAL NOT NULL,
                    ts_unix INTEGER NOT NULL,
                    source_path TEXT,
                    expected_text TEXT,
                    observed_text TEXT,
                    summary TEXT,
                    origin_file TEXT NOT NULL,
                    case_index INTEGER NOT NULL
                );
                CREATE TABLE metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            conn.executemany(
                """
                INSERT INTO eval_points (
                    point_id, suite, run_id, case_id, lane, outcome, pass_rate, ts_unix,
                    source_path, expected_text, observed_text, summary, origin_file, case_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    ("p1", "ocr", "1774901000", "typed-a", "typed", "pass", 1.0, 1774901000, "/tmp/typed-a.png", "alpha", "alpha", "", "origin-a", 0),
                    ("p2", "ocr", "1774901000", "hand-a", "handwriting", "fail", 0.0, 1774901000, "/tmp/hand-a.png", "beta", "bet", "", "origin-a", 1),
                    ("p3", "ocr", "1774901000", "ill-a", "illustration", "pass", 1.0, 1774901000, "/tmp/ill-a.png", "gamma", "gamma", "", "origin-a", 2),
                    ("p4", "ocr", "1774902000", "typed-b", "typed", "pass", 1.0, 1774902000, "/tmp/typed-b.png", "delta", "delta", "", "origin-b", 0),
                    ("p5", "ocr", "1774902000", "typed-c", "typed", "pass", 1.0, 1774902000, "/tmp/typed-c.png", "epsilon", "epsilon", "", "origin-b", 1),
                    ("p6", "ocr", "1774902000", "hand-b", "handwriting", "pass", 1.0, 1774902000, "/tmp/hand-b.png", "zeta", "zeta", "", "origin-b", 2),
                    ("p7", "ocr", "1774902000", "ill-b", "illustration", "error", 0.0, 1774902000, "/tmp/ill-b.png", "eta", "", "", "origin-b", 3),
                ],
            )
            conn.execute("INSERT INTO metadata (key, value) VALUES ('rebuilt_at_unix', '1774902999')")
            conn.commit()
            conn.close()

            payload = build_pass_fail_viz_payload(
                db_path=db_path,
                history_db_path=Path(tmp_dir) / "missing_history.db",
                max_evals=10,
            )

            self.assertEqual(payload["runs_total"], 2)
            self.assertEqual(payload["summary"]["run_id"], "1774902000")
            self.assertEqual(payload["summary"]["pass"], 3)
            self.assertEqual(payload["summary"]["errors"], 1)
            self.assertEqual(payload["summary"]["text"], 2)
            self.assertEqual(payload["summary"]["handwriting"], 1)
            self.assertEqual(payload["summary"]["illustration"], 1)
            self.assertEqual(payload["updated_at"], "2026-03-30T20:36:39Z")
            self.assertEqual(payload["points"][-1]["text"], 2)
            self.assertEqual(payload["points"][-1]["illustration"], 1)
            self.assertEqual(payload["evals"][0]["lane"], "text")
            self.assertEqual(payload["evals"][-1]["outcome"], "ERROR")

    def test_payload_prefers_history_ocr_runs_for_chart_points(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            eval_db_path = Path(tmp_dir) / "eval_viz.db"
            history_db_path = Path(tmp_dir) / "history.db"

            eval_conn = sqlite3.connect(eval_db_path)
            eval_conn.executescript(
                """
                CREATE TABLE eval_points (
                    point_id TEXT PRIMARY KEY,
                    suite TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    case_id TEXT NOT NULL,
                    lane TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    pass_rate REAL NOT NULL,
                    ts_unix INTEGER NOT NULL,
                    source_path TEXT,
                    expected_text TEXT,
                    observed_text TEXT,
                    summary TEXT,
                    origin_file TEXT NOT NULL,
                    case_index INTEGER NOT NULL
                );
                CREATE TABLE metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            eval_conn.executemany(
                """
                INSERT INTO eval_points (
                    point_id, suite, run_id, case_id, lane, outcome, pass_rate, ts_unix,
                    source_path, expected_text, observed_text, summary, origin_file, case_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    ("ep1", "ocr", "1774901000", "typed-a", "typed", "pass", 1.0, 1774901000, "/tmp/typed-a.png", "alpha", "alpha", "", "origin-a", 0),
                    ("ep2", "ocr", "1774902000", "typed-b", "typed", "fail", 0.0, 1774902000, "/tmp/typed-b.png", "beta", "bet", "", "origin-b", 0),
                ],
            )
            eval_conn.execute("INSERT INTO metadata (key, value) VALUES ('rebuilt_at_unix', '1774902999')")
            eval_conn.commit()
            eval_conn.close()

            history_conn = sqlite3.connect(history_db_path)
            history_conn.executescript(
                """
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
            history_conn.executemany(
                """
                INSERT INTO ocr_runs (
                    run_id, session_id, source_name, mime_type, source_message_id,
                    result_message_id, status, extracted_text, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    ("ocr-1", "session-1", "Screenshot-1.png", "image/png", None, None, "ok", "hello world", 1774903000),
                    ("ocr-2", "session-1", "IMG_0001.jpeg", "image/jpeg", None, None, "ok", "notes on paper", 1774904000),
                    ("ocr-3", "session-1", "diagram-card.png", "image/png", None, None, "ok", "NODE\nEDGE\nGRAPH", 1774905000),
                ],
            )
            history_conn.commit()
            history_conn.close()

            payload = build_pass_fail_viz_payload(
                db_path=eval_db_path,
                history_db_path=history_db_path,
                max_evals=10,
                max_history_runs=50,
            )

            self.assertEqual(payload["runs_total"], 3)
            self.assertEqual(payload["summary"]["run_id"], "1774902000")
            self.assertEqual(payload["summary_points"][-1]["run_id"], "1774902000")
            self.assertEqual(payload["points"][0]["text"], 1)
            self.assertEqual(payload["points"][1]["handwriting"], 1)
            self.assertEqual(payload["points"][2]["illustration"], 1)

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

            payload = build_pass_fail_viz_payload(report_root=root, max_evals=10)
            self.assertEqual(payload["runs_total"], 2)
            self.assertEqual(payload["summary"]["run_id"], "1711003600-r1")
            self.assertEqual(payload["summary"]["pass"], 4)
            self.assertEqual(payload["summary"]["fail"], 2)
            self.assertEqual(len(payload["evals"]), 1)
            row = payload["evals"][0]
            self.assertEqual(row["item"], "case-a")
            self.assertEqual(row["outcome"], "PASS")
            self.assertIn("contain: alpha", row["expected"])
            self.assertIn("contain any: beta | gamma", row["expected"])
            self.assertIn("ordered: one -> two", row["expected"])
            self.assertIn("regex: \\\\d+", row["expected"])
            self.assertEqual(row["observed"], "alpha and beta")
            self.assertTrue(row["row_key"].startswith("case-a::"))

    def test_payload_without_reports_has_safe_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload = build_pass_fail_viz_payload(report_root=Path(tmp_dir))
            self.assertEqual(payload["runs_total"], 0)
            self.assertEqual(payload["summary"]["pass"], 0)
            self.assertEqual(payload["summary"]["fail"], 0)
            self.assertEqual(payload["evals"], [])

    def test_html_contains_live_viz_markup(self) -> None:
        html = render_pass_fail_viz_html(refresh_ms=2500, chart_max_points=20)
        self.assertIn("Polinko Eval Pulse", html)
        self.assertIn("See the balance move.", html)
        self.assertIn('id="passRate"', html)
        self.assertIn('id="healthState"', html)
        self.assertIn('id="latestMix"', html)
        self.assertIn('id="windowLabel"', html)
        self.assertIn('id="chartTip"', html)
        self.assertIn("bucketed OCR lane history", html)
        self.assertIn("function clipId(runId)", html)
        self.assertIn("function bucketPoints(points, desiredBuckets = DEFAULT_MAX_CHART_POINTS)", html)
        self.assertIn("Latest Bucket", html)
        self.assertIn("Recent OCR mix", html)
        self.assertIn("0 text · 0 handwriting · 0 illustration", html)
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
