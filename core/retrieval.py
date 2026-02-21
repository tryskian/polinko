import json
import re
from pathlib import Path
from typing import Any


DEFAULT_MEMORY_FACTS_PATH = Path("configs/memory_facts.json")


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9']+", text.lower()) if len(token) >= 3}


def load_memory_facts(path: Path = DEFAULT_MEMORY_FACTS_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    raw_facts = data.get("facts", [])
    if not isinstance(raw_facts, list):
        return []

    facts: list[dict[str, Any]] = []
    for item in raw_facts:
        if isinstance(item, str):
            text = item.strip()
            if text:
                facts.append({"text": text, "tags": []})
            continue

        if isinstance(item, dict):
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            tags = item.get("tags", [])
            if not isinstance(tags, list):
                tags = []
            facts.append({"text": text, "tags": [str(tag).lower() for tag in tags]})

    return facts


def _score_fact(fact: dict[str, Any], message_tokens: set[str]) -> int:
    text = str(fact.get("text", ""))
    fact_tokens = _tokenize(text)
    overlap = len(message_tokens & fact_tokens)
    tag_bonus = 1 if fact.get("tags") else 0
    return overlap + tag_bonus


def select_relevant_facts(
    user_message: str,
    facts: list[dict[str, Any]],
    *,
    max_facts: int = 4,
) -> list[str]:
    if not facts:
        return []

    message_tokens = _tokenize(user_message)
    ranked = sorted(facts, key=lambda fact: _score_fact(fact, message_tokens), reverse=True)

    selected: list[str] = []
    for fact in ranked:
        text = str(fact.get("text", "")).strip()
        if not text or text in selected:
            continue
        selected.append(text)
        if len(selected) >= max_facts:
            break
    return selected


def build_augmented_user_message(
    user_message: str,
    *,
    memory_facts_path: Path = DEFAULT_MEMORY_FACTS_PATH,
    max_facts: int = 4,
) -> str:
    facts = load_memory_facts(memory_facts_path)
    selected_facts = select_relevant_facts(user_message, facts, max_facts=max_facts)
    if not selected_facts:
        return user_message

    fact_lines = "\n".join(f"- {fact}" for fact in selected_facts)
    return (
        "Persistent user context (use only if relevant; do not reference this block directly):\n"
        f"{fact_lines}\n\n"
        f"User message:\n{user_message}"
    )
