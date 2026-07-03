#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"
# shellcheck source=tools/process_lifecycle_common.sh
. "$script_dir/process_lifecycle_common.sh"

polinko_cd_repo_root

base_dir="${PLAYWRIGHT_SNAPSHOT_BASE_DIR:-docs/peanut/assets/screenshots/playwright}"
day="${PLAYWRIGHT_SNAPSHOT_DAY:-$(date +%d-%m-%y)}"
snapshot_stamp="${PLAYWRIGHT_SNAPSHOT_STAMP:-}"
snapshot_dir="${base_dir%/}/${day}"
default_session="${PLAYWRIGHT_SESSION:-polinko}"

prepare_snapshot_dir() {
  if ! mkdir -p "$snapshot_dir" 2>/dev/null; then
    echo "pwcli-daily failed to prepare snapshot directory: $snapshot_dir" >&2
    return 1
  fi
}

if ! prepare_snapshot_dir; then
  exit 1
fi

if [[ "${1:-}" == "--print-dir" ]]; then
  printf '%s\n' "$snapshot_dir"
  exit 0
fi

if [[ "$#" -eq 0 ]]; then
  cat >&2 <<EOF
Usage: tools/pwcli_daily.sh <playwright-cli args>

Snapshot directory: $snapshot_dir
Example: tools/pwcli_daily.sh --session pass-fail open http://127.0.0.1:8000/viz/pass-fail
EOF
  exit 2
fi

polinko_require_labeled_command "npx" "npx" "pwcli-daily"

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
for arg in "${args[@]}"; do
  case "$arg" in
    snapshot|screenshot|pdf)
      command_name="$arg"
      break
      ;;
  esac
done

if [[ "$has_filename" != "true" ]]; then
  if [[ -n "$snapshot_stamp" ]]; then
    timestamp="$snapshot_stamp"
  else
    timestamp="$(date -u +%Y-%m-%dT%H-%M-%SZ)-$$"
  fi
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
