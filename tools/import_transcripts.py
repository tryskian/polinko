from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openai import OpenAI

from config import load_config
from core.vector_store import VectorStore


GLOBAL_MEMORY_LANE_SESSION_ID = "__global_memory__"


@dataclass(frozen=True)
class TranscriptTurn:
    conversation_id: str
    title: str
    turn_id: str
    role: str
    text: str
    created_at_ms: int
    parent_turn_id: str | None
    turn_index: int


def _now_ms() -> int:
    return int(time.time() * 1000)


def _to_ms_timestamp(value: Any) -> int:
    if value is None:
        return _now_ms()
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return _now_ms()
    # Heuristic: values < 1e11 are likely seconds; otherwise milliseconds.
    return int(numeric * 1000) if numeric < 1e11 else int(numeric)


def _extract_text_content(raw: Any) -> str:
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, list):
        parts: list[str] = []
        for item in raw:
            text = _extract_text_content(item)
            if text:
                parts.append(text)
        return "\n".join(parts).strip()
    if isinstance(raw, dict):
        # OpenAI-style: {"parts": [...]}
        if "parts" in raw:
            return _extract_text_content(raw.get("parts"))
        # Generic: {"text": "..."}
        if "text" in raw:
            return _extract_text_content(raw.get("text"))
        # Rich content blocks
        if "content" in raw:
            return _extract_text_content(raw.get("content"))
        if "value" in raw:
            return _extract_text_content(raw.get("value"))
    return ""


def _conversation_title(conversation: dict[str, Any], fallback: str) -> str:
    for key in ("title", "name", "chat_title"):
        value = conversation.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _conversation_id(conversation: dict[str, Any], fallback: str) -> str:
    for key in ("conversation_id", "id", "thread_id", "session_id", "chat_id"):
        value = conversation.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _extract_role(message: dict[str, Any]) -> str:
    direct = message.get("role")
    if isinstance(direct, str) and direct.strip():
        return direct.strip().lower()
    author = message.get("author")
    if isinstance(author, dict):
        role = author.get("role")
        if isinstance(role, str) and role.strip():
            return role.strip().lower()
    return ""


def _parse_openai_mapping_conversation(
    conversation: dict[str, Any],
    *,
    fallback_id: str,
    fallback_title: str,
) -> list[TranscriptTurn]:
    mapping = conversation.get("mapping")
    if not isinstance(mapping, dict):
        return []

    conv_id = _conversation_id(conversation, fallback_id)
    title = _conversation_title(conversation, fallback_title)

    raw_turns: list[tuple[int, str, str, str, int, str | None]] = []
    for node_key, node in mapping.items():
        if not isinstance(node, dict):
            continue
        message = node.get("message")
        if not isinstance(message, dict):
            continue
        role = _extract_role(message)
        if role not in {"assistant", "user", "system"}:
            continue
        text = _extract_text_content(message.get("content"))
        if not text:
            continue
        turn_id_raw = message.get("id")
        turn_id = (
            turn_id_raw.strip()
            if isinstance(turn_id_raw, str) and turn_id_raw.strip()
            else str(node_key)
        )
        created_at_ms = _to_ms_timestamp(message.get("create_time"))
        parent_raw = node.get("parent")
        parent_turn_id = parent_raw.strip() if isinstance(parent_raw, str) and parent_raw.strip() else None
        raw_turns.append((created_at_ms, turn_id, role, text, len(raw_turns), parent_turn_id))

    # Stable ordering: timestamp, then discovery order.
    raw_turns.sort(key=lambda item: (item[0], item[4]))
    turns: list[TranscriptTurn] = []
    for idx, (created_at_ms, turn_id, role, text, _, parent_turn_id) in enumerate(raw_turns):
        turns.append(
            TranscriptTurn(
                conversation_id=conv_id,
                title=title,
                turn_id=turn_id,
                role=role,
                text=text,
                created_at_ms=created_at_ms,
                parent_turn_id=parent_turn_id,
                turn_index=idx,
            )
        )
    return turns


def _parse_messages_conversation(
    conversation: dict[str, Any],
    *,
    fallback_id: str,
    fallback_title: str,
) -> list[TranscriptTurn]:
    messages_obj = conversation.get("messages")
    if not isinstance(messages_obj, list):
        return []

    conv_id = _conversation_id(conversation, fallback_id)
    title = _conversation_title(conversation, fallback_title)
    turns: list[TranscriptTurn] = []
    for idx, raw_message in enumerate(messages_obj):
        if not isinstance(raw_message, dict):
            continue
        role = _extract_role(raw_message)
        if role not in {"assistant", "user", "system"}:
            continue
        text = _extract_text_content(raw_message.get("content") or raw_message.get("text"))
        if not text:
            continue
        turn_id_raw = raw_message.get("message_id") or raw_message.get("id")
        turn_id = (
            turn_id_raw.strip()
            if isinstance(turn_id_raw, str) and turn_id_raw.strip()
            else f"{conv_id}:turn:{idx + 1}"
        )
        parent_raw = raw_message.get("parent_message_id") or raw_message.get("parent_id")
        parent_turn_id = parent_raw.strip() if isinstance(parent_raw, str) and parent_raw.strip() else None
        created_at_ms = _to_ms_timestamp(raw_message.get("created_at") or raw_message.get("create_time"))
        turns.append(
            TranscriptTurn(
                conversation_id=conv_id,
                title=title,
                turn_id=turn_id,
                role=role,
                text=text,
                created_at_ms=created_at_ms,
                parent_turn_id=parent_turn_id,
                turn_index=idx,
            )
        )
    return turns


def _parse_conversation_payload(payload: dict[str, Any], fallback: str) -> list[TranscriptTurn]:
    turns = _parse_messages_conversation(payload, fallback_id=fallback, fallback_title=fallback)
    if turns:
        return turns
    turns = _parse_openai_mapping_conversation(payload, fallback_id=fallback, fallback_title=fallback)
    if turns:
        return turns
    return []


def _load_turns_from_json_file(path: Path) -> list[TranscriptTurn]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    fallback_id = path.stem
    if isinstance(payload, dict):
        return _parse_conversation_payload(payload, fallback_id)
    if isinstance(payload, list):
        turns: list[TranscriptTurn] = []
        for idx, item in enumerate(payload):
            if not isinstance(item, dict):
                continue
            item_fallback = f"{fallback_id}:{idx + 1}"
            turns.extend(_parse_conversation_payload(item, item_fallback))
        return turns
    return []


def _chunk_text(text: str, *, max_chars: int, overlap: int) -> list[str]:
    compact = text.strip()
    if not compact:
        return []
    if len(compact) <= max_chars:
        return [compact]

    chunks: list[str] = []
    start = 0
    while start < len(compact):
        end = min(len(compact), start + max_chars)
        if end < len(compact):
            split_at = compact.rfind("\n", start, end)
            if split_at <= start:
                split_at = compact.rfind(" ", start, end)
            if split_at > start + int(max_chars * 0.55):
                end = split_at
        chunk = compact[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(compact):
            break
        start = max(0, end - overlap)
    return chunks


def _iter_json_files(root: Path, *, recursive: bool, max_files: int | None) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix.lower() == ".json" else []
    if not root.exists() or not root.is_dir():
        return []
    iterator = root.rglob("*.json") if recursive else root.glob("*.json")
    files = sorted(path for path in iterator if path.is_file())
    if max_files is not None:
        return files[: max(0, max_files)]
    return files


def _build_import_message_id(
    *,
    source_platform: str,
    conversation_id: str,
    turn_id: str,
    chunk_index: int,
    content: str,
) -> str:
    payload = f"{source_platform}|{conversation_id}|{turn_id}|{chunk_index}|{content}".encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()[:30]
    return f"imp_{digest}"


def _embed_batch(client: OpenAI, model: str, texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(model=model, input=texts)
    vectors: list[list[float]] = []
    for item in response.data:
        vectors.append([float(value) for value in item.embedding])
    if len(vectors) != len(texts):
        raise RuntimeError("Embedding response size mismatch during transcript import.")
    return vectors


def _collect_turns(
    *,
    input_path: Path,
    recursive: bool,
    max_files: int | None,
    include_user_turns: bool,
) -> tuple[list[TranscriptTurn], int]:
    files = _iter_json_files(input_path, recursive=recursive, max_files=max_files)
    turns: list[TranscriptTurn] = []
    for file_path in files:
        try:
            parsed = _load_turns_from_json_file(file_path)
        except Exception:
            continue
        if include_user_turns:
            turns.extend(turn for turn in parsed if turn.role in {"assistant", "user"})
        else:
            turns.extend(turn for turn in parsed if turn.role == "assistant")
    return turns, len(files)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import transcript JSON files into Nautorus vector memory for retrieval."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to transcript JSON file or directory (can be in another workspace).",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively scan --input for *.json files when --input is a directory.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Optional cap on number of JSON files scanned.",
    )
    parser.add_argument(
        "--include-user-turns",
        action="store_true",
        help="Also index user turns (default indexes assistant turns only).",
    )
    parser.add_argument(
        "--session-lane",
        choices=("global", "conversation"),
        default="global",
        help="Index to global lane (__global_memory__) or each source conversation lane.",
    )
    parser.add_argument(
        "--source-platform",
        default="transcript_import",
        help="Metadata label for provenance (e.g., chatgpt_export, claude_export).",
    )
    parser.add_argument(
        "--batch-tag",
        default=None,
        help="Optional provenance batch tag. Defaults to current UTC timestamp.",
    )
    parser.add_argument(
        "--chunk-max-chars",
        type=int,
        default=800,
        help="Max chars per indexed chunk.",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=120,
        help="Character overlap between chunks.",
    )
    parser.add_argument(
        "--embed-batch-size",
        type=int,
        default=32,
        help="Embedding batch size.",
    )
    parser.add_argument(
        "--dotenv-path",
        default=".env",
        help="Path to .env file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and report counts without writing vectors.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_path = Path(args.input).expanduser()
    if not input_path.exists():
        raise SystemExit(f"Input path not found: {input_path}")
    if args.chunk_max_chars < 120:
        raise SystemExit("--chunk-max-chars must be >= 120")
    if args.chunk_overlap < 0 or args.chunk_overlap >= args.chunk_max_chars:
        raise SystemExit("--chunk-overlap must be >= 0 and < --chunk-max-chars")
    if args.embed_batch_size <= 0:
        raise SystemExit("--embed-batch-size must be >= 1")

    turns, scanned_file_count = _collect_turns(
        input_path=input_path,
        recursive=args.recursive,
        max_files=args.max_files,
        include_user_turns=args.include_user_turns,
    )
    if not turns:
        print(f"No eligible turns found (files_scanned={scanned_file_count}).")
        return 0

    batch_tag = args.batch_tag or time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    print(
        f"Prepared turns={len(turns)} files_scanned={scanned_file_count} "
        f"include_user_turns={args.include_user_turns} session_lane={args.session_lane}"
    )
    if args.dry_run:
        print("Dry run complete. No vectors written.")
        return 0

    config = load_config(args.dotenv_path)
    vector_store = VectorStore(config.vector_db_path)
    client = OpenAI(api_key=config.openai_api_key)

    queued_rows: list[tuple[str, str, str, str, str, dict[str, Any], int]] = []
    for turn in turns:
        chunks = _chunk_text(
            turn.text,
            max_chars=args.chunk_max_chars,
            overlap=args.chunk_overlap,
        )
        chunk_count = len(chunks)
        if chunk_count == 0:
            continue
        for chunk_index, chunk in enumerate(chunks):
            lane_session_id = (
                GLOBAL_MEMORY_LANE_SESSION_ID
                if args.session_lane == "global"
                else turn.conversation_id
            )
            message_id = _build_import_message_id(
                source_platform=args.source_platform,
                conversation_id=turn.conversation_id,
                turn_id=turn.turn_id,
                chunk_index=chunk_index,
                content=chunk,
            )
            source_ref = f"{turn.turn_id}:{chunk_index + 1}/{chunk_count}"
            metadata = {
                "source": "chat",
                "source_platform": args.source_platform,
                "import_batch": batch_tag,
                "conversation_id": turn.conversation_id,
                "conversation_title": turn.title,
                "turn_id": turn.turn_id,
                "turn_index": turn.turn_index,
                "original_role": turn.role,
                "origin_session_id": turn.conversation_id,
                "chunk_index": chunk_index,
                "chunk_count": chunk_count,
                "imported": True,
            }
            queued_rows.append(
                (
                    lane_session_id,
                    "assistant",
                    message_id,
                    source_ref,
                    chunk,
                    metadata,
                    turn.created_at_ms,
                )
            )

    if not queued_rows:
        print("No chunks produced from parsed turns.")
        return 0

    print(f"Indexing chunks={len(queued_rows)} model={config.vector_embedding_model} ...")
    indexed = 0
    for batch_start in range(0, len(queued_rows), args.embed_batch_size):
        batch = queued_rows[batch_start : batch_start + args.embed_batch_size]
        vectors = _embed_batch(
            client,
            config.vector_embedding_model,
            [item[4] for item in batch],
        )
        for (row, embedding) in zip(batch, vectors):
            lane_session_id, role, message_id, source_ref, chunk, metadata, created_at_ms = row
            vector_store.upsert_message_vector(
                session_id=lane_session_id,
                role=role,
                message_id=message_id,
                content=chunk,
                embedding=embedding,
                source_type="chat",
                source_ref=source_ref,
                metadata=metadata,
                created_at=created_at_ms,
            )
            indexed += 1

    print(
        f"Import complete: indexed_chunks={indexed} "
        f"turns={len(turns)} files_scanned={scanned_file_count} "
        f"batch={batch_tag} lane={args.session_lane}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
