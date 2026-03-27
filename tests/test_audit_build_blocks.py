import json
import tempfile
import unittest
from pathlib import Path

import tools.audit_build_blocks as audit_build_blocks


class EvalCaseSchemaAuditTests(unittest.TestCase):
    def test_collect_deprecated_keys_finds_nested_optional(self) -> None:
        payload = {
            "cases": [
                {"id": "c1", "optional": False},
                {"id": "c2", "nested": {"optional": True}},
            ]
        }
        hits = audit_build_blocks._collect_deprecated_keys(payload)
        self.assertIn("$.cases[0].optional", hits)
        self.assertIn("$.cases[1].nested.optional", hits)

    def test_check_eval_case_schema_legacy_fields_passes_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs_dir = root / "docs"
            docs_dir.mkdir(parents=True, exist_ok=True)
            (docs_dir / "file_search_eval_cases.json").write_text(
                json.dumps({"cases": [{"id": "c1", "query": "q", "seed_text": "t"}]}),
                encoding="utf-8",
            )
            self._with_repo_root(root)
            result = audit_build_blocks.check_eval_case_schema_legacy_fields()
            self.assertTrue(result.ok)
            self.assertIn("eval case files clean", result.details)

    def test_check_eval_case_schema_legacy_fields_fails_on_optional_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs_dir = root / "docs"
            docs_dir.mkdir(parents=True, exist_ok=True)
            (docs_dir / "file_search_eval_cases.json").write_text(
                json.dumps(
                    {
                        "cases": [
                            {
                                "id": "c1",
                                "query": "q",
                                "seed_text": "t",
                                "optional": False,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            self._with_repo_root(root)
            result = audit_build_blocks.check_eval_case_schema_legacy_fields()
            self.assertFalse(result.ok)
            self.assertIn("deprecated keys:", result.details)
            self.assertIn("docs/file_search_eval_cases.json", result.details)

    def _with_repo_root(self, root: Path) -> None:
        original_root = audit_build_blocks.REPO_ROOT
        self.addCleanup(setattr, audit_build_blocks, "REPO_ROOT", original_root)
        audit_build_blocks.REPO_ROOT = root


if __name__ == "__main__":
    unittest.main()
