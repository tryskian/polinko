import asyncio
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

Runner: Any
APIConnectionError: type[Exception]
APIStatusError: type[Exception]
AuthenticationError: type[Exception]
RateLimitError: type[Exception]
load_config: Any
ChatHistoryStore: Any
create_agent: Any
create_run_config: Any
create_session: Any

try:
    from agents import Runner
    from openai import APIConnectionError, APIStatusError, AuthenticationError, RateLimitError
    from config import load_config
    from core.history_store import ChatHistoryStore
    from core.runtime import create_agent, create_run_config, create_session
except ModuleNotFoundError as exc:
    # If launched with the wrong interpreter, restart with the project virtualenv python.
    project_venv = Path(__file__).resolve().parent / "polinko-repositioning-system"
    project_python = project_venv / "bin" / "python"
    current_prefix = Path(sys.prefix).resolve()
    if project_python.exists() and current_prefix != project_venv.resolve():
        os.execv(str(project_python), [str(project_python), __file__, *sys.argv[1:]])

    missing = exc.name or "a required package"
    raise SystemExit(
        f"Missing dependency: {missing}. "
        "Use the project interpreter at polinko-repositioning-system/bin/python "
        "or run: source polinko-repositioning-system/bin/activate"
    ) from exc

from core.prompts import ACTIVE_PROMPT_VERSION  # noqa: E402

config = load_config(dotenv_path=".env")
agent = create_agent()
run_config = create_run_config(store=True)
current_session_id = (
    os.getenv("NAUTORUS_CLI_SESSION_ID")
    or os.getenv("POLINKO_CLI_SESSION_ID")
    or config.default_session_id
)
session = create_session(
    session_id=current_session_id,
    db_path=config.session_db_path,
    limit=80,
)
history_store = ChatHistoryStore(config.history_db_path)
history_store.ensure_chat(session_id=current_session_id)


def _safe_session_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return slug or "chat"


def _default_export_path(session_id: str) -> Path:
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d-%H%M%S")
    filename = f"{_safe_session_slug(session_id)}-{timestamp}.md"
    return Path("exports") / filename


def _format_md(messages: list[object], *, session_id: str) -> str:
    lines: list[str] = [
        f"# Transcript: {session_id}",
        f"Exported: {datetime.now(tz=timezone.utc).isoformat()}",
        "",
    ]
    for message in messages:
        role = getattr(message, "role", "unknown").capitalize()
        content = getattr(message, "content", "")
        lines.extend([f"## {role}", str(content), ""])
    return "\n".join(lines).rstrip() + "\n"


def _format_txt(messages: list[object]) -> str:
    lines: list[str] = []
    for message in messages:
        role = getattr(message, "role", "unknown")
        created_at = getattr(message, "created_at", 0)
        stamp = datetime.fromtimestamp(int(created_at) / 1000, tz=timezone.utc).isoformat()
        lines.append(f"[{stamp}] {role}: {getattr(message, 'content', '')}")
    return "\n\n".join(lines).rstrip() + "\n"


def _format_json(messages: list[object]) -> str:
    payload = [
        {
            "message_id": getattr(message, "message_id", ""),
            "parent_message_id": getattr(message, "parent_message_id", None),
            "role": getattr(message, "role", ""),
            "content": getattr(message, "content", ""),
            "created_at": getattr(message, "created_at", 0),
        }
        for message in messages
    ]
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def export_transcript(session_id: str, target: str | None = None) -> Path:
    messages = history_store.list_messages(session_id=session_id)
    if not messages:
        raise RuntimeError("No messages in this session yet.")

    destination = Path(target).expanduser() if target else _default_export_path(session_id)
    if destination.suffix.lower() not in {".md", ".txt", ".json"}:
        destination = destination.with_suffix(".md")
    destination.parent.mkdir(parents=True, exist_ok=True)

    suffix = destination.suffix.lower()
    if suffix == ".txt":
        rendered = _format_txt(messages)
    elif suffix == ".json":
        rendered = _format_json(messages)
    else:
        rendered = _format_md(messages, session_id=session_id)
    destination.write_text(rendered, encoding="utf-8")
    return destination


def _new_cli_session_id() -> str:
    return f"cli-{uuid.uuid4().hex[:8]}"


def _switch_session(session_id: str) -> Any:
    next_session = create_session(
        session_id=session_id,
        db_path=config.session_db_path,
        limit=80,
    )
    history_store.ensure_chat(session_id=session_id)
    return next_session


def _print_chats(session_id: str) -> None:
    chats = history_store.list_chats()
    if not chats:
        print("No active chats.")
        return
    print("Active chats:")
    for chat in chats[:20]:
        marker = "*" if chat.session_id == session_id else " "
        print(f"{marker} {chat.session_id} | {chat.title} ({chat.message_count})")

print(f"Loaded prompt version: {ACTIVE_PROMPT_VERSION}")
print(f"Session: {current_session_id}")
print("Commands: /chats, /switch <id>, /rename <title>, /close, /reset, /export [path], exit")

while True:
    user_input = input("> ")
    trimmed_input = user_input.strip()
    lowered = trimmed_input.lower()
    if lowered in ("exit", "quit"):
        break

    if lowered == "/chats":
        _print_chats(current_session_id)
        continue

    if lowered.startswith("/switch "):
        target_session_id = trimmed_input[len("/switch") :].strip()
        if not target_session_id:
            print("Usage: /switch <session-id>")
            continue
        target = history_store.get_chat(target_session_id)
        if target is None:
            print(f"Chat not found: {target_session_id}")
            continue
        if target.status == "deprecated":
            print(f"Chat is deprecated and cannot be opened: {target_session_id}")
            continue
        current_session_id = target_session_id
        session = _switch_session(current_session_id)
        print(f"Switched to {current_session_id}")
        continue

    if lowered.startswith("/rename "):
        next_title = trimmed_input[len("/rename") :].strip()
        if not next_title:
            print("Usage: /rename <new title>")
            continue
        try:
            renamed = history_store.rename_chat(current_session_id, next_title)
        except KeyError:
            print(f"Chat not found: {current_session_id}")
            continue
        print(f'Renamed "{renamed.title}"')
        continue

    if lowered == "/close":
        try:
            history_store.deprecate_chat(current_session_id)
        except KeyError:
            print(f"Chat not found: {current_session_id}")
            continue
        asyncio.run(session.clear_session())
        previous_session_id = current_session_id
        current_session_id = _new_cli_session_id()
        session = _switch_session(current_session_id)
        print(f"Closed {previous_session_id}. Switched to {current_session_id}")
        continue

    if lowered == "/reset":
        asyncio.run(session.clear_session())
        history_store.clear_messages(session_id=current_session_id)
        print("Memory cleared.")
        continue

    if lowered.startswith("/export"):
        raw_target = trimmed_input[len("/export") :].strip()
        try:
            exported = export_transcript(current_session_id, raw_target or None)
        except RuntimeError as exc:
            print(str(exc))
            continue
        print(f"Transcript exported to {exported}")
        continue

    try:
        response = Runner.run_sync(agent, user_input, run_config=run_config, session=session)
    except AuthenticationError:
        print("Authentication failed. Check OPENAI_API_KEY in .env.")
        continue
    except RateLimitError:
        print("Rate limit reached. Wait a moment and try again.")
        continue
    except APIConnectionError:
        print("Connection error reaching OpenAI API. Check internet/VPN/firewall and try again.")
        continue
    except APIStatusError as exc:
        status_code = getattr(exc, "status_code", "unknown")
        print(f"OpenAI API error ({status_code}). Try again in a moment.")
        continue

    history_store.append_message(session_id=current_session_id, role="user", content=user_input)
    history_store.append_message(session_id=current_session_id, role="assistant", content=str(response.final_output))
    history_store.maybe_set_title_from_first_user_message(
        session_id=current_session_id,
        user_message=user_input,
    )
    print(response.final_output)
