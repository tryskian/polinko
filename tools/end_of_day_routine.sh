#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[end] starting end-of-day routine in: $ROOT_DIR"
echo "[end] 1/7 transcript-fix"
make --no-print-directory transcript-fix

echo "[end] 2/7 transcript-check"
make --no-print-directory transcript-check

echo "[end] 3/7 doctor-env"
make --no-print-directory doctor-env

echo "[end] 4/7 lint-docs"
make --no-print-directory lint-docs

echo "[end] 5/7 test"
make --no-print-directory test

echo "[end] 6/7 security-checks"
make --no-print-directory security-checks

echo "[end] 7/7 stop background tasks"
make --no-print-directory eod-stop

echo "[end] done"
