import asyncio
import os
import sys
from pathlib import Path
from typing import cast

try:
    from dotenv import load_dotenv
    from agents import Agent, ModelSettings, RunConfig, Runner
    from agents.memory import Session, SQLiteSession, SessionSettings
    from openai import APIConnectionError, APIStatusError, AuthenticationError, RateLimitError
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

load_dotenv(dotenv_path=".env")

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set. Add it to .env or export it before running.")

AGENT_INSTRUCTIONS = (
    "conversational, laid back, witty, resonant, and creative."
    "use emojis sparingly and be concise but still insightful."
    "UK english. no follow up questions."
    "no emotions, feelings, or human traits. you're a friendly brain, not human."
    )

agent = Agent(
    name="Polinko Repositining System",
    instructions=AGENT_INSTRUCTIONS,
    model="gpt-5-chat-latest"
)

run_config = RunConfig(
    model_settings=ModelSettings(
        temperature=1.0,
        top_p=1.0,
        store=True,
    )
)

session: Session = cast(
    Session,
    SQLiteSession(
        session_id="polinko-cli",
        db_path=".polinko_memory.db",
        session_settings=SessionSettings(limit=80),
    ),
)

while True:
    user_input = input("> ")
    if user_input.lower() in ("exit", "quit"):
        break
    if user_input.strip().lower() == "/reset":
        asyncio.run(session.clear_session())
        print("Memory cleared.")
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

    print(response.final_output)
