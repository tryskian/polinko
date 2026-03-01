"""Local server for the portfolio workbench with server-side notebook storage."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


DEFAULT_NOTEBOOK_PAGE = {
    "id": "note-1",
    "title": "Scratchpad",
    "markdown": "# Portfolio notebook\n\n- Working notes\n- Fragments\n- Draft language\n",
}


@dataclass
class NotebookState:
    pages: list[dict[str, str]]
    active_page_id: str

    def to_json(self) -> dict[str, Any]:
        return {
            "pages": self.pages,
            "active_page_id": self.active_page_id,
        }


def _default_state() -> NotebookState:
    page = dict(DEFAULT_NOTEBOOK_PAGE)
    return NotebookState(pages=[page], active_page_id=page["id"])


def _normalize_page(raw: Any, idx: int) -> dict[str, str] | None:
    if not isinstance(raw, dict):
        return None
    page_id = str(raw.get("id", "")).strip()
    title = str(raw.get("title", "")).strip()
    markdown = raw.get("markdown", "")
    if not isinstance(markdown, str):
        markdown = str(markdown)
    if not page_id:
        page_id = f"note-{idx + 1}"
    if not title:
        title = f"Note {idx + 1}"
    return {
        "id": page_id[:128],
        "title": title[:200],
        "markdown": markdown,
    }


def _sanitize_state(raw: Any) -> NotebookState:
    if not isinstance(raw, dict):
        return _default_state()
    raw_pages = raw.get("pages", [])
    if not isinstance(raw_pages, list):
        raw_pages = []
    pages: list[dict[str, str]] = []
    for idx, item in enumerate(raw_pages):
        normalized = _normalize_page(item, idx)
        if normalized is not None:
            pages.append(normalized)
    if not pages:
        return _default_state()
    active_page_id = str(raw.get("active_page_id", "")).strip() or pages[0]["id"]
    if not any(page["id"] == active_page_id for page in pages):
        active_page_id = pages[0]["id"]
    return NotebookState(pages=pages, active_page_id=active_page_id)


def load_state(path: Path) -> NotebookState:
    if not path.exists():
        return _default_state()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _default_state()
    return _sanitize_state(raw)


def save_state(path: Path, state: NotebookState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = state.to_json()
    tmp_path = path.with_suffix(f"{path.suffix}.tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)


class WorkbenchHandler(SimpleHTTPRequestHandler):
    state_file: Path

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> Any:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            raise ValueError("Request body is required.")
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _is_api_state_route(self) -> bool:
        return urlparse(self.path).path == "/api/notebook/state"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/notebook/state":
            state = load_state(self.state_file)
            self._send_json(state.to_json())
            return
        if parsed.path in {"", "/"}:
            self.path = "/workbench.html"
        super().do_GET()

    def do_PUT(self) -> None:  # noqa: N802
        if not self._is_api_state_route():
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        try:
            payload = self._read_json_body()
            state = _sanitize_state(payload)
            save_state(self.state_file, state)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON."}, status=HTTPStatus.BAD_REQUEST)
            return
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(state.to_json())

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        # Keep stdout concise while still showing requests.
        super().log_message(format, *args)


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Serve portfolio workbench with notebook persistence.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8020, help="Port to bind (default: 8020)")
    parser.add_argument(
        "--directory",
        default=str(repo_root / "docs" / "portfolio"),
        help="Directory to serve static files from.",
    )
    parser.add_argument(
        "--state-file",
        default=str(repo_root / ".portfolio_workbench_state.json"),
        help="JSON file used for server-side notebook persistence.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    serve_dir = Path(args.directory).resolve()
    state_file = Path(args.state_file).resolve()

    if not serve_dir.exists():
        raise SystemExit(f"Serve directory does not exist: {serve_dir}")

    class _ConfiguredHandler(WorkbenchHandler):
        pass

    _ConfiguredHandler.state_file = state_file
    os.chdir(serve_dir)
    server = ThreadingHTTPServer((args.host, args.port), _ConfiguredHandler)
    print(f"Portfolio workbench: http://{args.host}:{args.port}/workbench.html")
    print(f"Notebook state file: {state_file}")
    server.serve_forever()


if __name__ == "__main__":
    main()
