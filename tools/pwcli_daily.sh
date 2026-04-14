#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

base_dir="${PLAYWRIGHT_SNAPSHOT_BASE_DIR:-docs/peanut/assets/screenshots/playwright}"
day="${PLAYWRIGHT_SNAPSHOT_DAY:-$(date +%d-%m-%y)}"
snapshot_dir="${base_dir%/}/${day}"
default_session="${PLAYWRIGHT_SESSION:-polinko}"

mkdir -p "$snapshot_dir"

if [[ "${1:-}" == "--print-dir" ]]; then
  printf '%s\n' "$snapshot_dir"
  exit 0
fi

if [[ "$#" -eq 0 ]]; then
  cat >&2 <<EOF
Usage: tools/pwcli_daily.sh <playwright-cli args>

Snapshot directory: $snapshot_dir
Example: tools/pwcli_daily.sh --session portfolio open http://127.0.0.1:8000/portfolio
EOF
  exit 2
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "Error: npx is required but was not found on PATH." >&2
  exit 1
fi

config_dir=".local/logs/playwright"
config_file="$config_dir/cli.config.json"
mkdir -p "$config_dir"

"${PYTHON:-python3}" - "$config_file" "$snapshot_dir" <<'PY'
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
snapshot_dir = sys.argv[2]
config_path.write_text(
    json.dumps(
        {
            "outputDir": snapshot_dir,
            "outputMode": "file",
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
PY

has_config="false"
has_session="false"
for arg in "$@"; do
  case "$arg" in
    --config|--config=*)
      has_config="true"
      ;;
    --session|--session=*)
      has_session="true"
      ;;
  esac
done

codex_home="${CODEX_HOME:-$HOME/.codex}"
pwcli="${PWCLI:-$codex_home/skills/playwright/scripts/playwright_cli.sh}"
if [[ ! -x "$pwcli" ]]; then
  echo "Error: Playwright CLI wrapper not found or not executable: $pwcli" >&2
  exit 1
fi

args=("$@")
if [[ "$has_config" != "true" ]]; then
  args+=(--config "$config_file")
fi
if [[ "$has_session" != "true" ]]; then
  args=(--session "$default_session" "${args[@]}")
fi

echo "Playwright snapshot directory: $snapshot_dir" >&2
exec "$pwcli" "${args[@]}"
