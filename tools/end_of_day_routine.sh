#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[end] starting end-of-day routine in: $ROOT_DIR"
echo "[end] 1/10 end-git-check"
make --no-print-directory end-git-check

echo "[end] 2/10 transcript-fix"
make --no-print-directory transcript-fix

echo "[end] 3/10 transcript-check"
make --no-print-directory transcript-check

echo "[end] 4/10 doctor-env"
make --no-print-directory doctor-env

echo "[end] 5/10 ci-python-style"
make --no-print-directory ci-python-style

echo "[end] 6/10 ci-python-type-check"
make --no-print-directory ci-python-type-check

echo "[end] 7/10 lint-docs"
make --no-print-directory lint-docs

echo "[end] 8/10 test"
make --no-print-directory test

echo "[end] 9/10 security-checks"
make --no-print-directory security-checks

echo "[end] 10/10 stop background tasks"
make --no-print-directory eod-stop

echo "[end] done"
