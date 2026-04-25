#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
NPM_BIN="${NPM_BIN:-npm}"
DEV_HOST="${DEV_HOST:-127.0.0.1}"
DEV_BACKEND_PORT="${DEV_BACKEND_PORT:-8000}"
DEV_FRONTEND_PORT="${DEV_FRONTEND_PORT:-5173}"
DEV_AUTOKILL="${DEV_AUTOKILL:-1}"
DEV_STOP_ONLY="${DEV_STOP_ONLY:-0}"
DEV_WITH_UI="${DEV_WITH_UI:-0}"

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

    if [[ "${cmd}" == *"uvicorn"* || "${cmd}" == *"vite"* || "${cmd}" == *"server:app"* ]]; then
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

HAS_LSOF=1
if ! command -v lsof >/dev/null 2>&1; then
  HAS_LSOF=0
  echo "warning: lsof not found; skipping port preflight."
fi

if [[ "${HAS_LSOF}" == "1" ]]; then
  kill_port_listeners "${DEV_BACKEND_PORT}"
  if [[ "${DEV_WITH_UI}" == "1" || "${DEV_STOP_ONLY}" == "1" ]]; then
    kill_port_listeners "${DEV_FRONTEND_PORT}"
  fi
fi

if [[ "${DEV_STOP_ONLY}" == "1" ]]; then
  if [[ "${HAS_LSOF}" == "0" ]]; then
    echo "No lsof available; skipped listener stop preflight."
    exit 0
  fi
  echo "Stopped listeners on ${DEV_BACKEND_PORT} and ${DEV_FRONTEND_PORT}."
  exit 0
fi

if [[ "${DEV_WITH_UI}" == "1" ]]; then
  echo "Starting backend (${DEV_BACKEND_PORT}) and frontend (${DEV_FRONTEND_PORT}). Press Ctrl+C to stop both."
else
  echo "Starting backend only on ${DEV_BACKEND_PORT} (manual eval mode). Press Ctrl+C to stop."
fi
"${PYTHON_BIN}" -m uvicorn server:app --host "${DEV_HOST}" --port "${DEV_BACKEND_PORT}" --reload &
SERVER_PID=$!
UI_PID=""
if [[ "${DEV_WITH_UI}" == "1" ]]; then
  (
    cd frontend
    "${NPM_BIN}" run dev -- --host "${DEV_HOST}" --port "${DEV_FRONTEND_PORT}" --strictPort
  ) &
  UI_PID=$!
fi

cleanup() {
  if [[ -n "${UI_PID}" ]]; then
    kill "${SERVER_PID}" "${UI_PID}" >/dev/null 2>&1 || true
    wait "${SERVER_PID}" "${UI_PID}" >/dev/null 2>&1 || true
  else
    kill "${SERVER_PID}" >/dev/null 2>&1 || true
    wait "${SERVER_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

if [[ -n "${UI_PID}" ]]; then
  wait "${SERVER_PID}" "${UI_PID}"
else
  wait "${SERVER_PID}"
fi
