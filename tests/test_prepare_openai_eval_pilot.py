from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import prepare_openai_eval_pilot as pilot


class PrepareOpenAIEvalPilotTests(unittest.TestCase):
    def test_build_eval_payload_uses_custom_item_schema_and_string_check(self) -> None:
        schema = {
            "type": "object",
            "properties": {"item": {"type": "object"}, "sample": {"type": "object"}},
            "required": ["item", "sample"],
        }
        payload = pilot.build_eval_create_payload(
            eval_name="My Eval",
            item_schema=schema,
        )

        self.assertEqual(payload["name"], "My Eval")
        self.assertEqual(payload["data_source_config"]["type"], "custom")
        self.assertEqual(payload["data_source_config"]["item_schema"], schema)
        self.assertTrue(payload["data_source_config"]["include_sample_schema"])
        self.assertEqual(payload["testing_criteria"][0]["type"], "string_check")
        self.assertEqual(
            payload["testing_criteria"][0]["reference"], "{{ item.summary.outcome }}"
        )

    def test_build_run_payload_uses_template_and_file_id(self) -> None:
        payload = pilot.build_run_create_payload(
            run_name="My Run",
            model="gpt-4.1-mini",
            file_id="file-123",
        )

        self.assertEqual(payload["name"], "My Run")
        self.assertEqual(payload["data_source"]["type"], "responses")
        self.assertEqual(payload["data_source"]["model"], "gpt-4.1-mini")
        self.assertEqual(payload["data_source"]["source"]["id"], "file-123")
        template = payload["data_source"]["input_messages"]["template"]
        self.assertEqual(len(template), 2)
        self.assertEqual(template[0]["role"], "developer")
        self.assertEqual(template[1]["role"], "user")

    def test_run_prepare_prepare_only_writes_payload_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "dataset.jsonl"
            item_schema = root / "item_schema.json"
            eval_payload_path = root / "eval_payload.json"
            run_payload_path = root / "run_payload.json"

            dataset.write_text(
                json.dumps({"item": {"x": 1}, "sample": {"output_text": "pass"}}) + "\n",
                encoding="utf-8",
            )
            item_schema.write_text(
                json.dumps(
                    {
                        "type": "object",
                        "properties": {
                            "item": {"type": "object"},
                            "sample": {"type": "object"},
                        },
                        "required": ["item", "sample"],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            result = pilot.run_prepare(
                dataset_jsonl=dataset,
                item_schema_json=item_schema,
                eval_payload_json=eval_payload_path,
                run_payload_json=run_payload_path,
                eval_name="Pilot Eval",
                run_name="Pilot Run",
                model="gpt-4.1-mini",
                file_id="",
                eval_id="",
                execute=False,
                upload_dataset=False,
                api_key_env="OPENAI_API_KEY",
                base_url="https://api.openai.com/v1",
            )

            self.assertTrue(eval_payload_path.exists())
            self.assertTrue(run_payload_path.exists())
            self.assertEqual(result.file_id, "")
            self.assertEqual(result.eval_id, "")
            self.assertEqual(result.run_id, "")

            run_payload = json.loads(run_payload_path.read_text(encoding="utf-8"))
            self.assertEqual(run_payload["data_source"]["source"]["id"], "file-REPLACE_ME")


if __name__ == "__main__":
    unittest.main()

