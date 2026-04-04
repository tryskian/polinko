#!/bin/zsh
set -u
REPO_ROOT="/Users/tryskian/Github/polinko"
PYTHON_BIN="$REPO_ROOT/venv/bin/python"
RUN_LOG="$1"
EXPORT_ROOT="/Users/tryskian/Library/CloudStorage/Dropbox/CGPT-DATA-EXPORT"
cd "$REPO_ROOT" || exit 1
END_TS=$($PYTHON_BIN - <<'PY'
from datetime import datetime
now=datetime.now()
noon=now.replace(hour=12, minute=0, second=0, microsecond=0)
print(int(noon.timestamp()))
PY
)
PASS=1
echo "[start] $(date -u +%Y-%m-%dT%H:%M:%SZ) end_ts=$END_TS export_root=$EXPORT_ROOT" >> "$RUN_LOG"
if [ "$(date +%s)" -ge "$END_TS" ]; then
  echo "[info] now past noon; running one kernel pass only" >> "$RUN_LOG"
  make ocrkernel CGPT_EXPORT_ROOT="$EXPORT_ROOT" >> "$RUN_LOG" 2>&1 || true
  echo "[done-single] $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RUN_LOG"
  exit 0
fi
while [ "$(date +%s)" -lt "$END_TS" ]; do
  echo "[pass:$PASS:start] $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RUN_LOG"
  make ocrkernel CGPT_EXPORT_ROOT="$EXPORT_ROOT" >> "$RUN_LOG" 2>&1 || true
  echo "[pass:$PASS:end] $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RUN_LOG"
  PASS=$((PASS+1))
  sleep 90
done
echo "[done] $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RUN_LOG"
