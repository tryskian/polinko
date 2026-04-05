"""Build focused OCR case subsets from growth fail cohort outputs."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _case_id_list(payload: dict[str, Any], key: str) -> list[str]:
    rows = payload.get(key)
    if not isinstance(rows, list):
        return []
    out: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        case_id = str(row.get("id", "")).strip()
        if case_id:
            out.append(case_id)
    return out


def _cohort_case_map(payload: dict[str, Any], key: str) -> dict[str, dict[str, Any]]:
    rows = payload.get(key)
    if not isinstance(rows, list):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        case_id = str(row.get("id", "")).strip()
        if not case_id:
            continue
        out[case_id] = row
    return out


def _case_map(cases_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw_cases = cases_payload.get("cases")
    if not isinstance(raw_cases, list):
        raise RuntimeError("Source cases payload must contain a 'cases' list.")
    out: dict[str, dict[str, Any]] = {}
    for row in raw_cases:
        if not isinstance(row, dict):
            continue
        case_id = str(row.get("id", "")).strip()
        if not case_id:
            continue
        out[case_id] = row
    return out


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        token = str(item).strip()
        if token:
            out.append(token)
    return out


def _lane_priority(lane: str) -> int:
    lane_norm = str(lane).strip().lower()
    if lane_norm == "handwriting":
        return 2
    if lane_norm == "illustration":
        return 1
    if lane_norm == "typed":
        return 0
    return -1


def _focus_actionability_score(row: dict[str, Any]) -> int:
    must_order = _string_list(
        row.get("effective_must_appear_in_order") or row.get("must_appear_in_order")
    )
    must_any = _string_list(
        row.get("effective_must_contain_any") or row.get("must_contain_any")
    )

    primary_pattern = str(row.get("primary_failure_pattern", "")).strip().lower()
    fail_runs = int(row.get("fail_runs", 0) or 0)
    observed_runs = int(row.get("observed_runs", 0) or 0)
    text_variant_count = int(row.get("text_variant_count", 0) or 0)
    char_count_span = int(row.get("char_count_span", 0) or 0)
    lane_score = _lane_priority(str(row.get("lane", "")))

    score = 0
    if len(must_order) >= 2:
        score += 200
        score += min(len(must_order), 4) * 20
    elif primary_pattern == "anchor_any_missing":
        # Anchor-only misses with no sequence probe are high-noise in focus sets.
        score -= 150
    elif len(must_any) == 0:
        score -= 120

    if primary_pattern == "ordered_phrase_missing":
        score += 80
    elif primary_pattern.startswith("ordered_phrase_missing_"):
        score += 70
    elif primary_pattern == "anchor_any_missing":
        score += 10

    score += min(fail_runs, 6) * 8
    score += min(observed_runs, 6) * 4
    score += min(text_variant_count, 8) * 3
    score += min(char_count_span, 60) // 5
    score += lane_score * 10
    return score


def build_focus_cases(
    *,
    cohort_payload: dict[str, Any],
    source_cases_payload: dict[str, Any],
    include_fail_history: bool,
    include_exploratory: bool = True,
    max_cases: int,
) -> dict[str, Any]:
    source_map = _case_map(source_cases_payload)
    persistent_map = _cohort_case_map(cohort_payload, "cases")
    fail_history_map = _cohort_case_map(cohort_payload, "fail_history_cases")
    exploratory_map = _cohort_case_map(cohort_payload, "exploratory_cases")

    selected_ids: list[str] = []
    selected_ids.extend(_case_id_list(cohort_payload, "cases"))
    if include_fail_history:
        selected_ids.extend(_case_id_list(cohort_payload, "fail_history_cases"))
    if include_exploratory:
        selected_ids.extend(_case_id_list(cohort_payload, "exploratory_cases"))

    dedup_ids: list[str] = []
    seen: set[str] = set()
    for case_id in selected_ids:
        if case_id in seen:
            continue
        seen.add(case_id)
        dedup_ids.append(case_id)

    found: list[dict[str, Any]] = []
    missing: list[str] = []
    for case_id in dedup_ids:
        source_row = source_map.get(case_id)
        if source_row is None:
            missing.append(case_id)
            continue

        cohort_row = persistent_map.get(case_id)
        source_bucket = "persistent_fail"
        if cohort_row is None:
            cohort_row = fail_history_map.get(case_id)
            source_bucket = "fail_history"
        if cohort_row is None:
            cohort_row = exploratory_map.get(case_id)
            source_bucket = "exploratory"

        merged = dict(source_row)
        if cohort_row:
            for key, value in cohort_row.items():
                if key == "id":
                    continue
                existing = merged.get(key)
                if existing in (None, "", [], {}):
                    merged[key] = value
                if key == "lane" and str(existing).strip().lower() == "unknown":
                    merged[key] = value
            raw_focus_overrides = cohort_row.get("focus_overrides")
            focus_overrides: dict[str, Any] = (
                raw_focus_overrides if isinstance(raw_focus_overrides, dict) else {}
            )
            for key, value in focus_overrides.items():
                merged[key] = value
            if focus_overrides:
                merged["focus_override_keys"] = sorted(str(key) for key in focus_overrides.keys())
            merged["focus_source"] = source_bucket

        found.append(merged)

    if max_cases > 0:
        ranked_rows = sorted(
            enumerate(found),
            key=lambda item: (-_focus_actionability_score(item[1]), item[0]),
        )
        found = [row for _idx, row in ranked_rows[:max_cases]]

    cases_with_cohort_history = sum(
        1
        for row in found
        if row.get("focus_source") in {"persistent_fail", "fail_history"}
    )

    summary = {
        "source_case_count": len(source_map),
        "requested_ids": len(dedup_ids),
        "selected_cases": len(found),
        "missing_ids": len(missing),
        "include_fail_history": include_fail_history,
        "include_exploratory": include_exploratory,
        "max_cases": max_cases,
        "cases_with_cohort_history": cases_with_cohort_history,
    }
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": summary,
        "missing_ids": missing,
        "cases": found,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build focused OCR eval cases from fail cohort output."
    )
    parser.add_argument(
        "--cohort",
        default=".local/eval_cases/ocr_growth_fail_cohort.json",
        help="Path to fail cohort JSON from tools.build_ocr_growth_fail_cohort.",
    )
    parser.add_argument(
        "--source-cases",
        default=".local/eval_cases/ocr_transcript_cases_growth.json",
        help="Path to source OCR growth cases JSON.",
    )
    parser.add_argument(
        "--output-cases",
        default=".local/eval_cases/ocr_growth_focus_cases.json",
        help="Output path for focused OCR cases JSON.",
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        default=0,
        help="Maximum focused cases to keep (0 = all).",
    )
    parser.add_argument(
        "--exclude-fail-history",
        action="store_true",
        help="Exclude mixed PASS/FAIL fail-history cases from the focused set.",
    )
    parser.add_argument(
        "--exclude-exploratory",
        action="store_true",
        help="Exclude exploratory strict-replay cases from the focused set.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.max_cases < 0:
        print("max-cases must be >= 0")
        return 2

    cohort_path = Path(args.cohort).expanduser()
    source_cases_path = Path(args.source_cases).expanduser()
    output_cases_path = Path(args.output_cases).expanduser()

    if not cohort_path.is_file():
        print(f"cohort file not found: {cohort_path}")
        return 2
    if not source_cases_path.is_file():
        print(f"source cases file not found: {source_cases_path}")
        return 2

    cohort_payload = _load_json_object(cohort_path)
    source_cases_payload = _load_json_object(source_cases_path)
    report = build_focus_cases(
        cohort_payload=cohort_payload,
        source_cases_payload=source_cases_payload,
        include_fail_history=not bool(args.exclude_fail_history),
        include_exploratory=not bool(args.exclude_exploratory),
        max_cases=int(args.max_cases),
    )

    output_cases_path.parent.mkdir(parents=True, exist_ok=True)
    output_cases_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = report["summary"]
    print("OCR focus cases")
    print(f"  source_case_count: {summary['source_case_count']}")
    print(f"  requested_ids: {summary['requested_ids']}")
    print(f"  selected_cases: {summary['selected_cases']}")
    print(f"  missing_ids: {summary['missing_ids']}")
    print(f"  include_fail_history: {summary['include_fail_history']}")
    print(f"  include_exploratory: {summary['include_exploratory']}")
    print(f"  max_cases: {summary['max_cases']}")
    print(f"  output: {output_cases_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
