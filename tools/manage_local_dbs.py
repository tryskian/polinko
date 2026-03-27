from __future__ import annotations

import argparse
import shutil
from datetime import UTC, datetime
from pathlib import Path

from dotenv import dotenv_values

from core.history_store import ChatHistoryStore
from core.runtime import create_session
from core.vector_store import VectorStore


def _normalize_env_value(value: str | None, default: str) -> str:
    if value is None:
        return default
    raw = value.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {'"', "'"}:
        raw = raw[1:-1].strip()
    return raw or default


def _resolve_db_paths(dotenv_path: Path) -> dict[str, Path]:
    env = dotenv_values(dotenv_path)
    memory = _normalize_env_value(env.get("POLINKO_MEMORY_DB_PATH"), ".polinko_memory.db")
    history = _normalize_env_value(env.get("POLINKO_HISTORY_DB_PATH"), ".polinko_history.db")
    vector = _normalize_env_value(env.get("POLINKO_VECTOR_DB_PATH"), ".polinko_vector.db")
    return {
        "memory": Path(memory),
        "history": Path(history),
        "vector": Path(vector),
    }


def _remove_sqlite_family(db_path: Path) -> list[Path]:
    removed: list[Path] = []
    for candidate in (db_path, Path(f"{db_path}-shm"), Path(f"{db_path}-wal")):
        if candidate.exists():
            candidate.unlink()
            removed.append(candidate)
    return removed


def _ensure_parent(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _sqlite_family(db_path: Path) -> tuple[Path, Path, Path]:
    return (db_path, Path(f"{db_path}-shm"), Path(f"{db_path}-wal"))


def reset_dbs(paths: dict[str, Path]) -> None:
    for name, raw_path in paths.items():
        path = _ensure_parent(raw_path)
        removed = _remove_sqlite_family(path)
        if removed:
            print(f"{name}: removed {', '.join(str(item) for item in removed)}")
        else:
            print(f"{name}: already clean ({path})")


def init_dbs(paths: dict[str, Path]) -> None:
    history_path = _ensure_parent(paths["history"])
    vector_path = _ensure_parent(paths["vector"])
    memory_path = _ensure_parent(paths["memory"])

    ChatHistoryStore(str(history_path))
    VectorStore(str(vector_path))
    session = create_session(session_id="db-init", db_path=str(memory_path), limit=1)
    session.close()

    print(f"history: initialised {history_path}")
    print(f"vector: initialised {vector_path}")
    print(f"memory: initialised {memory_path}")


def archive_dbs(paths: dict[str, Path], archive_dir: Path) -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%SZ")
    snapshot_dir = archive_dir / stamp
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    moved_any = False

    for name, raw_path in paths.items():
        db_path = _ensure_parent(raw_path)
        family = _sqlite_family(db_path)
        name_dir = snapshot_dir / name
        name_dir.mkdir(parents=True, exist_ok=True)
        moved_for_name = 0
        for source in family:
            if not source.exists():
                continue
            destination = name_dir / source.name
            shutil.move(str(source), str(destination))
            moved_for_name += 1
            moved_any = True
        if moved_for_name > 0:
            print(f"{name}: archived to {name_dir}")
        else:
            print(f"{name}: nothing to archive")

    if moved_any:
        print(f"archive snapshot: {snapshot_dir}")
    else:
        print("archive snapshot: nothing archived")
    return snapshot_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage local Polinko SQLite DB baselines.")
    parser.add_argument(
        "action",
        choices=["reset", "init", "refresh", "archive", "archive-refresh"],
        help="Operation to run.",
    )
    parser.add_argument(
        "--dotenv",
        default=".env",
        help="Path to dotenv file used for db path resolution.",
    )
    parser.add_argument(
        "--archive-dir",
        default=".local_archive/runtime_dbs",
        help="Directory where DB archive snapshots are stored.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    paths = _resolve_db_paths(Path(args.dotenv))
    archive_dir = Path(args.archive_dir)

    if args.action == "reset":
        reset_dbs(paths)
    elif args.action == "init":
        init_dbs(paths)
    elif args.action == "refresh":
        reset_dbs(paths)
        init_dbs(paths)
    elif args.action == "archive":
        archive_dbs(paths, archive_dir=archive_dir)
    else:
        archive_dbs(paths, archive_dir=archive_dir)
        init_dbs(paths)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
