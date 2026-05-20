#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

MAKE_BIN="${MAKE:-make}"
exec "$MAKE_BIN" --no-print-directory server-daemon
