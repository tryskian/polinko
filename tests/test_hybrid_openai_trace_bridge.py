from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import hybrid_openai_trace_bridge as bridge


def _source_trace() -> dict[str, object]:
    return {
        "schema_version": "polinko.eval_trace.v1",
        "trace_id": "trace-abc123",
        "trace_type": "eval_run",
        "generated_at": 1710000000,
        "run_id": "run-001",
        "tool_name": "tools/eval_style.py",
        "model_metadata": {"judge_model": "gpt-4.1-mini"},
        "source_artifacts": {"report_json": "eval_reports/style-001.json"},
        "gate_outcomes": [
            {"name": "style_strict", "passed": True, "detail": "ok"},
            {"name": "file_search", "passed": True, "detail": "ok"},
            {"name": "clip_readiness_sequence", "passed": False, "detail": "delta low"},
        ],
        "summary": {"overall_ready": False},
        "metadata": {"reports_dir": "eval_reports"},
    }


class HybridOpenAITraceBridgeTests(unittest.TestCase):
    def test_mapping_is_deterministic_for_identical_input(self) -> None:
        source = _source_trace()
        first = bridge.map_trace_to_openai_preview(source)
        second = bridge.map_trace_to_openai_preview(source)

        self.assertEqual(first, second)
        self.assertEqual(
            first["schema_version"],
            "polinko.hybrid_openai_trace_bridge.v1",
        )
        self.assertEqual(first["source_trace_id"], "trace-abc123")
        self.assertEqual(
            first["openai_trace"]["gate_summary"],
            {
                "total": 3,
                "passed": 2,
                "failed": 1,
                "pass_rate": 0.666667,
            },
        )

    def test_run_bridge_disabled_does_not_write_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source_path = Path(tmp) / "source.jsonl"
            output_path = Path(tmp) / "output.jsonl"
            source_path.write_text(json.dumps(_source_trace()) + "\n", encoding="utf-8")

            result = bridge.run_bridge(
                source_jsonl=source_path,
                output_jsonl=output_path,
                enabled=False,
            )

            self.assertFalse(result.enabled)
            self.assertEqual(result.source_count, 1)
            self.assertEqual(result.written_count, 0)
            self.assertFalse(output_path.exists())

    def test_run_bridge_enabled_appends_transformed_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source_path = Path(tmp) / "source.jsonl"
            output_path = Path(tmp) / "output.jsonl"
            rows = [_source_trace(), _source_trace()]
            source_path.write_text(
                "\n".join(json.dumps(item) for item in rows) + "\n",
                encoding="utf-8",
            )

            result = bridge.run_bridge(
                source_jsonl=source_path,
                output_jsonl=output_path,
                enabled=True,
            )

            self.assertTrue(result.enabled)
            self.assertEqual(result.source_count, 2)
            self.assertEqual(result.written_count, 2)
            lines = output_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            first = json.loads(lines[0])
            self.assertIn("openai_trace", first)
            self.assertIn("openai_grader_preview", first)


if __name__ == "__main__":
    unittest.main()
