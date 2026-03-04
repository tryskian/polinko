import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class BuildEvidenceIndexTests(unittest.TestCase):
    def _run_index(self, root: Path, out_md: Path, out_json: Path) -> None:
        result = subprocess.run(
            [
                "python3",
                "tools/build_evidence_index.py",
                "--root",
                str(root),
                "--out-md",
                str(out_md),
                "--out-json",
                str(out_json),
            ],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_fail_records_default_open_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "raw_evidence"
            fail_dir = root / "FAIL"
            fail_dir.mkdir(parents=True)
            (root / "PASS").mkdir()
            (root / "MIXED").mkdir()
            (root / "INBOX").mkdir()

            fail_file = (
                fail_dir
                / "ocr-miss-chat-11111111-1111-4111-8111-111111111111-20260304-120000Z.md"
            )
            fail_file.write_text("OCR output was incorrect and guessed.", encoding="utf-8")

            out_md = Path(tmp) / "index.md"
            out_json = Path(tmp) / "index.json"
            self._run_index(root, out_md, out_json)

            records = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual(len(records), 1)
            record = records[0]
            self.assertEqual(record["outcome"], "FAIL")
            self.assertEqual(record["status"], "OPEN")
            self.assertEqual(record["action_taken"], "Pending")
            self.assertIn("recommended_action", record)

    def test_fail_auto_closes_when_later_pass_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "raw_evidence"
            pass_dir = root / "PASS"
            fail_dir = root / "FAIL"
            pass_dir.mkdir(parents=True)
            fail_dir.mkdir(parents=True)
            (root / "MIXED").mkdir()
            (root / "INBOX").mkdir()

            fail_file = (
                fail_dir
                / "case-a-chat-11111111-1111-4111-8111-111111111111-20260304-120000Z.md"
            )
            pass_file = (
                pass_dir
                / "case-a-chat-11111111-1111-4111-8111-111111111111-20260304-130000Z.md"
            )
            fail_file.write_text("Output incorrect. Try again.", encoding="utf-8")
            pass_file.write_text("Expected behavior observed.", encoding="utf-8")

            out_md = Path(tmp) / "index.md"
            out_json = Path(tmp) / "index.json"
            self._run_index(root, out_md, out_json)

            records = json.loads(out_json.read_text(encoding="utf-8"))
            fail_records = [r for r in records if r["outcome"] == "FAIL"]
            self.assertEqual(len(fail_records), 1)
            fail_record = fail_records[0]
            self.assertEqual(fail_record["status"], "CLOSED")
            self.assertIn("Validated by subsequent PASS evidence.", fail_record["action_taken"])
            self.assertTrue(fail_record["resolved_by"].endswith(pass_file.name))

    def test_triage_override_sets_action_taken(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "raw_evidence"
            fail_dir = root / "FAIL"
            fail_dir.mkdir(parents=True)
            (root / "PASS").mkdir()
            (root / "MIXED").mkdir()
            (root / "INBOX").mkdir()

            fail_file = (
                fail_dir
                / "case-b-chat-22222222-2222-4222-8222-222222222222-20260304-120000Z.md"
            )
            fail_file.write_text("no new image evidence", encoding="utf-8")

            overrides = {
                "files": {
                    fail_file.name: {
                        "action_taken": "Adjusted OCR follow-up trigger and added regression case.",
                        "status": "OPEN",
                        "notes": "Awaiting next scheduled eval run.",
                    }
                }
            }
            (root / "triage_overrides.json").write_text(
                json.dumps(overrides, indent=2),
                encoding="utf-8",
            )

            out_md = Path(tmp) / "index.md"
            out_json = Path(tmp) / "index.json"
            self._run_index(root, out_md, out_json)

            records = json.loads(out_json.read_text(encoding="utf-8"))
            record = records[0]
            self.assertEqual(record["outcome"], "FAIL")
            self.assertEqual(
                record["action_taken"],
                "Adjusted OCR follow-up trigger and added regression case.",
            )
            self.assertEqual(record["status"], "OPEN")
            self.assertEqual(record["triage_notes"], "Awaiting next scheduled eval run.")


if __name__ == "__main__":
    unittest.main()
