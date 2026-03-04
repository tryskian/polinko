from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SECTION_ID_RE = re.compile(r"^###\s+(S\d-\d+)\s*$")
FIELD_RE = re.compile(r"^- ([^:]+):\s*(.*)$")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Finding:
    level: str
    scope: str
    item: str
    field: str
    message: str


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    return False


def _audit_evidence_index(index_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not index_path.exists():
        findings.append(
            Finding(
                level="ERROR",
                scope="evidence_index",
                item=str(index_path),
                field="file",
                message="Evidence index file is missing.",
            )
        )
        return findings

    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception as exc:
        findings.append(
            Finding(
                level="ERROR",
                scope="evidence_index",
                item=str(index_path),
                field="json",
                message=f"Failed to parse index JSON: {exc}",
            )
        )
        return findings

    if not isinstance(payload, list):
        findings.append(
            Finding(
                level="ERROR",
                scope="evidence_index",
                item=str(index_path),
                field="json",
                message="Index root must be a JSON array.",
            )
        )
        return findings

    required_common = [
        "evidence_id",
        "outcome",
        "file",
        "source_type",
        "artifact_sha256",
        "artifact_bytes",
        "test_type",
        "failure_reason",
        "recommended_action",
        "action_taken",
        "status",
        "preview",
    ]
    required_fail = ["chat_id", "timestamp_utc"]

    valid_status = {"OPEN", "CLOSED"}
    for record in payload:
        if not isinstance(record, dict):
            findings.append(
                Finding(
                    level="ERROR",
                    scope="evidence_record",
                    item="<non-dict>",
                    field="record",
                    message="Record is not an object.",
                )
            )
            continue

        evidence_id = str(record.get("evidence_id") or "<unknown>")
        for field in required_common:
            if _is_blank(record.get(field)):
                findings.append(
                    Finding(
                        level="ERROR",
                        scope="evidence_record",
                        item=evidence_id,
                        field=field,
                        message="Required metadata is missing.",
                    )
                )

        outcome = str(record.get("outcome") or "")
        if outcome == "FAIL":
            for field in required_fail:
                if _is_blank(record.get(field)):
                    findings.append(
                        Finding(
                            level="WARN",
                            scope="evidence_record",
                            item=evidence_id,
                            field=field,
                            message="FAIL record should include this metadata for traceability.",
                        )
                    )

        status = str(record.get("status") or "")
        if status and status not in valid_status:
            findings.append(
                Finding(
                    level="ERROR",
                    scope="evidence_record",
                    item=evidence_id,
                    field="status",
                    message=f"Unsupported status '{status}'. Expected one of {sorted(valid_status)}.",
                )
            )

        file_path = record.get("file")
        if isinstance(file_path, str) and file_path.strip():
            path = Path(file_path)
            if not path.exists():
                findings.append(
                    Finding(
                        level="WARN",
                        scope="evidence_record",
                        item=evidence_id,
                        field="file",
                        message=f"Artifact path does not exist on disk: {file_path}",
                    )
                )

    return findings


def _audit_evidence_log(log_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not log_path.exists():
        findings.append(
            Finding(
                level="WARN",
                scope="evidence_log",
                item=str(log_path),
                field="file",
                message="Evidence log markdown is missing.",
            )
        )
        return findings

    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    sections: dict[str, dict[str, str]] = {}
    current: str | None = None
    for line in lines:
        section_match = SECTION_ID_RE.match(line.strip())
        if section_match:
            current = section_match.group(1)
            sections[current] = {}
            continue
        if current is None:
            continue
        field_match = FIELD_RE.match(line.strip())
        if field_match:
            sections[current][field_match.group(1).strip()] = field_match.group(2).strip()

    required_fields = [
        "Section",
        "Claim",
        "Mechanism",
        "Build Function / Surface",
        "Evidence Artifact",
        "APA Key",
        "Status",
    ]
    for section_id, fields in sections.items():
        for required in required_fields:
            if _is_blank(fields.get(required)):
                findings.append(
                    Finding(
                        level="ERROR",
                        scope="evidence_log",
                        item=section_id,
                        field=required,
                        message="Required section metadata is missing.",
                    )
                )
        apa_key = fields.get("APA Key", "")
        if isinstance(apa_key, str) and apa_key.strip().upper() == "`TBD`":
            findings.append(
                Finding(
                    level="WARN",
                    scope="evidence_log",
                    item=section_id,
                    field="APA Key",
                    message="Citation key still marked TBD.",
                )
            )

    return findings


def _render_markdown(findings: list[Finding]) -> str:
    errors = sum(1 for f in findings if f.level == "ERROR")
    warns = sum(1 for f in findings if f.level == "WARN")
    lines = [
        "# Portfolio Metadata Audit",
        "",
        f"Generated: `{_now_iso()}`",
        "",
        "## Summary",
        "",
        f"- Errors: {errors}",
        f"- Warnings: {warns}",
        "",
    ]
    if not findings:
        lines.extend(["No findings.", ""])
        return "\n".join(lines)

    lines.extend(["## Findings", ""])
    for finding in findings:
        lines.append(
            f"- [{finding.level}] {finding.scope} `{finding.item}` field `{finding.field}`: {finding.message}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit metadata completeness for portfolio evidence/docs.")
    parser.add_argument(
        "--index-json",
        default="docs/portfolio/raw_evidence/index.json",
        help="Path to evidence index JSON.",
    )
    parser.add_argument(
        "--evidence-log",
        default="docs/portfolio/03_evidence_log.md",
        help="Path to evidence log markdown.",
    )
    parser.add_argument(
        "--out-json",
        default="docs/portfolio/raw_evidence/metadata_audit.json",
        help="Path for machine-readable audit output.",
    )
    parser.add_argument(
        "--out-md",
        default="docs/portfolio/raw_evidence/metadata_audit.md",
        help="Path for markdown audit summary.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when any ERROR findings exist.",
    )
    args = parser.parse_args()

    findings = _audit_evidence_index(Path(args.index_json))
    findings.extend(_audit_evidence_log(Path(args.evidence_log)))

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps([asdict(f) for f in findings], indent=2), encoding="utf-8")
    out_md.write_text(_render_markdown(findings), encoding="utf-8")

    errors = sum(1 for f in findings if f.level == "ERROR")
    warns = sum(1 for f in findings if f.level == "WARN")
    print(f"Metadata audit complete. errors={errors} warnings={warns}")
    print(f"JSON: {out_json}")
    print(f"Markdown: {out_md}")

    if args.strict and errors > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
