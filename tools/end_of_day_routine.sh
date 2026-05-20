#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[end] starting end-of-day routine in: $ROOT_DIR"
echo "[end] 1/9 transcript-fix"
make --no-print-directory transcript-fix

echo "[end] 2/9 transcript-check"
make --no-print-directory transcript-check

echo "[end] 3/9 doctor-env"
make --no-print-directory doctor-env

echo "[end] 4/9 ci-python-style"
make --no-print-directory ci-python-style

echo "[end] 5/9 ci-python-type-check"
make --no-print-directory ci-python-type-check

echo "[end] 6/9 lint-docs"
make --no-print-directory lint-docs

echo "[end] 7/9 test"
make --no-print-directory test

echo "[end] 8/9 security-checks"
make --no-print-directory security-checks

echo "[end] 9/9 stop background tasks"
make --no-print-directory eod-stop

echo "[end] done"
