"""Build a bounded OCR generalization review slice from OCR-ready candidates."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from tools.build_ocr_cases_from_export import _classify_lane

CAMERA_NAME_RX = re.compile(r"(?:^|[-_])(img|dsc)[_-]?\d{3,}", re.IGNORECASE)
SCREENSHOT_NAME_RX = re.compile(r"screenshot", re.IGNORECASE)


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _lane_hint(row: dict[str, Any]) -> str:
    return _classify_lane(
        ask_text=str(row.get("ask_text", "")),
        title=str(row.get("conversation_title", "")),
        image_path=str(row.get("image_path", "")),
        followups=[],
        assistant_text="",
    )


def _lane_priority(lane: str) -> int:
    lane_norm = str(lane).strip().lower()
    if lane_norm == "handwriting":
        return 3
    if lane_norm == "illustration":
        return 2
    if lane_norm == "typed":
        return 1
    return 0


def _source_bonus(source_name: str) -> int:
    value = str(source_name).strip()
    if CAMERA_NAME_RX.search(value):
        return 2
    if SCREENSHOT_NAME_RX.search(value):
        return -1
    return 0


def _reason_priority(reason: str) -> int:
    if str(reason).strip() == "same_conversation_unmined":
        return 1
    return 0


def _candidate_sort_key(row: dict[str, Any]) -> tuple[int, int, int, int, str, str]:
    lane = str(row.get("lane_hint", ""))
    return (
        _reason_priority(str(row.get("intake_reason", ""))),
        int(row.get("priority_score", 0)),
        _lane_priority(lane),
        _source_bonus(str(row.get("source_name", ""))),
        str(row.get("conversation_title", "")).lower(),
        str(row.get("source_name", "")).lower(),
    )


def _candidate_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("candidates")
    if not isinstance(rows, list):
        raise RuntimeError("Candidate payload must contain a 'candidates' list.")
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        candidate_id = str(row.get("candidate_id", "")).strip()
        if not candidate_id:
            continue
        enriched = dict(row)
        enriched["lane_hint"] = _lane_hint(enriched)
        out.append(enriched)
    return out


def build_review(
    *,
    candidates_payload: dict[str, Any],
    max_cases: int,
    max_per_conversation: int,
    include_candidate_ids: set[str] | None = None,
) -> dict[str, Any]:
    rows = _candidate_rows(candidates_payload)
    rows_by_id = {str(row["candidate_id"]): row for row in rows}
    include_candidate_ids = include_candidate_ids or set()

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    selected_per_conversation: dict[str, int] = {}

    def add_row(row: dict[str, Any], *, selection_reason: str) -> bool:
        candidate_id = str(row.get("candidate_id", ""))
        if not candidate_id or candidate_id in selected_ids:
            return False
        conversation_id = str(row.get("conversation_id", ""))
        if selection_reason != "pinned_include":
            if max_per_conversation > 0 and selected_per_conversation.get(conversation_id, 0) >= max_per_conversation:
                return False
        enriched = dict(row)
        enriched["selection_reason"] = selection_reason
        selected.append(enriched)
        selected_ids.add(candidate_id)
        selected_per_conversation[conversation_id] = selected_per_conversation.get(conversation_id, 0) + 1
        return True

    for candidate_id in sorted(include_candidate_ids):
        row = rows_by_id.get(candidate_id)
        if row is None:
            continue
        add_row(row, selection_reason="pinned_include")

    remaining = [row for row in rows if str(row.get("candidate_id", "")) not in selected_ids]
    remaining.sort(key=_candidate_sort_key, reverse=True)

    lanes_in_order = ["handwriting", "illustration", "typed", "unknown"]
    lane_buckets: dict[str, list[dict[str, Any]]] = {lane: [] for lane in lanes_in_order}
    for row in remaining:
        lane = str(row.get("lane_hint", "")).strip().lower() or "unknown"
        lane_buckets.setdefault(lane, []).append(row)

    if max_cases <= 0:
        max_cases = len(rows)

    progressed = True
    while len(selected) < max_cases and progressed:
        progressed = False
        for lane in lanes_in_order:
            bucket = lane_buckets.get(lane, [])
            while bucket and len(selected) < max_cases:
                row = bucket.pop(0)
                if add_row(row, selection_reason="ranked_lane_mix"):
                    progressed = True
                    break

    for rank, row in enumerate(selected, start=1):
        row["selection_rank"] = rank

    lane_counts: dict[str, int] = {}
    reason_counts: dict[str, int] = {}
    for row in selected:
        lane = str(row.get("lane_hint", "unknown"))
        lane_counts[lane] = lane_counts.get(lane, 0) + 1
        reason = str(row.get("intake_reason", ""))
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": {
            "source_candidates": len(rows),
            "selected_cases": len(selected),
            "max_cases": max_cases,
            "max_per_conversation": max_per_conversation,
            "pinned_includes_requested": len(include_candidate_ids),
            "lane_counts": lane_counts,
            "intake_reason_counts": reason_counts,
        },
        "selected_candidates": selected,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a bounded OCR generalization review slice from OCR-ready candidates."
    )
    parser.add_argument(
        "--candidates",
        default=".local/eval_cases/ocr_generalization_candidates.json",
        help="Path to OCR generalization candidates JSON.",
    )
    parser.add_argument(
        "--output-review",
        default=".local/eval_cases/ocr_generalization_review.json",
        help="Output path for bounded OCR generalization review JSON.",
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        default=24,
        help="Maximum candidates to keep in the review slice.",
    )
    parser.add_argument(
        "--max-per-conversation",
        type=int,
        default=2,
        help="Maximum non-pinned candidates to keep per conversation.",
    )
    parser.add_argument(
        "--include-candidate-ids",
        default="",
        help="Comma-separated candidate ids to force-include in the review slice.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    include_candidate_ids = {
        token.strip()
        for token in str(args.include_candidate_ids or "").split(",")
        if token.strip()
    }
    payload = build_review(
        candidates_payload=_load_json_object(Path(args.candidates).expanduser().resolve()),
        max_cases=int(args.max_cases),
        max_per_conversation=int(args.max_per_conversation),
        include_candidate_ids=include_candidate_ids,
    )
    output_path = Path(args.output_review).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("OCR generalization review")
    print(f"candidates={payload['summary']['source_candidates']}")
    print(f"selected_cases={payload['summary']['selected_cases']}")
    print(f"max_cases={payload['summary']['max_cases']}")
    print(f"max_per_conversation={payload['summary']['max_per_conversation']}")
    print(f"pinned_includes_requested={payload['summary']['pinned_includes_requested']}")
    print(f"output={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
