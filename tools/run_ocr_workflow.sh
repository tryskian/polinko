#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"
# shellcheck source=tools/make_runtime.sh
source "$script_dir/make_runtime.sh"

polinko_cd_repo_root
ROOT_DIR="$POLINKO_REPO_ROOT"
# shellcheck source=tools/ocr_workflow_common.sh
. "$script_dir/ocr_workflow_common.sh"

MAKE_BIN=$(polinko_require_make_command "ocr-workflow")

run_make() {
  "$MAKE_BIN" --no-print-directory "$@"
}

run_ocrkernel() {
  local export_root
  ocr_workflow_require_export_root "ocrkernel" 1
  export_root="$OCR_WORKFLOW_EXPORT_ROOT"

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
  ocr_workflow_require_export_root "ocr-data" 1
  export_root="$OCR_WORKFLOW_EXPORT_ROOT"

  run_make doctor-env
  run_make ocrmine CGPT_EXPORT_ROOT="$export_root"
  run_make ocr-generalization-review
  run_make ocrdelta
}

run_ocr_notebook_workflow() {
  local export_root
  ocr_workflow_require_export_root "ocr-notebook-workflow" 1
  export_root="$OCR_WORKFLOW_EXPORT_ROOT"

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
