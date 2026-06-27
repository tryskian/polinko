#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root
ROOT_DIR="$POLINKO_REPO_ROOT"

MAKE_BIN="${MAKE:-make}"
EXPORT_ROOT_RESOLVED=""

run_make() {
  "$MAKE_BIN" --no-print-directory "$@"
}

resolve_export_root() {
  local export_root="${CGPT_EXPORT_ROOT:-}"
  if [ -z "$export_root" ]; then
    export_root="${CGPT_EXPORT_ROOT_DEFAULT:-}"
  fi
  printf '%s\n' "$export_root"
}

require_export_root() {
  local target_name="$1"
  EXPORT_ROOT_RESOLVED="$(resolve_export_root)"

  if [ -z "$EXPORT_ROOT_RESOLVED" ]; then
    echo "CGPT_EXPORT_ROOT is required."
    echo "Run: make $target_name CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"
    exit 1
  fi
  if [ ! -d "$EXPORT_ROOT_RESOLVED" ]; then
    echo "CGPT export root not found: $EXPORT_ROOT_RESOLVED"
    echo "Run: make $target_name CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"
    exit 1
  fi
}

run_ocrkernel() {
  local export_root
  require_export_root "ocrkernel"
  export_root="$EXPORT_ROOT_RESOLVED"

  run_make doctor-env
  run_make ocrmine CGPT_EXPORT_ROOT="$export_root"
  run_make ocrdelta
  run_make ocrwiden
  run_make ocrstablegrowth
  run_make ocrgrowth
  run_make ocrfails
  run_make ocrfocuscases
  run_make eval-ocr-focus-stability
  run_make ocrfocusreport
}

run_ocr_data() {
  local export_root
  require_export_root "ocr-data"
  export_root="$EXPORT_ROOT_RESOLVED"

  run_make doctor-env
  run_make ocrmine CGPT_EXPORT_ROOT="$export_root"
  run_make ocr-generalization-review
  run_make ocrdelta
}

run_ocr_notebook_workflow() {
  local export_root
  require_export_root "ocr-notebook-workflow"
  export_root="$EXPORT_ROOT_RESOLVED"

  run_make doctor-env
  run_make ocrmine CGPT_EXPORT_ROOT="$export_root"
  run_make ocrall
  run_make ocrstable
  run_make ocrwiden
  run_make ocrstablegrowth
  run_make ocrgrowth
  run_make ocrfails
}

case "${1:-}" in
  ocrkernel)
    run_ocrkernel
    ;;
  ocr-data)
    run_ocr_data
    ;;
  ocr-notebook-workflow)
    run_ocr_notebook_workflow
    ;;
  *)
    echo "Usage: $0 {ocrkernel|ocr-data|ocr-notebook-workflow}" >&2
    exit 2
    ;;
esac
