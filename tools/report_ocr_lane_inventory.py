from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "polinko.ocr_lane_inventory.v1"
DEFAULT_FRESHNESS_DAYS = 14.0
ROW_COUNT_KEYS = (
    "cases",
    "candidates",
    "selected_candidates",
    "failing_cases",
    "runs",
    "items",
)
FRESHNESS_SECTION_KEYS = ("local_cases", "local_reports")

TRACKED_CASE_PATHS: tuple[tuple[str, str], ...] = (
    ("base_ocr_cases", "docs/eval/beta_2_0/ocr_eval_cases.json"),
    ("ocr_recovery_cases", "docs/eval/beta_2_0/ocr_recovery_eval_cases.json"),
    ("ocr_safety_cases", "docs/eval/beta_2_0/ocr_safety_eval_cases.json"),
)

LOCAL_CASE_DEFAULTS: tuple[tuple[str, str, str], ...] = (
    (
        "transcript_all",
        "OCR_TRANSCRIPT_CASES_ALL",
        ".local/eval_cases/ocr_transcript_cases_all.json",
    ),
    (
        "transcript_growth",
        "OCR_TRANSCRIPT_CASES_GROWTH",
        ".local/eval_cases/ocr_transcript_cases_growth.json",
    ),
    (
        "handwriting",
        "OCR_TRANSCRIPT_CASES_HANDWRITING",
        ".local/eval_cases/ocr_handwriting_from_transcripts.json",
    ),
    (
        "typed",
        "OCR_TRANSCRIPT_CASES_TYPED",
        ".local/eval_cases/ocr_typed_from_transcripts.json",
    ),
    (
        "illustration",
        "OCR_TRANSCRIPT_CASES_ILLUSTRATION",
        ".local/eval_cases/ocr_illustration_from_transcripts.json",
    ),
    (
        "handwriting_benchmark",
        "OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK",
        ".local/eval_cases/ocr_handwriting_benchmark_cases.json",
    ),
    (
        "typed_benchmark",
        "OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK",
        ".local/eval_cases/ocr_typed_benchmark_cases.json",
    ),
    (
        "illustration_benchmark",
        "OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK",
        ".local/eval_cases/ocr_illustration_benchmark_cases.json",
    ),
    (
        "generalization_candidates",
        "OCR_GENERALIZATION_CANDIDATES",
        ".local/eval_cases/ocr_generalization_candidates.json",
    ),
    (
        "generalization_review",
        "OCR_GENERALIZATION_REVIEW",
        ".local/eval_cases/ocr_generalization_review.json",
    ),
    (
        "growth_fail_cohort",
        "OCR_GROWTH_FAIL_COHORT_JSON",
        ".local/eval_cases/ocr_growth_fail_cohort.json",
    ),
    (
        "focus_cases",
        "OCR_FOCUS_CASES_JSON",
        ".local/eval_cases/ocr_growth_focus_cases.json",
    ),
)

LOCAL_REPORT_DEFAULTS: tuple[tuple[str, str, str], ...] = (
    (
        "transcript_stability",
        "OCR_STABILITY_OUTPUT",
        ".local/eval_reports/ocr_transcript_stability.json",
    ),
    (
        "growth_stability",
        "OCR_GROWTH_STABILITY_OUTPUT",
        ".local/eval_reports/ocr_growth_stability.json",
    ),
    (
        "growth_metrics",
        "OCR_GROWTH_METRICS_OUTPUT",
        ".local/eval_reports/ocr_growth_metrics.json",
    ),
    (
        "growth_fail_cohort",
        "OCR_GROWTH_FAIL_COHORT_MARKDOWN",
        ".local/eval_reports/ocr_growth_fail_cohort.md",
    ),
    (
        "focus_stability",
        "OCR_FOCUS_OUTPUT",
        ".local/eval_reports/ocr_focus_stability.json",
    ),
    (
        "focus_fail_patterns",
        "OCR_FOCUS_FAIL_PATTERNS_JSON",
        ".local/eval_reports/ocr_focus_fail_patterns.json",
    ),
)

LOCAL_REPORT_DIR_DEFAULTS: tuple[tuple[str, str, str], ...] = (
    (
        "transcript_stability_runs",
        "OCR_STABILITY_REPORT_DIR",
        ".local/eval_reports/ocr_stability_runs",
    ),
    (
        "growth_stability_runs",
        "OCR_GROWTH_STABILITY_REPORT_DIR",
        ".local/eval_reports/ocr_growth_stability_runs",
    ),
    (
        "growth_batched_runs",
        "OCR_GROWTH_BATCH_REPORT_DIR",
        ".local/eval_reports/ocr_growth_batched_runs",
    ),
    (
        "focus_runs",
        "OCR_FOCUS_REPORT_DIR",
        ".local/eval_reports/ocr_focus_runs",
    ),
)

MANUAL_EVAL_PATHS: tuple[tuple[str, str, str], ...] = (
    (
        "manual_evals_db",
        "POLINKO_MANUAL_EVALS_DB_PATH",
        ".local/runtime_dbs/active/manual_evals.db",
    ),
    (
        "history_db",
        "POLINKO_HISTORY_DB_PATH",
        ".local/runtime_dbs/active/history.db",
    ),
)


def _resolve_path(env_name: str, default: str, *, root: Path) -> Path:
    path = Path(os.getenv(env_name, default)).expanduser()
    if path.is_absolute():
        return path
    return root / path


def _display_path(path: Path, *, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _json_shape(payload: Any) -> str:
    if isinstance(payload, dict):
        return "object"
    if isinstance(payload, list):
        return "list"
    return type(payload).__name__


def _json_metadata(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    metadata: dict[str, Any] = {"json_shape": _json_shape(payload)}
    if isinstance(payload, list):
        metadata["rows"] = len(payload)
        return metadata
    if isinstance(payload, dict):
        schema_version = payload.get("schema_version")
        if isinstance(schema_version, str):
            metadata["source_schema_version"] = schema_version
        generated_at = payload.get("generated_at")
        if isinstance(generated_at, str | int | float):
            metadata["generated_at"] = generated_at
        list_counts = {
            key: len(value)
            for key, value in sorted(payload.items())
            if isinstance(value, list)
        }
        if list_counts:
            metadata["list_counts"] = list_counts
            for key in ROW_COUNT_KEYS:
                if key in list_counts:
                    metadata["rows"] = list_counts[key]
                    metadata["row_source"] = key
                    break
    return metadata


def _parse_generated_at(value: Any) -> datetime | None:
    if isinstance(value, int | float):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    if not isinstance(value, str):
        return None
    raw_value = value.strip()
    if not raw_value:
        return None
    try:
        parsed = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _age_days(generated_at: datetime, *, now: datetime) -> float:
    return round(max((now - generated_at).total_seconds(), 0.0) / 86_400, 2)


def _annotate_freshness(
    inventory: dict[str, Any],
    *,
    now: datetime,
    freshness_days: float,
) -> None:
    summary: dict[str, Any] = {
        "threshold_days": freshness_days,
        "current": 0,
        "stale": 0,
        "unknown": 0,
        "missing": 0,
        "current_items": [],
        "stale_items": [],
        "unknown_items": [],
        "missing_items": [],
    }
    for section_key in FRESHNESS_SECTION_KEYS:
        for item in inventory[section_key]:
            item_ref = {
                "section": section_key,
                "name": item["name"],
                "path": item["path"],
            }
            if not item.get("exists"):
                item["freshness_state"] = "missing"
                item["freshness_reason"] = "path_missing"
                summary["missing"] += 1
                summary["missing_items"].append(item_ref)
                continue

            generated_at = _parse_generated_at(item.get("generated_at"))
            if generated_at is None:
                item["freshness_state"] = "unknown"
                item["freshness_reason"] = "generated_at_missing_or_invalid"
                summary["unknown"] += 1
                summary["unknown_items"].append(item_ref)
                continue

            generated_at_utc = generated_at.strftime("%Y-%m-%dT%H:%M:%SZ")
            age_days = _age_days(generated_at, now=now)
            item["generated_at_utc"] = generated_at_utc
            item["age_days"] = age_days
            item_ref.update(
                {
                    "generated_at_utc": generated_at_utc,
                    "age_days": age_days,
                }
            )
            if age_days > freshness_days:
                item["freshness_state"] = "stale"
                item["freshness_reason"] = "generated_at_older_than_threshold"
                summary["stale"] += 1
                summary["stale_items"].append(item_ref)
            else:
                item["freshness_state"] = "current"
                item["freshness_reason"] = "generated_at_within_threshold"
                summary["current"] += 1
                summary["current_items"].append(item_ref)

    for key in ("current_items", "stale_items", "unknown_items", "missing_items"):
        summary[key].sort(key=lambda item: (str(item["section"]), str(item["name"])))
    inventory["freshness"] = summary


def _file_status(name: str, path: Path, *, root: Path) -> dict[str, Any]:
    exists = path.exists()
    status: dict[str, Any] = {
        "name": name,
        "path": _display_path(path, root=root),
        "exists": exists,
        "kind": "missing",
    }
    if path.is_file():
        status["kind"] = "file"
        status["bytes"] = path.stat().st_size
        status.update(_json_metadata(path))
    elif path.is_dir():
        status["kind"] = "dir"
        status["entries"] = len(list(path.iterdir()))
    return status


def build_inventory(
    *,
    root: Path,
    now: datetime | None = None,
    freshness_days: float = DEFAULT_FRESHNESS_DAYS,
) -> dict[str, Any]:
    if now is None:
        now = datetime.now(timezone.utc)
    else:
        now = now.astimezone(timezone.utc)
    notebook_dir = _resolve_path("NOTEBOOK_DIR", ".local/notebooks", root=root)
    notebook_start = _resolve_path(
        "NOTEBOOK_START_PATH",
        ".local/notebooks/ocr-eval-live-filters-starter.ipynb",
        root=root,
    )
    inventory = {
        "schema_version": SCHEMA_VERSION,
        "tracked_cases": [
            _file_status(name, root / path, root=root)
            for name, path in TRACKED_CASE_PATHS
        ],
        "local_cases": [
            _file_status(name, _resolve_path(env_name, default, root=root), root=root)
            for name, env_name, default in LOCAL_CASE_DEFAULTS
        ],
        "local_reports": [
            _file_status(name, _resolve_path(env_name, default, root=root), root=root)
            for name, env_name, default in LOCAL_REPORT_DEFAULTS
        ],
        "local_report_dirs": [
            _file_status(name, _resolve_path(env_name, default, root=root), root=root)
            for name, env_name, default in LOCAL_REPORT_DIR_DEFAULTS
        ],
        "manual_eval_sources": [
            _file_status(name, _resolve_path(env_name, default, root=root), root=root)
            for name, env_name, default in MANUAL_EVAL_PATHS
        ],
        "notebooks": [
            _file_status("notebook_dir", notebook_dir, root=root),
            _file_status("notebook_start", notebook_start, root=root),
        ],
    }
    _annotate_freshness(
        inventory,
        now=now,
        freshness_days=freshness_days,
    )
    return inventory


def _format_row(item: dict[str, Any]) -> str:
    details: list[str] = [str(item["path"]), str(item["kind"])]
    if "json_shape" in item:
        details.append(f"json={item['json_shape']}")
    if "source_schema_version" in item:
        details.append(f"schema={item['source_schema_version']}")
    if "freshness_state" in item:
        details.append(f"freshness={item['freshness_state']}")
    if "age_days" in item:
        details.append(f"age_days={item['age_days']}")
    if "rows" in item:
        details.append(f"rows={item['rows']}")
    if "row_source" in item:
        details.append(f"row_source={item['row_source']}")
    if "list_counts" in item:
        list_counts = item["list_counts"]
        details.append(
            "lists=" + ",".join(f"{key}:{value}" for key, value in list_counts.items())
        )
    if "entries" in item:
        details.append(f"entries={item['entries']}")
    if "bytes" in item and "rows" not in item:
        details.append(f"bytes={item['bytes']}")
    return f"  - {item['name']}: " + " ".join(details)


def format_inventory(inventory: dict[str, Any]) -> str:
    sections = (
        ("tracked cases", "tracked_cases"),
        ("local case inputs", "local_cases"),
        ("local reports", "local_reports"),
        ("local report dirs", "local_report_dirs"),
        ("manual eval sources", "manual_eval_sources"),
        ("notebooks", "notebooks"),
    )
    lines = [f"OCR lane inventory: {inventory['schema_version']}"]
    freshness = inventory.get("freshness")
    if isinstance(freshness, dict):
        lines.append("")
        lines.append("freshness")
        lines.append(
            "  - "
            f"threshold_days={freshness['threshold_days']} "
            f"current={freshness['current']} "
            f"stale={freshness['stale']} "
            f"unknown={freshness['unknown']} "
            f"missing={freshness['missing']}"
        )
        for item in freshness["stale_items"]:
            lines.append(
                "  - stale: "
                f"{item['section']}/{item['name']} "
                f"generated_at={item['generated_at_utc']} "
                f"age_days={item['age_days']}"
            )
    for title, key in sections:
        lines.append("")
        lines.append(title)
        lines.extend(_format_row(item) for item in inventory[key])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Print a read-only inventory of OCR lane cases, reports, "
            "and local evidence paths."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit inventory as JSON instead of terminal text.",
    )
    parser.add_argument(
        "--freshness-days",
        type=float,
        default=DEFAULT_FRESHNESS_DAYS,
        help=(
            "Mark local case/report files stale when generated_at is older "
            "than this many days."
        ),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    inventory = build_inventory(root=Path.cwd(), freshness_days=args.freshness_days)
    if args.json:
        print(json.dumps(inventory, ensure_ascii=False, indent=2))
    else:
        print(format_inventory(inventory))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
