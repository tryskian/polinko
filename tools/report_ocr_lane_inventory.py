from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "polinko.ocr_lane_inventory.v1"

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


def _json_count(path: Path) -> int | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if isinstance(payload, dict):
        cases = payload.get("cases")
        if isinstance(cases, list):
            return len(cases)
        candidates = payload.get("candidates")
        if isinstance(candidates, list):
            return len(candidates)
    if isinstance(payload, list):
        return len(payload)
    return None


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
        count = _json_count(path)
        if count is not None:
            status["rows"] = count
    elif path.is_dir():
        status["kind"] = "dir"
        status["entries"] = len(list(path.iterdir()))
    return status


def build_inventory(*, root: Path) -> dict[str, Any]:
    notebook_dir = _resolve_path("NOTEBOOK_DIR", ".local/notebooks", root=root)
    notebook_start = _resolve_path(
        "NOTEBOOK_START_PATH",
        ".local/notebooks/ocr-eval-live-filters-starter.ipynb",
        root=root,
    )
    return {
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


def _format_row(item: dict[str, Any]) -> str:
    details: list[str] = [str(item["path"]), str(item["kind"])]
    if "rows" in item:
        details.append(f"rows={item['rows']}")
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
    return parser


def main() -> int:
    args = build_parser().parse_args()
    inventory = build_inventory(root=Path.cwd())
    if args.json:
        print(json.dumps(inventory, ensure_ascii=False, indent=2))
    else:
        print(format_inventory(inventory))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
