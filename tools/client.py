import argparse
import base64
import json
import mimetypes
import os
import shlex
import sys
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


def _post_json(
    *,
    base_url: str,
    path: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    timeout: int,
) -> requests.Response:
    return requests.post(
        f"{base_url}{path}",
        headers=headers,
        data=json.dumps(payload),
        timeout=timeout,
    )


def _safe_json(response: requests.Response) -> dict[str, Any]:
    try:
        value = response.json()
    except ValueError:
        return {}
    return value if isinstance(value, dict) else {}


def _print_help() -> None:
    print("Commands:")
    print("  /help                     show command help")
    print("  /reset                    clear server-side memory for active session")
    print("  /ocr <file>               run OCR ingest for a local file (verbatim mode)")
    print("  /ocr --mode normalized <file>   run OCR with normalized whitespace mode")
    print("  /pdf <file>               run PDF ingest for a local PDF file")
    print("  /search <query>           search indexed content (chat/ocr/pdf)")
    print("  /search-ocr <query>       search only OCR-indexed content")
    print("  /search-pdf <query>       search only PDF-indexed content")
    print("  /search-chat <query>      search only chat-indexed content")
    print("  /export                   print chat export summary")
    print("  /exit                     stop client")
    print("  exit|quit                 stop client")


def _read_file_base64(file_path: str) -> tuple[str, str, str]:
    path = Path(file_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    mime_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return payload, mime_type, path.name


def _parse_ocr_command(tokens: list[str]) -> tuple[str, str] | None:
    if not tokens:
        return None

    mode = "verbatim"
    file_path: str | None = None
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "--mode":
            index += 1
            if index >= len(tokens):
                return None
            candidate = tokens[index].strip().lower()
            if candidate not in {"verbatim", "normalized"}:
                return None
            mode = candidate
        elif token.startswith("--mode="):
            candidate = token.split("=", 1)[1].strip().lower()
            if candidate not in {"verbatim", "normalized"}:
                return None
            mode = candidate
        elif token.startswith("-"):
            return None
        elif file_path is None:
            file_path = token
        else:
            return None
        index += 1

    if not file_path:
        return None
    return file_path, mode


def _run_search(
    *,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    query: str,
    source_types: list[str] | None,
) -> None:
    resp = _post_json(
        base_url=base_url,
        path="/skills/file_search",
        headers=headers,
        payload={
            "query": query,
            "session_id": session_id,
            "source_types": source_types,
            "limit": 5,
        },
        timeout=120,
    )
    if not resp.ok:
        print(f"[{resp.status_code}] {resp.text}")
        return
    payload = _safe_json(resp)
    matches = payload.get("matches", [])
    if not isinstance(matches, list) or not matches:
        print("No matches.")
        return
    print(f"Matches: {len(matches)}")
    for idx, match in enumerate(matches[:5], start=1):
        if not isinstance(match, dict):
            continue
        source = str(match.get("source_type", "unknown"))
        score = float(match.get("score", 0.0))
        snippet = str(match.get("snippet", ""))
        print(f"{idx}. [{source}] score={score:.3f}")
        print(f"   {snippet}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Nautorus API chat client")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Nautorus API base URL")
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
    print("Type '/help' for commands.")

    while True:
        try:
            user_input = input("> ").strip()
        except EOFError:
            print()
            return 0

        lowered = user_input.lower()
        if lowered in {"exit", "quit", "/exit"}:
            return 0

        if user_input.startswith("/"):
            try:
                tokens = shlex.split(user_input)
            except ValueError as exc:
                print(f"Invalid command syntax: {exc}")
                continue
            if not tokens:
                continue

            command = tokens[0].lower()

            if command == "/help":
                _print_help()
                continue

            if command == "/reset":
                resp = _post_json(
                    base_url=args.base_url,
                    path="/session/reset",
                    headers=headers,
                    payload={"session_id": args.session_id},
                    timeout=60,
                )
                print(f"[{resp.status_code}] {resp.text}")
                continue

            if command in {"/search", "/search-ocr", "/search-pdf", "/search-chat"}:
                if len(tokens) < 2:
                    print(f"Usage: {command} <query>")
                    continue
                query = " ".join(tokens[1:]).strip()
                source_types_map: dict[str, list[str] | None] = {
                    "/search": None,
                    "/search-ocr": ["ocr"],
                    "/search-pdf": ["pdf"],
                    "/search-chat": ["chat"],
                }
                _run_search(
                    base_url=args.base_url,
                    headers=headers,
                    session_id=args.session_id,
                    query=query,
                    source_types=source_types_map[command],
                )
                continue

            if command in {"/ocr", "/pdf"}:
                ocr_mode = "verbatim"
                file_arg = ""
                if command == "/ocr":
                    parsed = _parse_ocr_command(tokens[1:])
                    if parsed is None:
                        print("Usage: /ocr [--mode verbatim|normalized] <file-path>")
                        continue
                    file_arg, ocr_mode = parsed
                else:
                    if len(tokens) < 2:
                        print("Usage: /pdf <file-path>")
                        continue
                    file_arg = tokens[1]
                try:
                    payload_b64, mime_type, source_name = _read_file_base64(file_arg)
                except (OSError, FileNotFoundError) as exc:
                    print(str(exc))
                    continue

                endpoint = "/skills/ocr" if command == "/ocr" else "/skills/pdf_ingest"
                if command == "/pdf":
                    mime_type = "application/pdf"
                payload: dict[str, Any] = {
                    "session_id": args.session_id,
                    "source_name": source_name,
                    "mime_type": mime_type,
                    "data_base64": payload_b64,
                    "attach_to_chat": True,
                }
                if command == "/ocr":
                    payload["transcription_mode"] = ocr_mode
                resp = _post_json(
                    base_url=args.base_url,
                    path=endpoint,
                    headers=headers,
                    payload=payload,
                    timeout=180,
                )
                if not resp.ok:
                    print(f"[{resp.status_code}] {resp.text}")
                    continue
                payload = _safe_json(resp)
                if command == "/ocr":
                    run = payload.get("run", {})
                    if isinstance(run, dict):
                        print(
                            f"OCR indexed: run_id={run.get('run_id')} "
                            f"status={run.get('status')} chars={len(str(run.get('extracted_text', '')))}"
                        )
                    else:
                        print(json.dumps(payload, ensure_ascii=False))
                else:
                    print(
                        f"PDF indexed: ingest_id={payload.get('ingest_id')} "
                        f"chunks={payload.get('vector_chunks')} chars={payload.get('extracted_chars')}"
                    )
                continue

            if command == "/export":
                resp = requests.get(
                    f"{args.base_url}/chats/{args.session_id}/export",
                    headers=headers,
                    timeout=120,
                )
                if not resp.ok:
                    print(f"[{resp.status_code}] {resp.text}")
                    continue
                payload = _safe_json(resp)
                print(
                    "Export: "
                    f"title={payload.get('title')} "
                    f"messages={payload.get('message_count')} "
                    f"ocr_runs={len(payload.get('ocr_runs', [])) if isinstance(payload.get('ocr_runs'), list) else 0}"
                )
                continue

            print(f"Unknown command: {command}. Type /help.")
            continue

        resp = _post_json(
            base_url=args.base_url,
            path="/chat",
            headers=headers,
            payload={"message": user_input, "session_id": args.session_id},
            timeout=120,
        )
        if resp.ok:
            body = _safe_json(resp)
            print(body.get("output", ""))
        else:
            print(f"[{resp.status_code}] {resp.text}")


if __name__ == "__main__":
    sys.exit(main())
