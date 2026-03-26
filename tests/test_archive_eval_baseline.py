from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.archive_eval_baseline import archive_eval_baseline


class ArchiveEvalBaselineTests(unittest.TestCase):
    def test_archives_raw_evidence_and_eval_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_root = root / "docs" / "portfolio" / "raw_evidence"
            reports_root = root / "eval_reports"

            (raw_root / "PASS").mkdir(parents=True, exist_ok=True)
            (raw_root / "FAIL").mkdir(parents=True, exist_ok=True)
            (raw_root / "MIXED").mkdir(parents=True, exist_ok=True)
            (raw_root / "INBOX").mkdir(parents=True, exist_ok=True)
            (raw_root / "PASS" / "evidence-pass.md").write_text("ok", encoding="utf-8")
            (raw_root / "FAIL" / "legacy.json").write_text("{}", encoding="utf-8")
            (raw_root / "index.json").write_text("{}", encoding="utf-8")
            (raw_root / "metadata_audit.md").write_text("# audit\n", encoding="utf-8")
            (raw_root / "triage_overrides.json").write_text("{}", encoding="utf-8")
            (raw_root / "triage_overrides.example.json").write_text("{}", encoding="utf-8")

            reports_root.mkdir(parents=True, exist_ok=True)
            (reports_root / "retrieval-1.json").write_text("{}", encoding="utf-8")
            (reports_root / "retrieval-1.log").write_text("ok\n", encoding="utf-8")
            (reports_root / "archive").mkdir(parents=True, exist_ok=True)
            (reports_root / "archive" / "keep.txt").write_text("keep\n", encoding="utf-8")

            result = archive_eval_baseline(
                raw_evidence_root=raw_root,
                eval_reports_root=reports_root,
                run_id="20260326-170000",
            )

            self.assertEqual(result.moved_raw_count, 8)
            self.assertEqual(result.moved_report_count, 2)

            self.assertFalse((raw_root / "PASS" / "evidence-pass.md").exists())
            self.assertFalse((raw_root / "FAIL" / "legacy.json").exists())
            self.assertFalse((raw_root / "index.json").exists())
            self.assertFalse((raw_root / "metadata_audit.md").exists())
            self.assertFalse((raw_root / "MIXED").exists())
            self.assertFalse((raw_root / "INBOX").exists())
            self.assertFalse((raw_root / "triage_overrides.json").exists())
            self.assertFalse((raw_root / "triage_overrides.example.json").exists())

            archived_raw = raw_root / "archive" / "baseline-reset-20260326-170000"
            self.assertTrue((archived_raw / "PASS" / "evidence-pass.md").exists())
            self.assertTrue((archived_raw / "FAIL" / "legacy.json").exists())
            self.assertTrue((archived_raw / "index.json").exists())
            self.assertTrue((archived_raw / "metadata_audit.md").exists())
            self.assertTrue((archived_raw / "MIXED").exists())
            self.assertTrue((archived_raw / "INBOX").exists())
            self.assertTrue((archived_raw / "triage_overrides.json").exists())
            self.assertTrue((archived_raw / "triage_overrides.example.json").exists())
            self.assertFalse((raw_root / "PASS").exists())
            self.assertFalse((raw_root / "FAIL").exists())

            self.assertFalse((reports_root / "retrieval-1.json").exists())
            self.assertFalse((reports_root / "retrieval-1.log").exists())
            self.assertTrue((reports_root / "archive" / "keep.txt").exists())
            archived_reports = reports_root / "archive" / "baseline-reset-20260326-170000"
            self.assertTrue((archived_reports / "retrieval-1.json").exists())
            self.assertTrue((archived_reports / "retrieval-1.log").exists())

    def test_noop_when_nothing_to_move(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_root = root / "docs" / "portfolio" / "raw_evidence"
            reports_root = root / "eval_reports"
            raw_root.mkdir(parents=True, exist_ok=True)
            (raw_root / "archive").mkdir(parents=True, exist_ok=True)
            reports_root.mkdir(parents=True, exist_ok=True)
            (reports_root / "archive").mkdir(parents=True, exist_ok=True)

            result = archive_eval_baseline(
                raw_evidence_root=raw_root,
                eval_reports_root=reports_root,
                run_id="20260326-170001",
            )

            self.assertEqual(result.moved_raw_count, 0)
            self.assertEqual(result.moved_report_count, 0)
            self.assertFalse((raw_root / "archive" / "baseline-reset-20260326-170001").exists())
            self.assertFalse((reports_root / "archive" / "baseline-reset-20260326-170001").exists())


if __name__ == "__main__":
    unittest.main()
