from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import export_openai_eval_dataset as exporter


def _trace(*, trace_id: str, run_id: str, tool_name: str, passed: bool) -> dict[str, object]:
    return {
        "schema_version": "polinko.eval_trace.v1",
        "trace_id": trace_id,
        "trace_type": "eval_run",
        "generated_at": 1710000000,
        "run_id": run_id,
        "tool_name": tool_name,
        "model_metadata": {"judge_model": "gpt-4.1-mini"},
        "source_artifacts": {"report_json": "eval_reports/sample.json"},
        "gate_outcomes": [
            {"name": "gate_a", "passed": passed, "detail": "ok" if passed else "bad"}
        ],
        "summary": {"overall_ready": passed},
        "metadata": {"suite": "smoke"},
    }


class ExportOpenAIEvalDatasetTests(unittest.TestCase):
    def test_map_trace_to_dataset_row_sets_binary_outcome(self) -> None:
        row_pass = exporter.map_trace_to_dataset_row(
            _trace(
                trace_id="trace-pass",
                run_id="run-pass",
                tool_name="tools/eval_style.py",
                passed=True,
            )
        )
        row_fail = exporter.map_trace_to_dataset_row(
            _trace(
                trace_id="trace-fail",
                run_id="run-fail",
                tool_name="tools/eval_style.py",
                passed=False,
            )
        )

        self.assertEqual(row_pass["sample"]["overall"], "pass")
        self.assertIn("overall:pass", row_pass["sample"]["labels"])
        self.assertEqual(row_fail["sample"]["overall"], "fail")
        self.assertIn("overall:fail", row_fail["sample"]["labels"])

    def test_run_export_writes_dataset_and_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "trace.jsonl"
            output = Path(tmp) / "dataset.jsonl"
            schema = Path(tmp) / "item_schema.json"

            traces = [
                _trace(
                    trace_id="trace-1",
                    run_id="run-1",
                    tool_name="tools/eval_style.py",
                    passed=True,
                ),
                _trace(
                    trace_id="trace-2",
                    run_id="run-2",
                    tool_name="tools/eval_file_search.py",
                    passed=False,
                ),
            ]
            source.write_text(
                "\n".join(json.dumps(row) for row in traces) + "\n",
                encoding="utf-8",
            )

            result = exporter.run_export(
                source_jsonl=source,
                output_jsonl=output,
                item_schema_json=schema,
            )
            self.assertEqual(result.source_count, 2)
            self.assertEqual(result.selected_count, 2)
            self.assertEqual(result.written_count, 2)
            self.assertTrue(output.exists())
            self.assertTrue(schema.exists())

            dataset_rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(dataset_rows), 2)
            self.assertEqual(dataset_rows[0]["schema_version"], exporter.DATASET_SCHEMA_VERSION)

            schema_obj = json.loads(schema.read_text(encoding="utf-8"))
            self.assertEqual(schema_obj["type"], "object")
            self.assertIn("item", schema_obj["properties"])
            self.assertIn("sample", schema_obj["properties"])

    def test_run_export_supports_tool_filter_and_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "trace.jsonl"
            output = Path(tmp) / "dataset.jsonl"
            schema = Path(tmp) / "item_schema.json"

            traces = [
                _trace(
                    trace_id="trace-1",
                    run_id="run-1",
                    tool_name="tools/eval_style.py",
                    passed=True,
                ),
                _trace(
                    trace_id="trace-2",
                    run_id="run-2",
                    tool_name="tools/eval_file_search.py",
                    passed=False,
                ),
                _trace(
                    trace_id="trace-3",
                    run_id="run-3",
                    tool_name="tools/eval_file_search.py",
                    passed=True,
                ),
            ]
            source.write_text(
                "\n".join(json.dumps(row) for row in traces) + "\n",
                encoding="utf-8",
            )

            result = exporter.run_export(
                source_jsonl=source,
                output_jsonl=output,
                item_schema_json=schema,
                include_tools={"tools/eval_file_search.py"},
                limit=1,
            )
            self.assertEqual(result.source_count, 3)
            self.assertEqual(result.selected_count, 1)
            self.assertEqual(result.written_count, 1)

            dataset_rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(dataset_rows[0]["item"]["run_id"], "run-3")


if __name__ == "__main__":
    unittest.main()
