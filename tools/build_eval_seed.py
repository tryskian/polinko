import argparse
import csv
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


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
    for key in ("content", "text", "message", "output", "input"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _extract_turn_from_row(row: dict[str, Any], *, fallback_conversation: str, seq: int) -> dict[str, Any] | None:
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

    conversation_id = str(
        row.get("conversation_id")
        or row.get("chat_id")
        or row.get("thread_id")
        or fallback_conversation
    )
    turn_id = str(row.get("turn_id") or row.get("id") or f"turn_{seq:06d}")
    timestamp = str(row.get("timestamp") or row.get("created_at") or row.get("time") or "")

    return {
        "conversation_id": conversation_id,
        "turn_id": turn_id,
        "role": role,
        "text": text,
        "timestamp": timestamp,
        "seq": seq,
    }


def _load_turns_from_csv(path: Path) -> list[dict[str, Any]]:
    turns: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for seq, row in enumerate(reader):
            turn = _extract_turn_from_row(row, fallback_conversation=path.stem, seq=seq)
            if turn:
                turns.append(turn)
    return turns


def _iter_json_turns(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        if isinstance(payload.get("turns"), list):
            return [item for item in payload["turns"] if isinstance(item, dict)]
        if isinstance(payload.get("messages"), list):
            return [item for item in payload["messages"] if isinstance(item, dict)]
        if isinstance(payload.get("conversations"), list):
            turns: list[dict[str, Any]] = []
            for conversation in payload["conversations"]:
                if not isinstance(conversation, dict):
                    continue
                for key in ("turns", "messages"):
                    raw_turns = conversation.get(key)
                    if isinstance(raw_turns, list):
                        for item in raw_turns:
                            if isinstance(item, dict):
                                if "conversation_id" not in item and conversation.get("id"):
                                    item = dict(item)
                                    item["conversation_id"] = conversation["id"]
                                turns.append(item)
            return turns
    return []


def _load_turns_from_json(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    turns: list[dict[str, Any]] = []
    for seq, row in enumerate(_iter_json_turns(payload)):
        turn = _extract_turn_from_row(row, fallback_conversation=path.stem, seq=seq)
        if turn:
            turns.append(turn)
    return turns


def load_turns(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        return _load_turns_from_csv(path)
    if path.suffix.lower() == ".json":
        return _load_turns_from_json(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")


def build_seed_cases(
    turns: list[dict[str, Any]],
    *,
    max_cases: int,
    min_user_chars: int,
    min_assistant_chars: int,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for turn in turns:
        grouped[str(turn["conversation_id"])].append(turn)

    cases: list[dict[str, Any]] = []
    case_counter = 1
    for conversation_id, conversation_turns in grouped.items():
        sorted_turns = sorted(conversation_turns, key=lambda turn: (turn.get("timestamp", ""), turn["seq"]))
        pending_user: dict[str, Any] | None = None
        for turn in sorted_turns:
            if turn["role"] == "user":
                pending_user = turn
                continue

            if turn["role"] != "assistant" or pending_user is None:
                continue

            user_text = str(pending_user["text"]).strip()
            assistant_text = str(turn["text"]).strip()
            if len(user_text) < min_user_chars or len(assistant_text) < min_assistant_chars:
                pending_user = None
                continue

            cases.append(
                {
                    "id": f"seed_{case_counter:04d}",
                    "conversation_id": conversation_id,
                    "input_turn_id": pending_user["turn_id"],
                    "output_turn_id": turn["turn_id"],
                    "input": user_text,
                    "reference_output": assistant_text,
                }
            )
            case_counter += 1
            pending_user = None

            if len(cases) >= max_cases:
                return cases
    return cases


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build candidate eval seed pairs from transcript exports.")
    parser.add_argument("input_path", help="Path to transcript_turns.csv or normalized JSON export.")
    parser.add_argument(
        "--output",
        default="configs/eval_seed.json",
        help="Output JSON path (default: configs/eval_seed.json).",
    )
    parser.add_argument("--max-cases", type=int, default=200, help="Maximum seed cases to emit.")
    parser.add_argument("--min-user-chars", type=int, default=12, help="Minimum user message length.")
    parser.add_argument("--min-assistant-chars", type=int, default=24, help="Minimum assistant message length.")
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

    cases = build_seed_cases(
        turns,
        max_cases=args.max_cases,
        min_user_chars=args.min_user_chars,
        min_assistant_chars=args.min_assistant_chars,
    )
    payload = {
        "version": "eval-seed-v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "source": str(input_path),
        "case_count": len(cases),
        "cases": cases,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(cases)} cases to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
