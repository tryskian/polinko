"""Validate and summarize the tracked operator-burden row surface."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

DEFAULT_ROWS_PATH = Path("docs/eval/beta_2_0/operator_burden_rows.json")
DEFAULT_OUTPUT_JSON = Path(".local/eval_reports/operator_burden_rows_summary.json")
DEFAULT_OUTPUT_MD = Path(".local/eval_reports/operator_burden_rows_summary.md")
ALLOWED_VERDICTS = {"pass", "fail"}
ALLOWED_DISPOSITIONS = {"retain", "evict"}
ALLOWED_DIMENSION_VALUES = {"pass", "fail", "na"}


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _require_non_empty_string(row: dict[str, Any], key: str) -> str:
    value = str(row.get(key, "")).strip()
    if not value:
        raise RuntimeError(f"Row {row.get('id', '<missing id>')}: missing '{key}'")
    return value


def _validate_dimensions(row: dict[str, Any]) -> dict[str, str]:
    raw = row.get("dimensions")
    if not isinstance(raw, dict) or not raw:
        raise RuntimeError(f"Row {row.get('id', '<missing id>')}: missing 'dimensions' object")
    out: dict[str, str] = {}
    for key, value in raw.items():
        dim = str(key).strip()
        status = str(value).strip().lower()
        if not dim:
            raise RuntimeError(f"Row {row.get('id', '<missing id>')}: empty dimension key")
        if status not in ALLOWED_DIMENSION_VALUES:
            raise RuntimeError(
                f"Row {row.get('id', '<missing id>')}: invalid dimension value for '{dim}': {value!r}"
            )
        out[dim] = status
    return out


def _validate_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("Expected non-empty 'rows' list.")

    seen_ids: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for raw in rows:
        if not isinstance(raw, dict):
            raise RuntimeError("Each row must be a JSON object.")
        row_id = _require_non_empty_string(raw, "id")
        if row_id in seen_ids:
            raise RuntimeError(f"Duplicate row id: {row_id}")
        seen_ids.add(row_id)

        verdict = _require_non_empty_string(raw, "verdict").lower()
        if verdict not in ALLOWED_VERDICTS:
            raise RuntimeError(f"Row {row_id}: invalid verdict {verdict!r}")

        disposition_raw = raw.get("failure_disposition")
        disposition = str(disposition_raw).strip().lower() if disposition_raw is not None else None
        if verdict == "fail":
            if disposition not in ALLOWED_DISPOSITIONS:
                raise RuntimeError(f"Row {row_id}: failing rows require failure_disposition retain|evict")
        else:
            if disposition is not None:
                raise RuntimeError(f"Row {row_id}: passing rows must not set failure_disposition")

        source_ids = raw.get("source_ids")
        if not isinstance(source_ids, list) or not all(str(item).strip() for item in source_ids):
            raise RuntimeError(f"Row {row_id}: 'source_ids' must be a non-empty string list")

        normalized.append(
            {
                "id": row_id,
                "title": _require_non_empty_string(raw, "title"),
                "source_note": _require_non_empty_string(raw, "source_note"),
                "source_ids": [str(item).strip() for item in source_ids],
                "task_shape": _require_non_empty_string(raw, "task_shape"),
                "expected_boundary": _require_non_empty_string(raw, "expected_boundary"),
                "observed_pattern": _require_non_empty_string(raw, "observed_pattern"),
                "dimensions": _validate_dimensions(raw),
                "verdict": verdict,
                "failure_disposition": disposition,
                "note": _require_non_empty_string(raw, "note"),
            }
        )
    return normalized


def build_report(payload: dict[str, Any]) -> dict[str, Any]:
    lane = str(payload.get("lane", "")).strip() or "operator_burden"
    version = int(payload.get("version", 0) or 0)
    hypothesis_id = str(payload.get("hypothesis_id", "")).strip()
    rows = _validate_rows(payload)

    verdict_counts: Counter[str] = Counter()
    disposition_counts: Counter[str] = Counter()
    dimension_fail_counts: Counter[str] = Counter()
    retained_failures: list[dict[str, Any]] = []
    evicted_failures: list[dict[str, Any]] = []

    for row in rows:
        verdict_counts[row["verdict"]] += 1
        if row["failure_disposition"]:
            disposition_counts[str(row["failure_disposition"])] += 1
        for dim, status in row["dimensions"].items():
            if status == "fail":
                dimension_fail_counts[dim] += 1
        if row["verdict"] == "fail":
            if row["failure_disposition"] == "retain":
                retained_failures.append(row)
            elif row["failure_disposition"] == "evict":
                evicted_failures.append(row)

    return {
        "lane": lane,
        "version": version,
        "hypothesis_id": hypothesis_id,
        "row_count": len(rows),
        "verdict_counts": {
            "pass": int(verdict_counts.get("pass", 0)),
            "fail": int(verdict_counts.get("fail", 0)),
        },
        "failure_disposition_counts": {
            "retain": int(disposition_counts.get("retain", 0)),
            "evict": int(disposition_counts.get("evict", 0)),
        },
        "dimension_fail_counts": [
            {"dimension": key, "count": count}
            for key, count in dimension_fail_counts.most_common()
        ],
        "retained_failures": [
            {
                "id": row["id"],
                "title": row["title"],
                "task_shape": row["task_shape"],
                "source_note": row["source_note"],
                "note": row["note"],
            }
            for row in retained_failures
        ],
        "evicted_failures": [
            {
                "id": row["id"],
                "title": row["title"],
                "task_shape": row["task_shape"],
                "source_note": row["source_note"],
                "note": row["note"],
            }
            for row in evicted_failures
        ],
        "rows": rows,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Operator Burden Rows Summary",
        "",
        f"- lane: `{report['lane']}`",
        f"- hypothesis: `{report.get('hypothesis_id', '')}`",
        f"- rows: `{report['row_count']}`",
        f"- pass: `{report['verdict_counts']['pass']}`",
        f"- fail: `{report['verdict_counts']['fail']}`",
        f"- retained failures: `{report['failure_disposition_counts']['retain']}`",
        f"- evicted failures: `{report['failure_disposition_counts']['evict']}`",
        "",
        "## Retained Failures",
        "",
    ]
    retained = report.get("retained_failures", [])
    if retained:
        for row in retained:
            lines.extend(
                [
                    f"- `{row['id']}` {row['title']}",
                    f"  - task shape: `{row['task_shape']}`",
                    f"  - source: `{row['source_note']}`",
                    f"  - note: {row['note']}",
                ]
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Dimension Fail Counts", ""])
    dim_counts = report.get("dimension_fail_counts", [])
    if dim_counts:
        for row in dim_counts:
            lines.append(f"- `{row['dimension']}`: `{row['count']}`")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", default=str(DEFAULT_ROWS_PATH), help="Path to operator-burden row JSON.")
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON), help="Path to summary JSON.")
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD), help="Path to summary markdown.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = _load_json_object(Path(args.rows))
    report = build_report(payload)
    _write_json(Path(args.output_json), report)
    _write_markdown(Path(args.output_md), render_markdown(report))
    print(
        "Operator burden rows summary: "
        f"rows={report['row_count']} "
        f"pass={report['verdict_counts']['pass']} "
        f"fail={report['verdict_counts']['fail']} "
        f"retain={report['failure_disposition_counts']['retain']} "
        f"evict={report['failure_disposition_counts']['evict']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
