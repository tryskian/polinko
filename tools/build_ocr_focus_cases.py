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


def build_focus_cases(
    *,
    cohort_payload: dict[str, Any],
    source_cases_payload: dict[str, Any],
    include_fail_history: bool,
    max_cases: int,
) -> dict[str, Any]:
    source_map = _case_map(source_cases_payload)

    selected_ids: list[str] = []
    selected_ids.extend(_case_id_list(cohort_payload, "cases"))
    if include_fail_history:
        selected_ids.extend(_case_id_list(cohort_payload, "fail_history_cases"))

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
        row = source_map.get(case_id)
        if row is None:
            missing.append(case_id)
            continue
        found.append(row)

    if max_cases > 0:
        found = found[:max_cases]

    summary = {
        "source_case_count": len(source_map),
        "requested_ids": len(dedup_ids),
        "selected_cases": len(found),
        "missing_ids": len(missing),
        "include_fail_history": include_fail_history,
        "max_cases": max_cases,
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
    print(f"  max_cases: {summary['max_cases']}")
    print(f"  output: {output_cases_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
