import argparse
import json
import os
import sys

import requests
from dotenv import load_dotenv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Polinko API chat client")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL")
    parser.add_argument("--session-id", default="local-dev", help="Conversation session ID")
    return parser


def main() -> int:
    load_dotenv(dotenv_path=".env")
    args = build_parser().parse_args()

    api_key = os.getenv("POLINKO_SERVER_API_KEY")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key

    print(f"Connected to {args.base_url} (session_id={args.session_id})")
    print("Type 'exit' or 'quit' to stop. Type '/reset' to clear server-side memory.")

    while True:
        try:
            user_input = input("> ").strip()
        except EOFError:
            print()
            return 0

        if user_input.lower() in {"exit", "quit"}:
            return 0

        if user_input.lower() == "/reset":
            resp = requests.post(
                f"{args.base_url}/session/reset",
                headers=headers,
                data=json.dumps({"session_id": args.session_id}),
                timeout=60,
            )
            print(f"[{resp.status_code}] {resp.text}")
            continue

        resp = requests.post(
            f"{args.base_url}/chat",
            headers=headers,
            data=json.dumps({"message": user_input, "session_id": args.session_id}),
            timeout=120,
        )
        if resp.ok:
            body = resp.json()
            print(body.get("output", ""))
        else:
            print(f"[{resp.status_code}] {resp.text}")


if __name__ == "__main__":
    sys.exit(main())
