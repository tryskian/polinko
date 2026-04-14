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

has_session="false"
has_filename="false"
for arg in "$@"; do
  case "$arg" in
    --session|--session=*|-s|-s=*)
      has_session="true"
      ;;
    --filename|--filename=*)
      has_filename="true"
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
if [[ "$has_session" != "true" ]]; then
  args=(--session "$default_session" "${args[@]}")
fi

command_name=""
for ((i = 0; i < ${#args[@]}; i++)); do
  arg="${args[$i]}"
  case "$arg" in
    --session|-s)
      ((i += 1))
      ;;
    --session=*|-s=*)
      ;;
    --*)
      ;;
    *)
      command_name="$arg"
      break
      ;;
  esac
done

if [[ "$has_filename" != "true" ]]; then
  timestamp="$(date -u +%Y-%m-%dT%H-%M-%SZ)-$RANDOM"
  case "$command_name" in
    snapshot)
      args+=(--filename "$snapshot_dir/snapshot-$timestamp.md")
      ;;
    screenshot)
      args+=(--filename "$snapshot_dir/screenshot-$timestamp.png")
      ;;
    pdf)
      args+=(--filename "$snapshot_dir/page-$timestamp.pdf")
      ;;
  esac
fi

echo "Playwright snapshot directory: $snapshot_dir" >&2
exec "$pwcli" "${args[@]}"
