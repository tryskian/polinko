import argparse
import csv
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


PREFERENCE_PATTERN = re.compile(
    r"\b("
    r"i prefer|i'd prefer|i would prefer|i like|i dislike|i hate|i love|"
    r"please|don't|do not|never|always|use|avoid|no follow up|"
    r"uk english|detached|observer"
    r")\b",
    flags=re.IGNORECASE,
)


def _normalize_role(value: str | None) -> str | None:
    if not value:
        return None
    lowered = value.strip().lower()
    if lowered in {"user", "human"}:
        return "user"
    if lowered in {"assistant", "ai", "model"}:
        return "assistant"
    return None


def _extract_text(row: dict[str, Any]) -> str:
    for key in ("content", "text", "message", "input"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _extract_turn(row: dict[str, Any], *, fallback_conversation: str, seq: int) -> dict[str, Any] | None:
    role = _normalize_role(
        str(
            row.get("role")
            or row.get("speaker")
            or row.get("author_role")
            or row.get("author")
            or ""
        )
    )
    if role is None:
        return None

    text = _extract_text(row)
    if not text:
        return None

    return {
        "conversation_id": str(
            row.get("conversation_id")
            or row.get("chat_id")
            or row.get("thread_id")
            or fallback_conversation
        ),
        "turn_id": str(row.get("turn_id") or row.get("id") or f"turn_{seq:06d}"),
        "role": role,
        "text": text,
        "seq": seq,
    }


def _load_rows_from_json(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        if isinstance(payload.get("turns"), list):
            return [item for item in payload["turns"] if isinstance(item, dict)]
        if isinstance(payload.get("messages"), list):
            return [item for item in payload["messages"] if isinstance(item, dict)]
        if isinstance(payload.get("conversations"), list):
            rows: list[dict[str, Any]] = []
            for conversation in payload["conversations"]:
                if not isinstance(conversation, dict):
                    continue
                for key in ("turns", "messages"):
                    raw_turns = conversation.get(key)
                    if not isinstance(raw_turns, list):
                        continue
                    for item in raw_turns:
                        if not isinstance(item, dict):
                            continue
                        if "conversation_id" not in item and conversation.get("id"):
                            item = dict(item)
                            item["conversation_id"] = conversation["id"]
                        rows.append(item)
            return rows
    return []


def load_turns(path: Path) -> list[dict[str, Any]]:
    turns: list[dict[str, Any]] = []
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for seq, row in enumerate(reader):
                turn = _extract_turn(row, fallback_conversation=path.stem, seq=seq)
                if turn:
                    turns.append(turn)
        return turns

    if path.suffix.lower() == ".json":
        for seq, row in enumerate(_load_rows_from_json(path)):
            turn = _extract_turn(row, fallback_conversation=path.stem, seq=seq)
            if turn:
                turns.append(turn)
        return turns

    raise ValueError(f"Unsupported file type: {path.suffix}")


def _split_sentences(text: str) -> list[str]:
    candidates = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [candidate.strip() for candidate in candidates if candidate.strip()]


def _tag_sentence(sentence: str) -> list[str]:
    lowered = sentence.lower()
    tags: list[str] = []
    if any(word in lowered for word in ("prefer", "like", "dislike", "love", "hate")):
        tags.append("preference")
    if any(word in lowered for word in ("avoid", "don't", "do not", "never", "no ")):
        tags.append("avoidance")
    if any(word in lowered for word in ("uk english", "tone", "detached", "observer")):
        tags.append("style")
    if "follow up" in lowered:
        tags.append("interaction")
    if not tags:
        tags.append("general")
    return tags


def build_memory_facts(turns: list[dict[str, Any]], *, max_facts: int) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    seen: set[str] = set()
    fact_counter = 1
    for turn in turns:
        if turn["role"] != "user":
            continue
        for sentence in _split_sentences(str(turn["text"])):
            if len(sentence) < 24 or len(sentence) > 240:
                continue
            if not PREFERENCE_PATTERN.search(sentence):
                continue
            normalized = re.sub(r"\s+", " ", sentence.lower()).strip()
            if normalized in seen:
                continue
            seen.add(normalized)
            facts.append(
                {
                    "id": f"fact_{fact_counter:04d}",
                    "text": sentence,
                    "tags": _tag_sentence(sentence),
                    "source": {
                        "conversation_id": turn["conversation_id"],
                        "turn_id": turn["turn_id"],
                    },
                }
            )
            fact_counter += 1
            if len(facts) >= max_facts:
                return facts
    return facts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract candidate memory facts from transcript exports.")
    parser.add_argument("input_path", help="Path to transcript_turns.csv or normalized JSON export.")
    parser.add_argument(
        "--output",
        default="configs/memory_facts.json",
        help="Output JSON path (default: configs/memory_facts.json).",
    )
    parser.add_argument("--max-facts", type=int, default=200, help="Maximum fact candidates to emit.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_path = Path(args.input_path)
    output_path = Path(args.output)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return 1

    turns = load_turns(input_path)
    if not turns:
        print("No valid turns found in input.")
        return 1

    facts = build_memory_facts(turns, max_facts=args.max_facts)
    payload = {
        "version": "memory-facts-v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "source": str(input_path),
        "fact_count": len(facts),
        "facts": facts,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(facts)} memory facts to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
