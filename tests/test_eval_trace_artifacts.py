from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import eval_trace_artifacts as traces


class EvalTraceArtifactTests(unittest.TestCase):
    def test_build_and_append_trace_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            trace_path = Path(tmp) / "trace.jsonl"
            payload = traces.build_eval_trace(
                run_id="run-123",
                tool_name="tools/eval_style.py",
                source_artifacts={"report_json": "eval_reports/style-123.json"},
                gate_outcomes=[{"name": "style_eval", "passed": True, "detail": "ok"}],
                summary={"total": 3, "passed": 3, "failed": 0},
                model_metadata={"judge_model": "gpt-4.1-mini"},
                metadata={"strict": True},
            )

            written_path = traces.append_eval_trace(
                trace_payload=payload,
                trace_jsonl_path=trace_path,
            )

            self.assertEqual(written_path, trace_path)
            lines = trace_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            entry = json.loads(lines[0])
            self.assertEqual(entry["schema_version"], traces.TRACE_SCHEMA_VERSION)
            self.assertEqual(entry["run_id"], "run-123")
            self.assertEqual(entry["tool_name"], "tools/eval_style.py")
            self.assertTrue(entry["gate_outcomes"][0]["passed"])

    def test_append_is_jsonl_append_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            trace_path = Path(tmp) / "trace.jsonl"
            first = traces.build_eval_trace(
                run_id="run-a",
                tool_name="tools/eval_file_search.py",
                source_artifacts={"report_json": "a.json"},
                gate_outcomes=[{"name": "file_search", "passed": True, "detail": "ok"}],
                summary={"total": 1, "passed": 1, "failed": 0},
            )
            second = traces.build_eval_trace(
                run_id="run-b",
                tool_name="tools/eval_file_search.py",
                source_artifacts={"report_json": "b.json"},
                gate_outcomes=[{"name": "file_search", "passed": False, "detail": "bad"}],
                summary={"total": 1, "passed": 0, "failed": 1},
            )

            traces.append_eval_trace(trace_payload=first, trace_jsonl_path=trace_path)
            traces.append_eval_trace(trace_payload=second, trace_jsonl_path=trace_path)

            lines = trace_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            first_entry = json.loads(lines[0])
            second_entry = json.loads(lines[1])
            self.assertEqual(first_entry["run_id"], "run-a")
            self.assertEqual(second_entry["run_id"], "run-b")


if __name__ == "__main__":
    unittest.main()
