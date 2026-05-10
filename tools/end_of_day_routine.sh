#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[eod] starting end-of-day routine in: $ROOT_DIR"
echo "[eod] 1/6 transcript-fix"
make --no-print-directory transcript-fix

echo "[eod] 2/6 transcript-check"
make --no-print-directory transcript-check

echo "[eod] 3/6 doctor-env"
make --no-print-directory doctor-env

echo "[eod] 4/6 lint-docs"
make --no-print-directory lint-docs

echo "[eod] 5/6 test"
make --no-print-directory test

echo "[eod] 6/6 stop background tasks"
make --no-print-directory end-stop

echo "[eod] done"
