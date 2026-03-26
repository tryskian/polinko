from __future__ import annotations

import argparse
import json
import os
import sqlite3
from dataclasses import dataclass
from typing import Any


_CANONICAL_OUTCOMES = {"pass", "fail"}
_LEGACY_MIXED = "mixed"
_REMEDIATION_TAG = "needs_retry"


@dataclass(frozen=True)
class NormalizationResult:
    scanned: int
    updated: int
    mixed_mapped: int
    unknown_mapped: int


def _normalize_outcome(raw_outcome: str) -> tuple[str, str | None]:
    normalized = raw_outcome.strip().lower()
    if normalized in _CANONICAL_OUTCOMES:
        return normalized, None
    if normalized == _LEGACY_MIXED:
        return "fail", "mixed"
    return "fail", "unknown"


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in values if item))


def _parse_tags_json(raw_tags: str | None, fallback_outcome: str) -> tuple[list[str], list[str], list[str]]:
    positive: list[str] = []
    negative: list[str] = []
    all_tags: list[str] = []
    decoded: Any
    if raw_tags is None:
        decoded = []
    else:
        try:
            decoded = json.loads(raw_tags)
        except (TypeError, ValueError):
            decoded = []
    if isinstance(decoded, dict):
        raw_positive = decoded.get("positive")
        if isinstance(raw_positive, list):
            positive = [str(item).strip() for item in raw_positive if str(item).strip()]
        raw_negative = decoded.get("negative")
        if isinstance(raw_negative, list):
            negative = [str(item).strip() for item in raw_negative if str(item).strip()]
        raw_all = decoded.get("all")
        if isinstance(raw_all, list):
            all_tags = [str(item).strip() for item in raw_all if str(item).strip()]
    elif isinstance(decoded, list):
        all_tags = [str(item).strip() for item in decoded if str(item).strip()]
        if fallback_outcome == "fail":
            negative = list(all_tags)
        else:
            positive = list(all_tags)
    positive = _dedupe(positive)
    negative = _dedupe(negative)
    if not all_tags:
        all_tags = _dedupe(positive + negative)
    else:
        all_tags = _dedupe(all_tags)
    return positive, negative, all_tags


def _serialize_tags_json(positive: list[str], negative: list[str], all_tags: list[str]) -> str:
    payload = {
        "positive": _dedupe(positive),
        "negative": _dedupe(negative),
        "all": _dedupe(all_tags),
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def normalize_feedback_outcomes(db_path: str, dry_run: bool = False) -> NormalizationResult:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    scanned = 0
    updated = 0
    mixed_mapped = 0
    unknown_mapped = 0
    try:
        rows = conn.execute(
            """
            SELECT id, outcome, tags_json
            FROM message_feedback
            ORDER BY id ASC;
            """
        ).fetchall()
        for row in rows:
            scanned += 1
            row_id = int(row["id"])
            raw_outcome = str(row["outcome"] or "")
            normalized_outcome, mapped_reason = _normalize_outcome(raw_outcome)
            positive, negative, all_tags = _parse_tags_json(row["tags_json"], normalized_outcome)
            if mapped_reason is not None and _REMEDIATION_TAG not in negative:
                negative.append(_REMEDIATION_TAG)
            canonical_tags_json = _serialize_tags_json(positive, negative, _dedupe(all_tags + positive + negative))

            outcome_changed = raw_outcome != normalized_outcome
            tags_changed = str(row["tags_json"] or "") != canonical_tags_json
            if not outcome_changed and not tags_changed:
                continue

            if mapped_reason == "mixed":
                mixed_mapped += 1
            elif mapped_reason == "unknown":
                unknown_mapped += 1
            updated += 1
            if not dry_run:
                conn.execute(
                    """
                    UPDATE message_feedback
                    SET outcome = ?, tags_json = ?, updated_at = CAST(strftime('%s','now') AS INTEGER) * 1000
                    WHERE id = ?;
                    """,
                    (normalized_outcome, canonical_tags_json, row_id),
                )
        if not dry_run:
            conn.commit()
    finally:
        conn.close()
    return NormalizationResult(
        scanned=scanned,
        updated=updated,
        mixed_mapped=mixed_mapped,
        unknown_mapped=unknown_mapped,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalise legacy feedback outcomes to binary pass/fail in history DB."
    )
    parser.add_argument(
        "--db-path",
        default=os.getenv("POLINKO_HISTORY_DB_PATH", ".polinko_history.db"),
        help="Path to history SQLite DB (default: POLINKO_HISTORY_DB_PATH or .polinko_history.db).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and print changes without writing updates.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    result = normalize_feedback_outcomes(db_path=args.db_path, dry_run=args.dry_run)
    print(
        json.dumps(
            {
                "db_path": args.db_path,
                "dry_run": bool(args.dry_run),
                "scanned": result.scanned,
                "updated": result.updated,
                "mixed_mapped": result.mixed_mapped,
                "unknown_mapped": result.unknown_mapped,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
