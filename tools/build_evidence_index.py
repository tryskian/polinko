from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHAT_ID_RE = re.compile(r"chat-([0-9a-fA-F-]{36})")
STAMP_RE = re.compile(r"-(\d{8}-\d{6}Z)(?:\.|$)")
MEMORY_SCOPE_RE = re.compile(r'"memory_scope"\s*:\s*"(global|session)"', re.IGNORECASE)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_stamp(filename: str) -> str | None:
    match = STAMP_RE.search(filename)
    if not match:
        return None
    raw = match.group(1)
    try:
        dt = datetime.strptime(raw, "%Y%m%d-%H%M%SZ").replace(tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None


def _extract_chat_id(filename: str) -> str | None:
    match = CHAT_ID_RE.search(filename)
    return match.group(1) if match else None


def _content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out: list[str] = []
        for item in content:
            text = _content_to_text(item)
            if text:
                out.append(text)
        return "\n".join(out)
    if isinstance(content, dict):
        if "text" in content:
            return _content_to_text(content.get("text"))
        if "parts" in content:
            return _content_to_text(content.get("parts"))
        if "content" in content:
            return _content_to_text(content.get("content"))
        if "value" in content:
            return _content_to_text(content.get("value"))
    return ""


def _extract_turns_from_messages(messages: list[dict[str, Any]]) -> list[tuple[str, str]]:
    turns: list[tuple[str, str]] = []
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role")
        if not isinstance(role, str):
            role = ""
        text = _content_to_text(msg.get("content") or msg.get("text") or msg.get("message")).strip()
        if role and text:
            turns.append((role.lower(), text))
    return turns


def _extract_turns_from_mapping(mapping: dict[str, Any]) -> list[tuple[str, str]]:
    rows: list[tuple[float, int, str, str]] = []
    seq = 0
    for _, node in mapping.items():
        if not isinstance(node, dict):
            continue
        message = node.get("message")
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        if not isinstance(role, str):
            author = message.get("author")
            role = author.get("role") if isinstance(author, dict) else None
        if not isinstance(role, str):
            continue
        text = _content_to_text(message.get("content")).strip()
        if not text:
            continue
        create_time = message.get("create_time")
        try:
            ts = float(create_time) if create_time is not None else 0.0
        except (TypeError, ValueError):
            ts = 0.0
        rows.append((ts, seq, role.lower(), text))
        seq += 1
    rows.sort(key=lambda x: (x[0], x[1]))
    return [(role, text) for _, _, role, text in rows]


def _extract_turns_from_json(path: Path) -> list[tuple[str, str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    candidates: list[dict[str, Any]] = []
    if isinstance(payload, dict):
        candidates = [payload]
    elif isinstance(payload, list):
        candidates = [x for x in payload if isinstance(x, dict)]

    turns: list[tuple[str, str]] = []
    for conv in candidates:
        messages = conv.get("messages")
        if isinstance(messages, list):
            turns.extend(_extract_turns_from_messages(messages))
            continue
        mapping = conv.get("mapping")
        if isinstance(mapping, dict):
            turns.extend(_extract_turns_from_mapping(mapping))
            continue
    return turns


def _extract_memory_scope(raw_text: str) -> str | None:
    matches = MEMORY_SCOPE_RE.findall(raw_text)
    if not matches:
        return None
    return matches[-1].lower()


def _compact(text: str, limit: int = 260) -> str:
    one = re.sub(r"\s+", " ", text).strip()
    if len(one) <= limit:
        return one
    return one[: limit - 1].rstrip() + "…"


def _infer_reason_and_action(outcome: str, text: str) -> tuple[str, str]:
    lower = text.lower()
    if outcome == "PASS":
        return (
            "Expected behavior observed under current constraints.",
            "Keep as a positive control; reuse as calibration sample.",
        )
    if outcome == "FAIL":
        if "no new image evidence" in lower or "attach a new image" in lower:
            return (
                "OCR follow-up guard triggered on a non-OCR conversational turn.",
                "Narrow follow-up detection to explicit OCR-retry intent.",
            )
        if "http 404" in lower:
            return (
                "Client/server path mismatch returned 404.",
                "Verify endpoint wiring and base URL configuration.",
            )
        if "incorrect" in lower or "try again" in lower or "you just guessed" in lower:
            return (
                "OCR output drifted into repeated low-confidence guesses.",
                "Prefer uncertainty handling: ask for tighter crop instead of hard guess.",
            )
        if "tone" in lower or "arrogant" in lower or "dismiss" in lower:
            return (
                "Style/tone deviated from target collaborative register.",
                "Add this sample to style eval as a regression guard.",
            )
        return (
            "Observed behavior did not match expected output.",
            "Record as regression and attach one reproducible repro step.",
        )
    return (
        "Mixed signal: partial success with notable deviation.",
        "Split into one PASS control and one FAIL repro artifact.",
    )


@dataclass
class EvidenceRecord:
    evidence_id: str
    outcome: str
    file: str
    source_type: str
    chat_id: str | None
    timestamp_utc: str | None
    memory_scope: str | None
    failure_reason: str
    action: str
    preview: str


def _scan_bucket(bucket_dir: Path, bucket: str) -> list[EvidenceRecord]:
    records: list[EvidenceRecord] = []
    if not bucket_dir.exists():
        return records

    files = sorted(
        [p for p in bucket_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".json", ".md", ".txt"}],
        key=lambda p: p.name.lower(),
    )

    for idx, path in enumerate(files, start=1):
        source_type = path.suffix.lower().lstrip(".")
        if path.suffix.lower() == ".json":
            turns = _extract_turns_from_json(path)
            raw_text = (
                "\n\n".join(f"{role}: {text}" for role, text in turns)
                if turns
                else path.read_text(encoding="utf-8", errors="replace")
            )
        else:
            raw_text = path.read_text(encoding="utf-8", errors="replace")

        reason, action = _infer_reason_and_action(bucket, raw_text)
        records.append(
            EvidenceRecord(
                evidence_id=f"{bucket[:1]}-{idx:03d}",
                outcome=bucket,
                file=str(path),
                source_type=source_type,
                chat_id=_extract_chat_id(path.name),
                timestamp_utc=_parse_stamp(path.name),
                memory_scope=_extract_memory_scope(raw_text),
                failure_reason=reason,
                action=action,
                preview=_compact(raw_text),
            )
        )

    return records


def _render_markdown(records: list[EvidenceRecord]) -> str:
    totals = {"PASS": 0, "FAIL": 0, "MIXED": 0, "INBOX": 0}
    for record in records:
        totals[record.outcome] = totals.get(record.outcome, 0) + 1

    lines: list[str] = []
    lines.append("# Evidence Intake Index (Auto-Generated)")
    lines.append("")
    lines.append(f"Generated: `{_now_iso()}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- PASS: {totals['PASS']}")
    lines.append(f"- FAIL: {totals['FAIL']}")
    lines.append(f"- MIXED: {totals['MIXED']}")
    lines.append(f"- INBOX: {totals['INBOX']}")
    lines.append("")

    for bucket in ("FAIL", "MIXED", "PASS", "INBOX"):
        group = [r for r in records if r.outcome == bucket]
        if not group:
            continue
        lines.append(f"## {bucket}")
        lines.append("")
        for record in group:
            lines.append(f"### {record.evidence_id} — {Path(record.file).name}")
            lines.append("")
            lines.append(f"- Outcome: {record.outcome}")
            lines.append(f"- Source Type: `{record.source_type}`")
            lines.append(f"- File: `{record.file}`")
            if record.chat_id:
                lines.append(f"- Chat ID: `{record.chat_id}`")
            if record.timestamp_utc:
                lines.append(f"- Timestamp (UTC): `{record.timestamp_utc}`")
            if record.memory_scope:
                lines.append(f"- Memory Scope Seen: `{record.memory_scope}`")
            lines.append(f"- Failure Reason: {record.failure_reason}")
            lines.append(f"- Action: {record.action}")
            lines.append(f"- Preview: {record.preview}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an evidence intake index from raw evidence files.")
    parser.add_argument(
        "--root",
        default="docs/portfolio/raw_evidence",
        help="Root folder containing PASS/FAIL/MIXED/INBOX buckets.",
    )
    parser.add_argument(
        "--out-md",
        default="docs/portfolio/raw_evidence/index.md",
        help="Output markdown path.",
    )
    parser.add_argument(
        "--out-json",
        default="docs/portfolio/raw_evidence/index.json",
        help="Output JSON path.",
    )
    args = parser.parse_args()

    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)

    records: list[EvidenceRecord] = []
    for bucket in ("PASS", "FAIL", "MIXED", "INBOX"):
        bucket_dir = root / bucket
        bucket_dir.mkdir(parents=True, exist_ok=True)
        records.extend(_scan_bucket(bucket_dir, bucket))

    records.sort(
        key=lambda record: (record.timestamp_utc or "", Path(record.file).name.lower()),
        reverse=True,
    )

    out_md = Path(args.out_md)
    out_json = Path(args.out_json)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)

    out_md.write_text(_render_markdown(records), encoding="utf-8")
    out_json.write_text(
        json.dumps([asdict(record) for record in records], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Indexed {len(records)} evidence file(s).")
    print(f"Markdown: {out_md}")
    print(f"JSON: {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
