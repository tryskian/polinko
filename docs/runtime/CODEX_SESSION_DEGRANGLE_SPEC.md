<!-- @format -->

# Codex Session Degrangle Spec

Use this spec when a Codex thread is too large, stuck in compact/resume loops,
or returning malformed transcript payload errors from local session state.

This is a local repair procedure for `~/.codex` session files. It is not a repo
runtime migration and must not be run blindly.

## Trigger Symptoms

Run this procedure when one of these appears:

- remote compact fails with `array too long`
- remote compact fails with stream disconnects before completion
- Codex app resumes a completed/interrupted turn as still streaming
- request fails with malformed transcript content, for example invalid
  `image_url`
- a thread JSONL is hundreds of MB or larger
- SQLite `tokens_used` is clearly stale or extreme for a repaired thread

## Safety Rules

1. Do not edit an active thread.
   - If `lsof` shows a `codex` writer on the target JSONL, stop.
   - Ask the human to close that thread/window first.
2. Always back up before any write.
   - Back up the live transcript.
   - Back up the archived duplicate if present.
   - Back up `~/.codex/state_5.sqlite`.
   - Back up `~/.codex/session_index.jsonl` if present.
3. Preserve readable conversation records.
   - Keep `response_item` records whose payload type is `message`.
   - Remove tool/reasoning/compact baggage only.
4. Do not raw-print broad `~/.codex` state files.
   - Some local state files may contain environment values or tokens.
   - Use targeted parsers and summaries instead.
5. Validate after every write.
   - JSONL must parse.
   - `image_url` values must be valid `http`, `https`, or `data` URLs.
   - SQLite integrity must return `ok`.
   - `tokens_used` should be reset for repaired compact-loop threads.

## Local Paths

Common Codex local state paths:

- live sessions: `~/.codex/sessions/**/*.jsonl`
- archived sessions: `~/.codex/archived_sessions/*.jsonl`
- SQLite state: `~/.codex/state_5.sqlite`
- session index: `~/.codex/session_index.jsonl`
- backups: `~/.codex/backups/<timestamp>-<thread-name>-<operation>/`

The SQLite table for thread metadata is `threads`.

Important columns:

- `id`
- `title`
- `rollout_path`
- `archived`
- `tokens_used`
- `updated_at_ms`

## Read-Only Diagnosis

Set the target thread ID first:

```bash
THREAD_ID="019..."
```

Find candidate transcript paths:

```bash
find "$HOME/.codex/sessions" "$HOME/.codex/archived_sessions" \
  -name "*${THREAD_ID}*.jsonl" -print
```

Check whether the files are open:

```bash
lsof "$HOME/.codex/sessions/path/to/rollout-${THREAD_ID}.jsonl" \
  "$HOME/.codex/archived_sessions/rollout-${THREAD_ID}.jsonl" 2>/dev/null |
  awk 'NR==1 || /codex/ {print $1, $2, $4, $9}'
```

If a line contains `codex` with a write file descriptor such as `37w`, stop.

Summarize transcript size and record types:

```bash
python3 - <<'PY'
import json
from pathlib import Path

paths = [
    Path("/absolute/path/to/live.jsonl"),
    Path("/absolute/path/to/archive.jsonl"),
]

for path in paths:
    if not path.exists():
        continue
    counts = {}
    payloads = {}
    parse_errors = 0
    max_line = 0
    with path.open("rb") as handle:
        for line in handle:
            max_line = max(max_line, len(line))
            try:
                item = json.loads(line)
            except Exception:
                parse_errors += 1
                continue
            kind = item.get("type")
            counts[kind] = counts.get(kind, 0) + 1
            if kind == "response_item":
                payload_type = (item.get("payload") or {}).get("type")
                payloads[payload_type] = payloads.get(payload_type, 0) + 1
    print("==", path)
    print("size_bytes", path.stat().st_size)
    print("counts", counts)
    print("response_payloads", payloads)
    print("max_line_bytes", max_line)
    print("parse_errors", parse_errors)
PY
```

Check SQLite state:

```bash
python3 - <<'PY'
import sqlite3
from pathlib import Path

thread_id = "019..."
db = Path.home() / ".codex/state_5.sqlite"
con = sqlite3.connect(db)
print("integrity", con.execute("pragma integrity_check").fetchone()[0])
print(
    con.execute(
        "select id,title,archived,tokens_used,updated_at_ms,rollout_path "
        "from threads where id=?",
        (thread_id,),
    ).fetchall()
)
con.close()
PY
```

## Backup Procedure

Create a timestamped backup directory:

```bash
BACKUP="$HOME/.codex/backups/$(date +%Y%m%d-%H%M%S)-session-degrangle"
mkdir -p "$BACKUP"
cp -p /absolute/path/to/live.jsonl "$BACKUP/"
cp -p /absolute/path/to/archive.jsonl "$BACKUP/" 2>/dev/null || true
cp -p "$HOME/.codex/state_5.sqlite" "$BACKUP/"
cp -p "$HOME/.codex/session_index.jsonl" "$BACKUP/" 2>/dev/null || true
```

Do not continue if the backup fails.

## Cleanup Mode A: Compact/Tool Baggage Removal

Use this when `response_item` count is high or compact fails with an input item
limit.

This keeps readable `message` response items and removes non-message response
items, including reasoning, function calls, tool calls, tool outputs, and web
search calls. It also removes `compacted` records.

```bash
python3 - <<'PY'
import json
import os
from pathlib import Path

paths = [
    Path("/absolute/path/to/live.jsonl"),
    Path("/absolute/path/to/archive.jsonl"),
]

MAX_STRING = 200_000
KEEP_PREFIX = 16_000
KEEP_SUFFIX = 4_000


def trim_large_strings(value, stats, field_path="$"):
    if isinstance(value, str):
        if len(value) > MAX_STRING:
            stats["strings_trimmed"] += 1
            return (
                "[trimmed oversized local Codex transcript field: "
                f"{len(value)} chars at {field_path}; preserved prefix/suffix]\n"
                + value[:KEEP_PREFIX]
                + "\n...[trimmed for local Codex stability]...\n"
                + value[-KEEP_SUFFIX:]
            )
        return value
    if isinstance(value, list):
        return [
            trim_large_strings(item, stats, f"{field_path}[{index}]")
            for index, item in enumerate(value)
        ]
    if isinstance(value, dict):
        return {
            key: trim_large_strings(
                item,
                stats,
                f"{field_path}.{key}" if field_path else str(key),
            )
            for key, item in value.items()
        }
    return value


def clean_file(path):
    if not path.exists():
        return None

    tmp = path.with_suffix(path.suffix + ".tmp")
    stats = {
        "input_lines": 0,
        "output_lines": 0,
        "parse_errors": 0,
        "compacted_removed": 0,
        "response_items_removed": 0,
        "kept_response_messages": 0,
        "strings_trimmed": 0,
    }

    with path.open("rb") as src, tmp.open("wb") as dst:
        for raw in src:
            stats["input_lines"] += 1
            try:
                item = json.loads(raw)
            except Exception:
                stats["parse_errors"] += 1
                dst.write(raw)
                stats["output_lines"] += 1
                continue

            kind = item.get("type")
            if kind == "compacted":
                stats["compacted_removed"] += 1
                continue

            if kind == "response_item":
                payload_type = (item.get("payload") or {}).get("type")
                if payload_type != "message":
                    stats["response_items_removed"] += 1
                    continue
                stats["kept_response_messages"] += 1

            item = trim_large_strings(item, stats)
            dst.write(
                (json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
                .encode("utf-8")
            )
            stats["output_lines"] += 1

    os.replace(tmp, path)
    stats["output_bytes"] = path.stat().st_size
    return stats


for path in paths:
    result = clean_file(path)
    if result is not None:
        print("==", path)
        print(json.dumps(result, indent=2, sort_keys=True))
PY
```

## Cleanup Mode B: Invalid Image URL Repair

Use this when the API reports an invalid `image_url`, especially after a prior
oversized string trim.

Problem signature:

```text
Invalid 'input[N].content[M].image_url'. Expected a valid URL
```

Valid repair is to replace only malformed image URLs with a tiny valid
transparent PNG data URL. Do not remove the whole message unless the message is
otherwise corrupt.

```bash
python3 - <<'PY'
import json
import os
from pathlib import Path

paths = [
    Path("/absolute/path/to/live.jsonl"),
    Path("/absolute/path/to/archive.jsonl"),
]

PLACEHOLDER = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0l"
    "EQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)
MARKER = "[trimmed oversized local Codex transcript field:"


def repair(value, stats):
    if isinstance(value, dict):
        repaired = {}
        for key, item in value.items():
            if key == "image_url" and isinstance(item, str) and item.startswith(MARKER):
                stats["repaired"] += 1
                repaired[key] = PLACEHOLDER
            else:
                repaired[key] = repair(item, stats)
        if repaired.get("type") == "input_image" and repaired.get("image_url") == PLACEHOLDER:
            repaired["detail"] = "low"
        return repaired
    if isinstance(value, list):
        return [repair(item, stats) for item in value]
    return value


for path in paths:
    if not path.exists():
        continue
    tmp = path.with_suffix(path.suffix + ".tmp")
    stats = {"lines": 0, "parse_errors": 0, "repaired": 0}
    with path.open("rb") as src, tmp.open("wb") as dst:
        for raw in src:
            stats["lines"] += 1
            try:
                item = json.loads(raw)
            except Exception:
                stats["parse_errors"] += 1
                dst.write(raw)
                continue
            item = repair(item, stats)
            dst.write(
                (json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
                .encode("utf-8")
            )
    os.replace(tmp, path)
    print("==", path)
    print(json.dumps(stats, sort_keys=True))
PY
```

## Cleanup Mode C: Token Counter Reset

Use this after repairing a compact-loop thread. The app may otherwise retry
compaction because `tokens_used` remains stale.

```bash
python3 - <<'PY'
import shutil
import sqlite3
import time
from pathlib import Path

thread_id = "019..."
home = Path.home()
db = home / ".codex/state_5.sqlite"
backup = home / ".codex/backups" / (
    time.strftime("%Y%m%d-%H%M%S") + "-token-reset"
)
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(db, backup / db.name)

con = sqlite3.connect(db, timeout=30)
con.execute("pragma busy_timeout=30000")
before = con.execute(
    "select tokens_used from threads where id=?",
    (thread_id,),
).fetchone()
con.execute("update threads set tokens_used=0 where id=?", (thread_id,))
con.commit()
after = con.execute(
    "select tokens_used from threads where id=?",
    (thread_id,),
).fetchone()
print("backup", backup)
print("tokens_used", before, "->", after)
print("integrity", con.execute("pragma integrity_check").fetchone()[0])
con.close()
PY
```

## Validation

Run this after every cleanup pass:

```bash
python3 - <<'PY'
import json
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

paths = [
    Path("/absolute/path/to/live.jsonl"),
    Path("/absolute/path/to/archive.jsonl"),
]
thread_id = "019..."


def valid_image_url(value):
    if not isinstance(value, str) or not value:
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "data"}


def walk(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "image_url":
                yield item
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


for path in paths:
    if not path.exists():
        continue
    counts = {}
    payloads = {}
    parse_errors = 0
    invalid_images = 0
    image_count = 0
    with path.open("rb") as handle:
        for line in handle:
            try:
                item = json.loads(line)
            except Exception:
                parse_errors += 1
                continue
            kind = item.get("type")
            counts[kind] = counts.get(kind, 0) + 1
            if kind == "response_item":
                payload_type = (item.get("payload") or {}).get("type")
                payloads[payload_type] = payloads.get(payload_type, 0) + 1
            for image_url in walk(item):
                image_count += 1
                if not valid_image_url(image_url):
                    invalid_images += 1
    print("==", path)
    print("size_bytes", path.stat().st_size)
    print("parse_errors", parse_errors)
    print("counts", counts)
    print("response_payloads", payloads)
    print("image_urls", image_count)
    print("invalid_image_urls", invalid_images)

con = sqlite3.connect(Path.home() / ".codex/state_5.sqlite")
print("sqlite_integrity", con.execute("pragma integrity_check").fetchone()[0])
print(
    "thread_db",
    con.execute(
        "select tokens_used, archived, updated_at_ms from threads where id=?",
        (thread_id,),
    ).fetchone(),
)
con.close()
PY
```

Expected healthy post-repair state:

- `parse_errors` is `0`
- `invalid_image_urls` is `0`
- `response_payloads` contains only `message` for repaired bloated threads
- `compacted` count is absent or `0`
- SQLite integrity is `ok`
- repaired thread `tokens_used` is `0`
- `lsof` shows no unexpected `codex` writer on the repaired transcript

## Retirement Pattern For The Active Beab

The active Codex thread must not rewrite itself. For a clean handoff:

1. Active beab writes the state/handoff/spec docs.
2. Human closes the active thread.
3. A fresh beab identifies the retired thread ID and transcript path.
4. Fresh beab runs this spec against the closed thread.
5. Fresh beab validates JSONL, image URLs, SQLite, and `tokens_used`.

Peanut version: the beab can pack its own repair kit, but another beab should
do the surgery after the first beab is no longer holding the pen.

## Known POL-3/POL-4 Lessons

- POL-4 compact-loop cause:
  - huge transcript payloads and too many response items.
  - repair was to remove compact/tool baggage and reset `tokens_used`.
- POL-3 compact-loop cause:
  - very large transcript plus stale token count.
  - repair was to keep message records only, remove compact/tool baggage, and
    reset `tokens_used`.
- POL-3 follow-up image error:
  - oversized `data:image/png;base64,...` URLs were trimmed with a text prefix.
  - that made the field invalid because `image_url` must start with a valid URL
    scheme.
  - repair was to replace those malformed fields with tiny valid data URLs.

Do not generalize beyond the observed failure mode. Diagnose first, then apply
only the matching cleanup mode.
