from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from tools.manage_local_dbs import _resolve_db_paths


@dataclass(frozen=True)
class ColumnInfo:
    name: str
    declared_type: str
    pk: bool


@dataclass(frozen=True)
class ForeignKeyInfo:
    table: str
    from_col: str
    to_col: str


def _map_type(declared: str) -> str:
    probe = (declared or "").lower()
    if "int" in probe:
        return "int"
    if "real" in probe or "float" in probe or "double" in probe:
        return "float"
    if "blob" in probe:
        return "binary"
    if "bool" in probe:
        return "boolean"
    return "string"


def _load_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name ASC;
        """
    ).fetchall()
    return [str(row[0]) for row in rows]


def _load_columns(conn: sqlite3.Connection, table: str) -> list[ColumnInfo]:
    rows = conn.execute(f"PRAGMA table_info({table});").fetchall()
    out: list[ColumnInfo] = []
    for row in rows:
        # cid, name, type, notnull, dflt_value, pk
        out.append(
            ColumnInfo(
                name=str(row[1]),
                declared_type=str(row[2] or "TEXT"),
                pk=bool(row[5]),
            )
        )
    return out


def _load_foreign_keys(conn: sqlite3.Connection, table: str) -> list[ForeignKeyInfo]:
    rows = conn.execute(f"PRAGMA foreign_key_list({table});").fetchall()
    out: list[ForeignKeyInfo] = []
    for row in rows:
        # id, seq, table, from, to, on_update, on_delete, match
        out.append(
            ForeignKeyInfo(
                table=str(row[2]),
                from_col=str(row[3]),
                to_col=str(row[4]),
            )
        )
    return out


def _table_count(conn: sqlite3.Connection, table: str) -> int:
    row = conn.execute(f"SELECT COUNT(*) FROM {table};").fetchone()
    return int(row[0]) if row else 0


def _render_db_section(db_name: str, db_path: Path) -> str:
    lines: list[str] = []
    lines.append(f"## {db_name} ({db_path})")

    if not db_path.exists():
        lines.append("")
        lines.append("- status: missing")
        lines.append("")
        return "\n".join(lines)

    conn = sqlite3.connect(db_path)
    try:
        tables = _load_tables(conn)
        lines.append("")
        lines.append("- status: present")
        lines.append(f"- tables: {len(tables)}")
        lines.append("")

        lines.append("```mermaid")
        lines.append("erDiagram")

        relationships: list[str] = []
        for table in tables:
            columns = _load_columns(conn, table)
            lines.append(f"  {table} {{")
            for col in columns:
                mapped = _map_type(col.declared_type)
                key = " PK" if col.pk else ""
                lines.append(f"    {mapped} {col.name}{key}")
            lines.append("  }")

            for fk in _load_foreign_keys(conn, table):
                relationships.append(
                    f"  {fk.table} ||--o{{ {table} : \"{fk.to_col}->{fk.from_col}\""
                )

        for rel in sorted(set(relationships)):
            lines.append(rel)

        lines.append("```")
        lines.append("")
        lines.append("### Row Counts")
        lines.append("")
        for table in tables:
            lines.append(f"- `{table}`: {_table_count(conn, table)}")
        lines.append("")
    finally:
        conn.close()

    return "\n".join(lines)


def _count_if_exists(db_path: Path, table: str) -> int:
    if not db_path.exists():
        return 0
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(f"SELECT COUNT(*) FROM {table};").fetchone()
        return int(row[0]) if row else 0
    except sqlite3.DatabaseError:
        return 0
    finally:
        conn.close()


def _render_cross_db_flow(paths: dict[str, Path]) -> str:
    history_path = paths["history"]
    vector_path = paths["vector"]
    memory_path = paths["memory"]

    chat_count = _count_if_exists(history_path, "chat_messages")
    eval_count = _count_if_exists(history_path, "eval_checkpoints")
    vector_count = _count_if_exists(vector_path, "message_vectors")
    memory_session_count = _count_if_exists(memory_path, "agent_sessions")
    memory_message_count = _count_if_exists(memory_path, "agent_messages")

    lines: list[str] = []
    lines.append("## Runtime Data Flow (Cross-DB)")
    lines.append("")
    lines.append(
        "Logical relationships across runtime stores. These are application-level links, not SQLite foreign keys."
    )
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart LR")
    lines.append('  subgraph H["History DB"]')
    lines.append(f'    H1["chats ({_count_if_exists(history_path, "chats")})"]')
    lines.append(f'    H2["chat_messages ({chat_count})"]')
    lines.append(f'    H3["eval_checkpoints ({eval_count})"]')
    lines.append("    H1 --> H2")
    lines.append("    H1 --> H3")
    lines.append("  end")
    lines.append("")
    lines.append('  subgraph V["Vector DB"]')
    lines.append(f'    V1["message_vectors ({vector_count})"]')
    lines.append("  end")
    lines.append("")
    lines.append('  subgraph M["Memory DB"]')
    lines.append(f'    M1["agent_sessions ({memory_session_count})"]')
    lines.append(f'    M2["agent_messages ({memory_message_count})"]')
    lines.append("    M1 --> M2")
    lines.append("  end")
    lines.append("")
    lines.append('  H2 -->|"message_id/session_id"| V1')
    lines.append('  H1 -->|"session_id"| M1')
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def build_visuals(dotenv_path: Path, output: Path) -> None:
    paths = _resolve_db_paths(dotenv_path)

    lines: list[str] = []
    lines.append("# Runtime DB Visuals")
    lines.append("")
    lines.append(
        "Generated ER-style visuals for runtime SQLite stores (history, vector, memory)."
    )
    lines.append("")
    lines.append(f"- generated_utc: {datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append("")
    lines.append(_render_cross_db_flow(paths))

    lines.append(_render_db_section("History DB", paths["history"]))
    lines.append(_render_db_section("Vector DB", paths["vector"]))
    lines.append(_render_db_section("Memory DB", paths["memory"]))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build runtime DB Mermaid visuals.")
    parser.add_argument("--dotenv", default=".env", help="Path to dotenv file.")
    parser.add_argument(
        "--output",
        default="docs/RUNTIME_DB_VISUALS.md",
        help="Output markdown path.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    build_visuals(dotenv_path=Path(args.dotenv), output=Path(args.output))
    print(f"Runtime DB visuals written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
