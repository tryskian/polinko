from __future__ import annotations

import argparse
import hashlib
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


def _hash_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _extract_first_str(payload: Any, keys: set[str]) -> str | None:
    stack: list[Any] = [payload]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, value in current.items():
                if isinstance(key, str) and key in keys and isinstance(value, str) and value.strip():
                    return value.strip()
                stack.append(value)
        elif isinstance(current, list):
            stack.extend(current)
    return None


def _infer_test_type(path: Path, text: str) -> str:
    probe = f"{path.name.lower()} {text.lower()}"
    if "ocr" in probe or "transcribe" in probe:
        return "ocr"
    if "file_search" in probe or "file search" in probe:
        return "file-search"
    if "retrieval" in probe:
        return "retrieval"
    if "hallucination" in probe:
        return "hallucination"
    if "style" in probe:
        return "style"
    return "general"


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


def _default_status(outcome: str) -> str:
    if outcome == "PASS":
        return "CLOSED"
    if outcome in {"FAIL", "MIXED", "INBOX"}:
        return "OPEN"
    return "OPEN"


def _default_action_taken(outcome: str) -> str:
    if outcome == "PASS":
        return "Not required (pass control)."
    if outcome == "FAIL":
        return "Pending"
    if outcome == "MIXED":
        return "Pending split into PASS/FAIL artifacts."
    return "Pending triage."


def _parse_iso_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


@dataclass
class EvidenceRecord:
    evidence_id: str
    outcome: str
    file: str
    source_type: str
    artifact_sha256: str
    artifact_bytes: int
    test_type: str
    chat_id: str | None
    timestamp_utc: str | None
    model: str | None
    response_id: str | None
    memory_scope: str | None
    failure_reason: str
    recommended_action: str
    action_taken: str
    status: str
    resolved_by: str | None
    triage_notes: str | None
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
        file_bytes = path.read_bytes()
        model: str | None = None
        response_id: str | None = None
        if path.suffix.lower() == ".json":
            payload: Any
            try:
                payload = json.loads(file_bytes.decode("utf-8", errors="replace"))
            except Exception:
                payload = None

            turns = _extract_turns_from_json(path)
            raw_text = (
                "\n\n".join(f"{role}: {text}" for role, text in turns)
                if turns
                else path.read_text(encoding="utf-8", errors="replace")
            )
            if payload is not None:
                model = _extract_first_str(payload, {"model", "judge_model"})
                response_id = _extract_first_str(payload, {"response_id", "openai_response_id", "run_id"})
        else:
            raw_text = file_bytes.decode("utf-8", errors="replace")

        reason, action = _infer_reason_and_action(bucket, raw_text)
        records.append(
            EvidenceRecord(
                evidence_id=f"{bucket[:1]}-{idx:03d}",
                outcome=bucket,
                file=str(path),
                source_type=source_type,
                artifact_sha256=_hash_sha256(file_bytes),
                artifact_bytes=len(file_bytes),
                test_type=_infer_test_type(path, raw_text),
                chat_id=_extract_chat_id(path.name),
                timestamp_utc=_parse_stamp(path.name),
                model=model,
                response_id=response_id,
                memory_scope=_extract_memory_scope(raw_text),
                failure_reason=reason,
                recommended_action=action,
                action_taken=_default_action_taken(bucket),
                status=_default_status(bucket),
                resolved_by=None,
                triage_notes=None,
                preview=_compact(raw_text),
            )
        )

    return records


def _load_triage_overrides(path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if not path.exists():
        return {}, {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}, {}

    raw_entries: list[tuple[str, dict[str, Any]]] = []
    if isinstance(payload, dict):
        files_obj = payload.get("files")
        if isinstance(files_obj, dict):
            for key, value in files_obj.items():
                if isinstance(key, str) and isinstance(value, dict):
                    raw_entries.append((key, value))
        else:
            for key, value in payload.items():
                if isinstance(key, str) and isinstance(value, dict):
                    raw_entries.append((key, value))
    elif isinstance(payload, list):
        for item in payload:
            if not isinstance(item, dict):
                continue
            file_key = item.get("file")
            if isinstance(file_key, str):
                raw_entries.append((file_key, item))

    by_exact: dict[str, dict[str, Any]] = {}
    by_basename: dict[str, dict[str, Any]] = {}
    for key, value in raw_entries:
        by_exact[key] = value
        by_basename[Path(key).name] = value
    return by_exact, by_basename


def _apply_triage_overrides(
    records: list[EvidenceRecord], by_exact: dict[str, dict[str, Any]], by_basename: dict[str, dict[str, Any]]
) -> None:
    for record in records:
        override = by_exact.get(record.file)
        if override is None:
            override = by_basename.get(Path(record.file).name)
        if override is None:
            continue

        recommended_action = override.get("recommended_action")
        if isinstance(recommended_action, str) and recommended_action.strip():
            record.recommended_action = recommended_action.strip()

        action_taken = override.get("action_taken")
        if isinstance(action_taken, str) and action_taken.strip():
            record.action_taken = action_taken.strip()

        status = override.get("status")
        if isinstance(status, str) and status.strip():
            record.status = status.strip().upper()

        resolved_by = override.get("resolved_by")
        if isinstance(resolved_by, str) and resolved_by.strip():
            record.resolved_by = resolved_by.strip()

        notes = override.get("notes")
        if isinstance(notes, str) and notes.strip():
            record.triage_notes = notes.strip()


def _auto_close_failures(records: list[EvidenceRecord]) -> None:
    passes_by_chat: dict[str, list[EvidenceRecord]] = {}
    for record in records:
        if record.outcome != "PASS" or not record.chat_id:
            continue
        passes_by_chat.setdefault(record.chat_id, []).append(record)

    for pass_records in passes_by_chat.values():
        pass_records.sort(key=lambda r: _parse_iso_utc(r.timestamp_utc) or datetime.min.replace(tzinfo=timezone.utc))

    for record in records:
        if record.outcome != "FAIL":
            continue
        if not record.chat_id:
            continue
        if record.status.upper() == "CLOSED":
            continue

        candidates = passes_by_chat.get(record.chat_id, [])
        if not candidates:
            continue

        fail_ts = _parse_iso_utc(record.timestamp_utc)
        resolved_with: EvidenceRecord | None = None
        for candidate in candidates:
            pass_ts = _parse_iso_utc(candidate.timestamp_utc)
            if fail_ts is None or pass_ts is None or pass_ts >= fail_ts:
                resolved_with = candidate
                break
        if resolved_with is None:
            continue

        record.status = "CLOSED"
        if record.action_taken in {"Pending", "Pending triage."}:
            record.action_taken = "Validated by subsequent PASS evidence."
        record.resolved_by = resolved_with.file


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
            lines.append(f"- Test Type: `{record.test_type}`")
            lines.append(f"- File: `{record.file}`")
            lines.append(f"- Artifact SHA256: `{record.artifact_sha256}`")
            lines.append(f"- Artifact Bytes: `{record.artifact_bytes}`")
            if record.chat_id:
                lines.append(f"- Chat ID: `{record.chat_id}`")
            if record.timestamp_utc:
                lines.append(f"- Timestamp (UTC): `{record.timestamp_utc}`")
            if record.model:
                lines.append(f"- Model Seen: `{record.model}`")
            if record.response_id:
                lines.append(f"- Response ID Seen: `{record.response_id}`")
            if record.memory_scope:
                lines.append(f"- Memory Scope Seen: `{record.memory_scope}`")
            lines.append(f"- Failure Reason: {record.failure_reason}")
            lines.append(f"- Recommended Action: {record.recommended_action}")
            lines.append(f"- Action Taken: {record.action_taken}")
            lines.append(f"- Status: `{record.status}`")
            if record.resolved_by:
                lines.append(f"- Resolved By: `{record.resolved_by}`")
            if record.triage_notes:
                lines.append(f"- Triage Notes: {record.triage_notes}")
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
    parser.add_argument(
        "--triage-overrides",
        default=None,
        help="Optional path to triage override JSON (defaults to <root>/triage_overrides.json).",
    )
    args = parser.parse_args()

    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    triage_overrides_path = (
        Path(args.triage_overrides) if args.triage_overrides else root / "triage_overrides.json"
    )

    records: list[EvidenceRecord] = []
    for bucket in ("PASS", "FAIL", "MIXED", "INBOX"):
        bucket_dir = root / bucket
        bucket_dir.mkdir(parents=True, exist_ok=True)
        records.extend(_scan_bucket(bucket_dir, bucket))

    by_exact, by_basename = _load_triage_overrides(triage_overrides_path)
    _apply_triage_overrides(records, by_exact, by_basename)
    _auto_close_failures(records)

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
    if triage_overrides_path.exists():
        print(f"Triage overrides: {triage_overrides_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
