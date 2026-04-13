#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[eod] starting end-of-day routine in: $ROOT_DIR"
echo "[eod] 1/7 transcript-fix"
make --no-print-directory transcript-fix

echo "[eod] 2/7 transcript-check"
make --no-print-directory transcript-check

echo "[eod] 3/7 eod-docs-check"
make --no-print-directory eod-docs-check

echo "[eod] 4/7 doctor-env"
make --no-print-directory doctor-env

echo "[eod] 5/7 lint-docs"
make --no-print-directory lint-docs

echo "[eod] 6/7 test"
make --no-print-directory test

echo "[eod] 7/7 stop background tasks"
make --no-print-directory eod-stop

echo "[eod] done"
