from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import check_openai_eval_dataset_export as checker
from tools import export_openai_eval_dataset as exporter


def _valid_row() -> dict[str, object]:
    trace = {
        "schema_version": "polinko.eval_trace.v1",
        "trace_id": "trace-a",
        "trace_type": "eval_run",
        "generated_at": 1710000000,
        "run_id": "run-a",
        "tool_name": "tools/eval_style.py",
        "model_metadata": {},
        "source_artifacts": {},
        "gate_outcomes": [{"name": "style", "passed": True, "detail": "ok"}],
        "summary": {},
        "metadata": {},
    }
    return exporter.map_trace_to_dataset_row(trace)


class CheckOpenAIEvalDatasetExportTests(unittest.TestCase):
    def test_validate_export_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "dataset.jsonl"
            item_schema = Path(tmp) / "item_schema.json"
            dataset.write_text(json.dumps(_valid_row()) + "\n", encoding="utf-8")
            item_schema.write_text(
                json.dumps(exporter.build_item_schema(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = checker.validate_export(
                dataset_jsonl=dataset,
                item_schema_json=item_schema,
                min_rows=1,
            )
            self.assertTrue(result.ok)
            self.assertEqual(result.row_count, 1)
            self.assertEqual(result.errors, [])

    def test_validate_export_rejects_bad_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            row = _valid_row()
            row["sample"]["metrics"]["total"] = 99
            dataset = Path(tmp) / "dataset.jsonl"
            item_schema = Path(tmp) / "item_schema.json"
            dataset.write_text(json.dumps(row) + "\n", encoding="utf-8")
            item_schema.write_text(
                json.dumps(exporter.build_item_schema(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = checker.validate_export(
                dataset_jsonl=dataset,
                item_schema_json=item_schema,
                min_rows=1,
            )
            self.assertFalse(result.ok)
            joined = "\n".join(result.errors)
            self.assertIn("sample.metrics.total must equal gate_outcomes length", joined)


if __name__ == "__main__":
    unittest.main()
