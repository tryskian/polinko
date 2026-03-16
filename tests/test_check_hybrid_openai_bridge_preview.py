from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import check_hybrid_openai_bridge_preview as checker


def _valid_row() -> dict[str, object]:
    metrics = {
        "total": 3,
        "passed": 2,
        "failed": 1,
        "pass_rate": 0.666667,
    }
    trace_id = "oa_trace_1234567890abcdef"
    return {
        "schema_version": "polinko.hybrid_openai_trace_bridge.v1",
        "bridge_mode": "dry_run",
        "source_trace_id": "trace_abcdef0123456789",
        "openai_trace": {
            "trace_id": trace_id,
            "name": "tools/eval_style.py",
            "gate_outcomes": [{"name": "style", "passed": True, "detail": "ok"}],
            "gate_summary": metrics,
        },
        "openai_grader_preview": {
            "evaluation_id": "oa_eval_1234567890abcdef",
            "sample_id": "run-1",
            "task": "tools/eval_style.py",
            "labels": ["style"],
            "metrics": metrics,
            "source_trace_ref": trace_id,
        },
    }


class CheckHybridOpenAIBridgePreviewTests(unittest.TestCase):
    def test_validate_preview_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preview.jsonl"
            row = _valid_row()
            path.write_text(json.dumps(row) + "\n", encoding="utf-8")
            result = checker.validate_preview(preview_jsonl=path, min_rows=1)
            self.assertTrue(result.ok)
            self.assertEqual(result.row_count, 1)
            self.assertEqual(result.errors, [])

    def test_validate_preview_fails_on_missing_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preview.jsonl"
            row = _valid_row()
            row["openai_grader_preview"] = {"task": "oops"}
            path.write_text(json.dumps(row) + "\n", encoding="utf-8")
            result = checker.validate_preview(preview_jsonl=path, min_rows=1)
            self.assertFalse(result.ok)
            self.assertGreater(len(result.errors), 0)
            joined = " ".join(result.errors)
            self.assertIn("evaluation_id", joined)
            self.assertIn("source_trace_ref", joined)

    def test_validate_preview_fails_on_empty_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preview.jsonl"
            path.write_text("", encoding="utf-8")
            result = checker.validate_preview(preview_jsonl=path, min_rows=1)
            self.assertFalse(result.ok)
            self.assertEqual(result.row_count, 0)
            self.assertIn("requires at least 1 row", result.errors[0])


if __name__ == "__main__":
    unittest.main()
