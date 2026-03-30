#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[eod] starting end-of-day routine in: $ROOT_DIR"
echo "[eod] 1/5 transcript-fix"
make --no-print-directory transcript-fix

echo "[eod] 2/5 transcript-check"
make --no-print-directory transcript-check

echo "[eod] 3/5 build-audit"
make --no-print-directory build-audit

echo "[eod] 4/5 lint-docs"
make --no-print-directory lint-docs

echo "[eod] 5/5 test"
make --no-print-directory test

echo "[eod] done"
