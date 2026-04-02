"""Audit high-signal NULL surfaces in active runtime DBs."""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any


def _count_query(conn: sqlite3.Connection, query: str) -> int:
    row = conn.execute(query).fetchone()
    if row is None:
        return 0
    return int(row[0] or 0)


def _history_metrics(path: Path) -> dict[str, int]:
    with sqlite3.connect(path) as conn:
        return {
            "ocr_runs_total": _count_query(conn, "SELECT COUNT(*) FROM ocr_runs"),
            "source_message_id_null": _count_query(
                conn,
                "SELECT COUNT(*) FROM ocr_runs WHERE source_message_id IS NULL OR trim(source_message_id) = ''",
            ),
            "result_message_id_null": _count_query(
                conn,
                "SELECT COUNT(*) FROM ocr_runs WHERE result_message_id IS NULL OR trim(result_message_id) = ''",
            ),
            "both_message_ids_null": _count_query(
                conn,
                "SELECT COUNT(*) FROM ocr_runs WHERE (source_message_id IS NULL OR trim(source_message_id) = '') "
                "AND (result_message_id IS NULL OR trim(result_message_id) = '')",
            ),
        }


def _vector_metrics(path: Path) -> dict[str, int]:
    with sqlite3.connect(path) as conn:
        return {
            "message_vectors_total": _count_query(conn, "SELECT COUNT(*) FROM message_vectors"),
            "message_id_null": _count_query(
                conn,
                "SELECT COUNT(*) FROM message_vectors WHERE message_id IS NULL OR trim(message_id) = ''",
            ),
            "non_chat_total": _count_query(
                conn,
                "SELECT COUNT(*) FROM message_vectors WHERE source_type IS NOT NULL AND source_type <> 'chat'",
            ),
            "non_chat_message_id_null": _count_query(
                conn,
                "SELECT COUNT(*) FROM message_vectors WHERE source_type IS NOT NULL AND source_type <> 'chat' "
                "AND (message_id IS NULL OR trim(message_id) = '')",
            ),
        }


def _render_markdown(report: dict[str, Any]) -> str:
    history = report["history"]
    vector = report["vector"]
    lines: list[str] = []
    lines.append("# Runtime NULL Audit")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append("")
    lines.append("## Paths")
    lines.append("")
    lines.append(f"- history: `{report['history_db']}`")
    lines.append(f"- vector: `{report['vector_db']}`")
    lines.append("")
    lines.append("## History (`ocr_runs`)")
    lines.append("")
    lines.append("| metric | count |")
    lines.append("|---|---:|")
    lines.append(f"| ocr_runs_total | {history['ocr_runs_total']} |")
    lines.append(f"| source_message_id_null | {history['source_message_id_null']} |")
    lines.append(f"| result_message_id_null | {history['result_message_id_null']} |")
    lines.append(f"| both_message_ids_null | {history['both_message_ids_null']} |")
    lines.append("")
    lines.append("## Vector (`message_vectors`)")
    lines.append("")
    lines.append("| metric | count |")
    lines.append("|---|---:|")
    lines.append(f"| message_vectors_total | {vector['message_vectors_total']} |")
    lines.append(f"| message_id_null | {vector['message_id_null']} |")
    lines.append(f"| non_chat_total | {vector['non_chat_total']} |")
    lines.append(f"| non_chat_message_id_null | {vector['non_chat_message_id_null']} |")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "- `ocr_runs` message refs may be null for non-chat-attached OCR flows; "
        "use resolved refs (`ocr://<run_id>/source|result`) for joins."
    )
    lines.append(
        "- `non_chat_message_id_null` should trend toward `0` after vector backfill; "
        "non-zero indicates stale legacy rows worth migration."
    )
    lines.append("")
    return "\n".join(lines)


def build_report(*, history_db: Path, vector_db: Path) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "history_db": str(history_db),
        "vector_db": str(vector_db),
        "history": _history_metrics(history_db),
        "vector": _vector_metrics(vector_db),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit high-signal runtime NULL surfaces.")
    parser.add_argument(
        "--history-db",
        default=".local/runtime_dbs/active/history.db",
        help="Path to active history DB.",
    )
    parser.add_argument(
        "--vector-db",
        default=".local/runtime_dbs/active/vector.db",
        help="Path to active vector DB.",
    )
    parser.add_argument(
        "--output-json",
        default=".local/eval_reports/runtime_null_audit.json",
        help="Output JSON report path.",
    )
    parser.add_argument(
        "--output-markdown",
        default=".local/eval_reports/runtime_null_audit.md",
        help="Output markdown report path.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    history_db = Path(args.history_db).expanduser()
    vector_db = Path(args.vector_db).expanduser()
    output_json = Path(args.output_json).expanduser()
    output_markdown = Path(args.output_markdown).expanduser()

    if not history_db.is_file():
        print(f"history DB not found: {history_db}")
        return 2
    if not vector_db.is_file():
        print(f"vector DB not found: {vector_db}")
        return 2

    report = build_report(history_db=history_db, vector_db=vector_db)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    output_markdown.write_text(_render_markdown(report), encoding="utf-8")

    print("Runtime NULL audit")
    print(f"  history ocr_runs_total: {report['history']['ocr_runs_total']}")
    print(f"  history both_message_ids_null: {report['history']['both_message_ids_null']}")
    print(f"  vector message_vectors_total: {report['vector']['message_vectors_total']}")
    print(f"  vector non_chat_message_id_null: {report['vector']['non_chat_message_id_null']}")
    print(f"  json: {output_json}")
    print(f"  markdown: {output_markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
