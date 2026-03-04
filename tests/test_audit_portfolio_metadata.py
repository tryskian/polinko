import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class AuditPortfolioMetadataTests(unittest.TestCase):
    def _run_audit(
        self,
        index_json: Path,
        evidence_log: Path,
        out_json: Path,
        out_md: Path,
        strict: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        cmd = [
            "python3",
            "tools/audit_portfolio_metadata.py",
            "--index-json",
            str(index_json),
            "--evidence-log",
            str(evidence_log),
            "--out-json",
            str(out_json),
            "--out-md",
            str(out_md),
        ]
        if strict:
            cmd.append("--strict")
        return subprocess.run(
            cmd,
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_strict_passes_with_complete_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            artifact = base / "artifact.json"
            artifact.write_text('{"ok": true}', encoding="utf-8")

            index_json = base / "index.json"
            index_payload = [
                {
                    "evidence_id": "F-001",
                    "outcome": "FAIL",
                    "file": str(artifact),
                    "source_type": "json",
                    "artifact_sha256": "abc",
                    "artifact_bytes": 12,
                    "test_type": "ocr",
                    "chat_id": "11111111-1111-4111-8111-111111111111",
                    "timestamp_utc": "2026-03-04T12:00:00Z",
                    "model": None,
                    "response_id": None,
                    "memory_scope": "session",
                    "failure_reason": "Observed behavior did not match expected output.",
                    "recommended_action": "Add regression test.",
                    "action_taken": "Added regression test.",
                    "status": "OPEN",
                    "resolved_by": None,
                    "triage_notes": None,
                    "preview": "sample",
                }
            ]
            index_json.write_text(json.dumps(index_payload), encoding="utf-8")

            evidence_log = base / "evidence_log.md"
            evidence_log.write_text(
                "\n".join(
                    [
                        "# Evidence Log",
                        "### S1-01",
                        "- Section: Section 1",
                        "- Claim: Test claim",
                        "- Mechanism: Test mechanism",
                        "- Build Function / Surface: Test surface",
                        "- Evidence Artifact: Test artifact",
                        "- APA Key: key-1",
                        "- Status: Draft",
                    ]
                ),
                encoding="utf-8",
            )

            out_json = base / "audit.json"
            out_md = base / "audit.md"
            result = self._run_audit(index_json, evidence_log, out_json, out_md, strict=True)
            self.assertEqual(result.returncode, 0, msg=result.stderr)

            findings = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual(findings, [])

    def test_strict_fails_with_missing_required_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            artifact = base / "artifact.json"
            artifact.write_text('{"ok": true}', encoding="utf-8")

            index_json = base / "index.json"
            index_payload = [
                {
                    "evidence_id": "F-001",
                    "outcome": "FAIL",
                    "file": str(artifact),
                    "source_type": "json",
                    "artifact_sha256": "",
                    "artifact_bytes": 12,
                    "test_type": "ocr",
                    "chat_id": "11111111-1111-4111-8111-111111111111",
                    "timestamp_utc": "2026-03-04T12:00:00Z",
                    "model": None,
                    "response_id": None,
                    "memory_scope": "session",
                    "failure_reason": "Observed behavior did not match expected output.",
                    "recommended_action": "Add regression test.",
                    "action_taken": "Added regression test.",
                    "status": "OPEN",
                    "resolved_by": None,
                    "triage_notes": None,
                    "preview": "sample",
                }
            ]
            index_json.write_text(json.dumps(index_payload), encoding="utf-8")

            evidence_log = base / "evidence_log.md"
            evidence_log.write_text(
                "\n".join(
                    [
                        "# Evidence Log",
                        "### S1-01",
                        "- Section: Section 1",
                        "- Claim: Test claim",
                        "- Mechanism: Test mechanism",
                        "- Build Function / Surface: Test surface",
                        "- Evidence Artifact: Test artifact",
                        "- APA Key: key-1",
                        "- Status: Draft",
                    ]
                ),
                encoding="utf-8",
            )

            out_json = base / "audit.json"
            out_md = base / "audit.md"
            result = self._run_audit(index_json, evidence_log, out_json, out_md, strict=True)
            self.assertNotEqual(result.returncode, 0)

            findings = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertTrue(
                any(f["field"] == "artifact_sha256" and f["level"] == "ERROR" for f in findings),
                msg=str(findings),
            )


if __name__ == "__main__":
    unittest.main()
