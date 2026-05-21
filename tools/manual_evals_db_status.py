from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from polinko.api.manual_evals_surface import build_manual_evals_surface_payload


def data_freshness_status(*, db_path: Path) -> dict[str, Any]:
    payload = build_manual_evals_surface_payload(db_path=db_path)
    freshness = payload.get("data_freshness")
    if isinstance(freshness, dict):
        return freshness
    return {
        "state": "unknown",
        "warnings": ["manual eval freshness payload is missing"],
        "manual_evals_db": {"path": str(db_path), "exists": db_path.is_file()},
        "source_history_dbs": [],
    }


def _format_source_deltas(deltas: object) -> str:
    if not isinstance(deltas, dict) or not deltas:
        return "none"
    parts: list[str] = []
    for key, value in sorted(deltas.items()):
        try:
            delta = int(value)
        except (TypeError, ValueError):
            continue
        if delta != 0:
            parts.append(f"{key}={delta}")
    return ", ".join(parts) if parts else "none"


def format_freshness_status(freshness: dict[str, Any]) -> str:
    manual_db = freshness.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    warnings = freshness.get("warnings")
    warning_items = warnings if isinstance(warnings, list) else []

    lines = [
        "manual_evals.db status: "
        f"state={freshness.get('state', 'unknown')} "
        f"schema_current={manual_db.get('schema_current', False)} "
        f"generated_at_utc={manual_db.get('generated_at_utc', '') or 'unknown'} "
        f"path={manual_db.get('path', '') or 'unknown'}",
    ]

    source_items = freshness.get("source_history_dbs")
    if isinstance(source_items, list) and source_items:
        for source in source_items:
            if not isinstance(source, dict):
                continue
            label = source.get("label") or source.get("era") or "source"
            lines.append(
                "source "
                f"{label}: exists={source.get('exists', False)} "
                f"count_scope={source.get('count_scope', 'unknown')} "
                f"deltas={_format_source_deltas(source.get('count_deltas'))} "
                f"newer_than_generated={source.get('is_newer_than_generated', False)}"
            )
    else:
        lines.append("source history DBs: none recorded")

    if warning_items:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warning_items)
    else:
        lines.append("warnings: none")

    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print read-only manual eval warehouse freshness status.",
    )
    parser.add_argument(
        "--db",
        default=".local/runtime_dbs/active/manual_evals.db",
        help="Path to manual eval warehouse DB.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the data_freshness payload as JSON.",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    freshness = data_freshness_status(db_path=Path(args.db).expanduser())
    if args.json:
        print(json.dumps(freshness, indent=2, sort_keys=True))
    else:
        print(format_freshness_status(freshness))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
