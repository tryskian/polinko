from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})")
LINK_RE = re.compile(r"`(docs/(?:transcripts|theory|research)/[^`]+\.md)`")


def _now_utc_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def _extract_date_iso(path: Path, text: str) -> str | None:
    match = DATE_RE.search(path.name)
    if match:
        return match.group(1)
    first_lines = "\n".join(text.splitlines()[:20])
    match = DATE_RE.search(first_lines)
    if match:
        return match.group(1)
    return None


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


@dataclass(frozen=True)
class HumanDoc:
    path: str
    category: str
    title: str
    captured_on: str | None
    content: str
    sha256: str
    word_count: int
    modified_utc: str


def _category_for(path: Path) -> str:
    p = path.as_posix()
    if p.startswith("docs/peanut/transcripts/"):
        if "key_points" in path.name:
            return "key_points"
        return "transcripts"
    if p.startswith("docs/peanut/theory/"):
        return "theory_notes"
    if p.startswith("docs/peanut/research/"):
        return "research_notes"
    return "other_notes"


def _iter_markdown_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def _collect_docs(repo_root: Path, roots: list[str]) -> list[HumanDoc]:
    docs: list[HumanDoc] = []
    for rel_root in roots:
        base = repo_root / rel_root
        for path in _iter_markdown_files(base):
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(repo_root).as_posix()
            modified_utc = datetime.fromtimestamp(path.stat().st_mtime, UTC).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            docs.append(
                HumanDoc(
                    path=rel,
                    category=_category_for(Path(rel)),
                    title=_extract_title(text, path.stem),
                    captured_on=_extract_date_iso(path, text),
                    content=text,
                    sha256=_sha256_text(text),
                    word_count=_word_count(text),
                    modified_utc=modified_utc,
                )
            )
    return docs


SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    captured_on TEXT,
    content TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    modified_utc TEXT NOT NULL,
    indexed_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);
CREATE INDEX IF NOT EXISTS idx_documents_captured_on ON documents(captured_on);

CREATE VIEW IF NOT EXISTS v_human_reference_latest AS
SELECT
    category,
    title,
    path,
    captured_on,
    modified_utc,
    word_count
FROM documents
ORDER BY COALESCE(captured_on, modified_utc) DESC, path ASC;
"""

LINKS_SCHEMA_SQL = """
DROP TABLE IF EXISTS links;

CREATE TABLE links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_path TEXT NOT NULL,
    target_path TEXT NOT NULL,
    relation TEXT NOT NULL DEFAULT 'references',
    note TEXT DEFAULT '',
    UNIQUE(source_path, target_path, relation),
    FOREIGN KEY (source_path) REFERENCES documents(path) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (target_path) REFERENCES documents(path) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_links_source ON links(source_path);
CREATE INDEX idx_links_target ON links(target_path);
"""


def _reset_links_table(conn: sqlite3.Connection) -> None:
    # Recreate links each build so ER tools can rely on explicit FK relationships.
    conn.executescript(LINKS_SCHEMA_SQL)


def _rebuild_links(conn: sqlite3.Connection, docs: list[HumanDoc]) -> None:
    doc_paths = {doc.path for doc in docs}
    conn.execute("DELETE FROM links")
    insert_sql = """
        INSERT OR IGNORE INTO links (source_path, target_path, relation, note)
        VALUES (?, ?, 'references', '')
    """
    for doc in docs:
        for match in LINK_RE.findall(doc.content):
            if match in doc_paths and match != doc.path:
                conn.execute(insert_sql, (doc.path, match))


def _upsert_docs(conn: sqlite3.Connection, docs: list[HumanDoc]) -> None:
    upsert_sql = """
        INSERT INTO documents (
            path, category, title, captured_on, content, sha256, word_count, modified_utc, indexed_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            category=excluded.category,
            title=excluded.title,
            captured_on=excluded.captured_on,
            content=excluded.content,
            sha256=excluded.sha256,
            word_count=excluded.word_count,
            modified_utc=excluded.modified_utc,
            indexed_utc=excluded.indexed_utc
    """
    now = _now_utc_iso()
    seen_paths: set[str] = set()
    for doc in docs:
        seen_paths.add(doc.path)
        conn.execute(
            upsert_sql,
            (
                doc.path,
                doc.category,
                doc.title,
                doc.captured_on,
                doc.content,
                doc.sha256,
                doc.word_count,
                doc.modified_utc,
                now,
            ),
        )
    if seen_paths:
        placeholders = ",".join("?" for _ in seen_paths)
        conn.execute(f"DELETE FROM documents WHERE path NOT IN ({placeholders})", tuple(seen_paths))
    else:
        conn.execute("DELETE FROM documents")


def build_db(repo_root: Path, output_db: Path, roots: list[str]) -> None:
    docs = _collect_docs(repo_root, roots)
    output_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(output_db) as conn:
        conn.executescript(SCHEMA_SQL)
        _reset_links_table(conn)
        _upsert_docs(conn, docs)
        _rebuild_links(conn, docs)
        conn.execute(
            "INSERT INTO metadata(key, value) VALUES('last_index_utc', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (_now_utc_iso(),),
        )
        conn.execute(
            "INSERT INTO metadata(key, value) VALUES('roots', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (",".join(roots),),
        )
        conn.commit()
        counts = dict(conn.execute("SELECT category, COUNT(*) FROM documents GROUP BY category").fetchall())
        link_count = conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
    print(f"Built human reference DB: {output_db}")
    print(f"Indexed docs: {len(docs)}")
    for category in sorted(counts):
        print(f"  - {category}: {counts[category]}")
    print(f"Indexed links: {link_count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build local human-reference SQLite DB for portfolio browsing.")
    parser.add_argument(
        "--output-db",
        default=".human_reference.db",
        help="Output SQLite database path (default: .human_reference.db)",
    )
    parser.add_argument(
        "--roots",
        nargs="+",
        default=["docs/transcripts", "docs/research", "docs/theory"],
        help="Relative roots to ingest (default: docs/transcripts docs/research docs/theory)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    build_db(repo_root=repo_root, output_db=repo_root / args.output_db, roots=args.roots)


if __name__ == "__main__":
    main()
