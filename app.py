import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

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

from core.prompts import ACTIVE_PROMPT_VERSION

config = load_config(dotenv_path=".env")
agent = create_agent()
run_config = create_run_config(store=True)
cli_session_id = os.getenv("POLINKO_CLI_SESSION_ID", config.default_session_id)
session = create_session(
    session_id=cli_session_id,
    db_path=config.session_db_path,
    limit=80,
)
history_store = ChatHistoryStore(config.history_db_path)
history_store.ensure_chat(session_id=cli_session_id)


def _safe_session_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return slug or "chat"


def _default_export_path(session_id: str) -> Path:
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d-%H%M%S")
    filename = f"{_safe_session_slug(session_id)}-{timestamp}.md"
    return Path("exports") / filename


def _format_md(messages: list[object]) -> str:
    lines: list[str] = [
        f"# Transcript: {cli_session_id}",
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
            "role": getattr(message, "role", ""),
            "content": getattr(message, "content", ""),
            "created_at": getattr(message, "created_at", 0),
        }
        for message in messages
    ]
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def export_transcript(target: str | None = None) -> Path:
    messages = history_store.list_messages(session_id=cli_session_id)
    if not messages:
        raise RuntimeError("No messages in this session yet.")

    destination = Path(target).expanduser() if target else _default_export_path(cli_session_id)
    if destination.suffix.lower() not in {".md", ".txt", ".json"}:
        destination = destination.with_suffix(".md")
    destination.parent.mkdir(parents=True, exist_ok=True)

    suffix = destination.suffix.lower()
    if suffix == ".txt":
        rendered = _format_txt(messages)
    elif suffix == ".json":
        rendered = _format_json(messages)
    else:
        rendered = _format_md(messages)
    destination.write_text(rendered, encoding="utf-8")
    return destination

print(f"Loaded prompt version: {ACTIVE_PROMPT_VERSION}")
print("Commands: /reset, /export [path], exit")

while True:
    user_input = input("> ")
    if user_input.lower() in ("exit", "quit"):
        break
    if user_input.strip().lower() == "/reset":
        asyncio.run(session.clear_session())
        history_store.clear_messages(session_id=cli_session_id)
        print("Memory cleared.")
        continue
    if user_input.strip().lower().startswith("/export"):
        raw_target = user_input.strip()[len("/export") :].strip()
        try:
            exported = export_transcript(raw_target or None)
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
        print(f"OpenAI API error ({exc.status_code}). Try again in a moment.")
        continue

    history_store.append_message(session_id=cli_session_id, role="user", content=user_input)
    history_store.append_message(session_id=cli_session_id, role="assistant", content=str(response.final_output))
    history_store.maybe_set_title_from_first_user_message(
        session_id=cli_session_id,
        user_message=user_input,
    )
    print(response.final_output)
