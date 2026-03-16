from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import backfill_eval_trace_artifacts as backfill


class BackfillEvalTraceArtifactsTests(unittest.TestCase):
    def _write_submissions(self, path: Path) -> None:
        rows = [
            {
                "timestamp_ms": 1710000000000,
                "session_id": "chat-a",
                "chat_title": "First",
                "message_id": "msg-a",
                "outcome": "pass",
                "positive_tags": ["accurate", "grounded"],
                "negative_tags": [],
                "status": "closed",
            },
            {
                "timestamp_ms": 1710000005000,
                "session_id": "chat-b",
                "chat_title": "Second",
                "message_id": "msg-b",
                "outcome": "partial",
                "positive_tags": ["style"],
                "negative_tags": ["grounding_gap"],
                "status": "open",
            },
        ]
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    def test_backfill_writes_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            submissions = Path(tmp) / "inbox" / "eval_submissions.jsonl"
            traces = Path(tmp) / "inbox" / "eval_trace_artifacts.jsonl"
            self._write_submissions(submissions)

            first = backfill.run_backfill(
                submissions_jsonl=submissions,
                trace_jsonl=traces,
                enabled=True,
            )
            self.assertEqual(first.source_count, 2)
            self.assertEqual(first.written_count, 2)
            self.assertEqual(first.skipped_existing, 0)

            lines = traces.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            entry = json.loads(lines[0])
            self.assertEqual(entry["tool_name"], "ui/eval_submission")
            self.assertEqual(entry["trace_type"], "ui_eval_submission")
            self.assertIn("submission_key", entry["metadata"])

            second = backfill.run_backfill(
                submissions_jsonl=submissions,
                trace_jsonl=traces,
                enabled=True,
            )
            self.assertEqual(second.source_count, 2)
            self.assertEqual(second.written_count, 0)
            self.assertEqual(second.skipped_existing, 2)

            lines_after = traces.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines_after), 2)

    def test_backfill_respects_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            submissions = Path(tmp) / "inbox" / "eval_submissions.jsonl"
            traces = Path(tmp) / "inbox" / "eval_trace_artifacts.jsonl"
            self._write_submissions(submissions)

            result = backfill.run_backfill(
                submissions_jsonl=submissions,
                trace_jsonl=traces,
                enabled=True,
                limit=1,
            )
            self.assertEqual(result.source_count, 1)
            self.assertEqual(result.written_count, 1)
            self.assertEqual(result.skipped_existing, 0)


if __name__ == "__main__":
    unittest.main()
