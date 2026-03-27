#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
DEV_HOST="${DEV_HOST:-127.0.0.1}"
DEV_BACKEND_PORT="${DEV_BACKEND_PORT:-8000}"
DEV_AUTOKILL="${DEV_AUTOKILL:-1}"
DEV_STOP_ONLY="${DEV_STOP_ONLY:-0}"

kill_port_listeners() {
  local port="$1"
  local pids
  pids="$(lsof -nP -iTCP:"${port}" -sTCP:LISTEN -t 2>/dev/null | sort -u || true)"
  if [[ -z "${pids}" ]]; then
    return 0
  fi

  echo "Port ${port} is in use. Resolving listeners..."
  for pid in ${pids}; do
    local cmd
    cmd="$(ps -o command= -p "${pid}" 2>/dev/null || true)"
    if [[ -z "${cmd}" ]]; then
      continue
    fi

    if [[ "${cmd}" == *"uvicorn"* || "${cmd}" == *"server:app"* ]]; then
      echo "  stopping dev-like process ${pid}: ${cmd}"
      kill "${pid}" >/dev/null 2>&1 || true
      continue
    fi

    if [[ "${DEV_AUTOKILL}" == "1" ]]; then
      echo "  stopping process ${pid} on required port ${port}: ${cmd}"
      kill "${pid}" >/dev/null 2>&1 || true
    else
      echo "Port ${port} is used by a non-dev process and DEV_AUTOKILL=0."
      echo "Process ${pid}: ${cmd}"
      echo "Stop it manually or re-run with DEV_AUTOKILL=1."
      exit 1
    fi
  done

  sleep 0.3
  local still
  still="$(lsof -nP -iTCP:"${port}" -sTCP:LISTEN -t 2>/dev/null | sort -u || true)"
  if [[ -n "${still}" ]]; then
    echo "  force-stopping remaining listener(s) on ${port}: ${still}"
    kill -9 ${still} >/dev/null 2>&1 || true
  fi
}

if ! command -v lsof >/dev/null 2>&1; then
  echo "lsof is required for make dev port preflight."
  exit 1
fi

kill_port_listeners "${DEV_BACKEND_PORT}"

if [[ "${DEV_STOP_ONLY}" == "1" ]]; then
  echo "Stopped listeners on ${DEV_BACKEND_PORT}."
  exit 0
fi

echo "Starting backend (${DEV_BACKEND_PORT}). Press Ctrl+C to stop."
"${PYTHON_BIN}" -m uvicorn server:app --host "${DEV_HOST}" --port "${DEV_BACKEND_PORT}" --reload &
SERVER_PID=$!

cleanup() {
  kill "${SERVER_PID}" >/dev/null 2>&1 || true
  wait "${SERVER_PID}" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

wait "${SERVER_PID}"
