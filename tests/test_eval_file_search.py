import json
import tempfile
import unittest
from pathlib import Path

from tools.eval_file_search import _load_cases


class EvalFileSearchCaseContractTests(unittest.TestCase):
    def _write_cases(self, payload: dict) -> Path:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        try:
            json.dump(payload, tmp)
            tmp.flush()
            return Path(tmp.name)
        finally:
            tmp.close()

    def test_load_cases_accepts_strict_case_shape(self) -> None:
        path = self._write_cases(
            {
                "cases": [
                    {
                        "id": "c1",
                        "seed_method": "ocr",
                        "source_type": "ocr",
                        "source_name": "c1.txt",
                        "seed_text": "signal chain anchor",
                        "query": "what anchors the chain?",
                        "must_include": ["signal chain"],
                    }
                ]
            }
        )
        self.addCleanup(path.unlink)
        cases = _load_cases(path)
        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0]["id"], "c1")
        self.assertNotIn("optional", cases[0])

    def test_load_cases_rejects_optional_true(self) -> None:
        path = self._write_cases(
            {
                "cases": [
                    {
                        "id": "c1",
                        "seed_method": "ocr",
                        "source_type": "ocr",
                        "source_name": "c1.txt",
                        "seed_text": "signal chain anchor",
                        "query": "what anchors the chain?",
                        "must_include": ["signal chain"],
                        "optional": True,
                    }
                ]
            }
        )
        self.addCleanup(path.unlink)
        with self.assertRaises(RuntimeError) as ctx:
            _load_cases(path)
        self.assertIn("deprecated field 'optional=true'", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
