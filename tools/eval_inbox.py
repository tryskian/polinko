import argparse
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

_DEFAULT_CURSOR = Path(".eval_inbox.cursor")


def _default_log_path() -> Path:
    root = Path(
        os.getenv("POLINKO_FEEDBACK_EVIDENCE_ROOT", "docs/portfolio/raw_evidence")
    )
    return root / "INBOX" / "eval_submissions.jsonl"


def _load_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = line.strip()
            if not payload:
                continue
            try:
                item = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                rows.append(item)
    rows.sort(key=lambda item: int(item.get("timestamp_ms", 0)))
    return rows


def _read_cursor(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return int(path.read_text(encoding="utf-8").strip() or "0")
    except (OSError, ValueError):
        return 0


def _write_cursor(path: Path, value: int) -> None:
    path.write_text(str(value), encoding="utf-8")


def _format_time(timestamp_ms: int) -> str:
    if timestamp_ms <= 0:
        return "unknown"
    stamp = dt.datetime.fromtimestamp(
        timestamp_ms / 1000, tz=dt.timezone.utc
    ).astimezone()
    return stamp.strftime("%Y-%m-%d %H:%M:%S")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show recent eval submissions from the local inbox log."
    )
    parser.add_argument(
        "--log-path",
        default=str(_default_log_path()),
        help="Path to eval submissions jsonl log.",
    )
    parser.add_argument("--limit", type=int, default=20, help="Max records to print.")
    parser.add_argument(
        "--status",
        choices=["all", "open", "closed"],
        default="all",
        help="Filter by eval status.",
    )
    parser.add_argument(
        "--new", action="store_true", help="Show only entries newer than local cursor."
    )
    parser.add_argument(
        "--cursor-file",
        default=str(_DEFAULT_CURSOR),
        help="Cursor file used with --new.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Print matching records as JSON."
    )
    return parser


def main() -> int:
    load_dotenv(dotenv_path=".env")
    args = build_parser().parse_args()

    log_path = Path(args.log_path).expanduser()
    cursor_path = Path(args.cursor_file).expanduser()
    records = _load_records(log_path)

    if not records:
        print(f"No eval submissions found at {log_path}.")
        return 0

    min_ts = 0
    if args.new:
        min_ts = _read_cursor(cursor_path)

    filtered: list[dict[str, Any]] = []
    for item in records:
        ts = int(item.get("timestamp_ms", 0))
        status = str(item.get("status", "")).strip().lower()
        if ts <= min_ts:
            continue
        if args.status != "all" and status != args.status:
            continue
        filtered.append(item)

    if args.limit > 0:
        filtered = filtered[-args.limit :]

    if args.json:
        print(json.dumps(filtered, ensure_ascii=False, indent=2))
    else:
        if not filtered:
            print("No matching eval submissions.")
        for item in filtered:
            ts = int(item.get("timestamp_ms", 0))
            when = _format_time(ts)
            outcome = str(item.get("outcome", "")).upper() or "UNKNOWN"
            status = str(item.get("status", "")).upper() or "UNKNOWN"
            title = str(item.get("chat_title", "")).strip() or "(untitled)"
            session_id = str(item.get("session_id", "")).strip()
            positive = ", ".join(item.get("positive_tags", []) or []) or "none"
            negative = ", ".join(item.get("negative_tags", []) or []) or "none"
            print(f"[{when}] {status}/{outcome} {title}")
            print(f"  session={session_id}")
            print(f"  +tags={positive}")
            print(f"  -tags={negative}")
            note = str(item.get("note", "")).strip()
            if note:
                print(f"  note={note}")
            rec = str(item.get("recommended_action", "")).strip()
            if rec:
                print(f"  action={rec}")

    if args.new and records:
        newest = max(int(item.get("timestamp_ms", 0)) for item in records)
        _write_cursor(cursor_path, newest)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
