from __future__ import annotations

import argparse
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path


def _clip(value: object, width: int = 100) -> str:
    text = "" if value is None else str(value)
    return text if len(text) <= width else f"{text[: width - 3]}..."


def _render_table(headers: list[str], rows: list[tuple[object, ...]]) -> str:
    clipped_rows = [[_clip(cell) for cell in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in clipped_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    divider = "-+-".join("-" * w for w in widths)
    lines = []
    lines.append(" | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)))
    lines.append(divider)
    for row in clipped_rows:
        lines.append(" | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))
    return "\n".join(lines)


def _run_latest(conn: sqlite3.Connection, limit: int) -> tuple[list[str], list[tuple[object, ...]]]:
    cur = conn.execute(
        """
        SELECT category, title, path, COALESCE(captured_on, modified_utc) AS reference_date, word_count
        FROM v_human_reference_latest
        LIMIT ?
        """,
        (limit,),
    )
    headers = [d[0] for d in cur.description or []]
    return headers, cur.fetchall()


def _run_transcripts(conn: sqlite3.Connection, limit: int) -> tuple[list[str], list[tuple[object, ...]]]:
    cur = conn.execute(
        """
        SELECT category, title, path, COALESCE(captured_on, modified_utc) AS reference_date, word_count
        FROM documents
        WHERE category IN ('transcripts', 'key_points')
        ORDER BY COALESCE(captured_on, modified_utc) DESC, path ASC
        LIMIT ?
        """,
        (limit,),
    )
    headers = [d[0] for d in cur.description or []]
    return headers, cur.fetchall()


def _run_changes(
    conn: sqlite3.Connection, limit: int, since_hours: int
) -> tuple[list[str], list[tuple[object, ...]]]:
    threshold = (datetime.now(UTC) - timedelta(hours=since_hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    cur = conn.execute(
        """
        SELECT category, title, path, modified_utc
        FROM documents
        WHERE modified_utc >= ?
        ORDER BY modified_utc DESC, path ASC
        LIMIT ?
        """,
        (threshold, limit),
    )
    headers = [d[0] for d in cur.description or []]
    return headers, cur.fetchall()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one-click human-reference DB queries.")
    parser.add_argument(
        "query",
        choices=("latest", "transcripts", "changes"),
        help="Query preset to run.",
    )
    parser.add_argument(
        "--db",
        default=".human_reference.db",
        help="Path to human reference sqlite database.",
    )
    parser.add_argument("--limit", type=int, default=25, help="Max rows to print.")
    parser.add_argument(
        "--since-hours",
        type=int,
        default=24,
        help="Used by `changes` query. Include docs modified in the last N hours.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")

    with sqlite3.connect(db_path) as conn:
        if args.query == "latest":
            headers, rows = _run_latest(conn, args.limit)
            label = f"latest (limit={args.limit})"
        elif args.query == "transcripts":
            headers, rows = _run_transcripts(conn, args.limit)
            label = f"transcripts+key_points (limit={args.limit})"
        else:
            headers, rows = _run_changes(conn, args.limit, args.since_hours)
            label = f"changes since {args.since_hours}h (limit={args.limit})"

    print(f"human-reference query: {label}")
    if not rows:
        print("(no rows)")
        return
    print(_render_table(headers, rows))


if __name__ == "__main__":
    main()

