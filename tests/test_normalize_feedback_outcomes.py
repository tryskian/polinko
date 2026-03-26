import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tools.normalize_feedback_outcomes import normalize_feedback_outcomes


class NormalizeFeedbackOutcomesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "history.db"
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE message_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    outcome TEXT NOT NULL,
                    tags_json TEXT,
                    updated_at INTEGER NOT NULL DEFAULT 0
                );
                """
            )
            conn.commit()
        finally:
            conn.close()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _insert_feedback_row(self, *, outcome: str, tags_json: dict[str, list[str]] | list[str]) -> int:
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "INSERT INTO message_feedback(outcome, tags_json, updated_at) VALUES (?, ?, 0);",
                (outcome, json.dumps(tags_json, separators=(",", ":"))),
            )
            conn.commit()
            return int(cursor.lastrowid)
        finally:
            conn.close()

    def _fetch_row(self, row_id: int) -> tuple[str, dict[str, list[str]]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT outcome, tags_json FROM message_feedback WHERE id = ?;",
                (row_id,),
            ).fetchone()
        finally:
            conn.close()
        assert row is not None
        payload = json.loads(str(row["tags_json"]))
        return str(row["outcome"]), payload

    def test_mixed_outcome_is_mapped_to_fail_with_needs_retry(self) -> None:
        row_id = self._insert_feedback_row(
            outcome="MIXED",
            tags_json={"positive": ["style"], "negative": [], "all": ["style"]},
        )
        result = normalize_feedback_outcomes(str(self.db_path))
        self.assertEqual(result.scanned, 1)
        self.assertEqual(result.updated, 1)
        self.assertEqual(result.mixed_mapped, 1)
        self.assertEqual(result.unknown_mapped, 0)

        outcome, payload = self._fetch_row(row_id)
        self.assertEqual(outcome, "fail")
        self.assertIn("needs_retry", payload["negative"])
        self.assertIn("needs_retry", payload["all"])

    def test_unknown_outcome_is_failed_closed(self) -> None:
        row_id = self._insert_feedback_row(
            outcome="PARTIAL",
            tags_json={"positive": [], "negative": ["grounding_gap"], "all": ["grounding_gap"]},
        )
        result = normalize_feedback_outcomes(str(self.db_path))
        self.assertEqual(result.scanned, 1)
        self.assertEqual(result.updated, 1)
        self.assertEqual(result.mixed_mapped, 0)
        self.assertEqual(result.unknown_mapped, 1)

        outcome, payload = self._fetch_row(row_id)
        self.assertEqual(outcome, "fail")
        self.assertIn("grounding_gap", payload["negative"])
        self.assertIn("needs_retry", payload["negative"])

    def test_dry_run_reports_changes_without_writing(self) -> None:
        row_id = self._insert_feedback_row(outcome="mixed", tags_json=["style"])
        result = normalize_feedback_outcomes(str(self.db_path), dry_run=True)
        self.assertEqual(result.scanned, 1)
        self.assertEqual(result.updated, 1)
        self.assertEqual(result.mixed_mapped, 1)

        outcome, payload = self._fetch_row(row_id)
        self.assertEqual(outcome, "mixed")
        self.assertEqual(payload, ["style"])


if __name__ == "__main__":
    unittest.main()
