#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"
# shellcheck source=tools/shell_command_common.sh
source "$script_dir/shell_command_common.sh"
# shellcheck source=tools/python_runtime.sh
source "$script_dir/python_runtime.sh"

polinko_cd_repo_root

python_bin=$(polinko_default_python_bin)
source_notebook=${BUILD_WEEK_OCR_NOTEBOOK_SOURCE:-docs/peanut/publication/build-week-ocr-eval-demo.ipynb}
output_dir=${BUILD_WEEK_OCR_NOTEBOOK_OUTPUT_DIR:-.local/notebooks/build-week-ocr-demo}
executed_name=${BUILD_WEEK_OCR_NOTEBOOK_EXECUTED_NAME:-build-week-ocr-eval-demo.executed.ipynb}
html_name=${BUILD_WEEK_OCR_NOTEBOOK_HTML_NAME:-build-week-ocr-eval-demo.html}
timeout_seconds=${BUILD_WEEK_OCR_NOTEBOOK_TIMEOUT:-240}
open_output=${BUILD_WEEK_OCR_NOTEBOOK_OPEN:-1}

executed_path="$output_dir/$executed_name"
html_path="$output_dir/$html_name"

echo "== Polinko Build Week OCR notebook demo =="
echo "Executes the local notebook demo and writes replayable artifacts."
echo

if [ ! -f "$source_notebook" ]; then
	echo "Missing source notebook: $source_notebook" >&2
	echo "Expected the local Build Week notebook created under docs/peanut/publication/." >&2
	exit 2
fi

"$python_bin" - <<'PY'
from __future__ import annotations

import importlib.util
import sys

if importlib.util.find_spec("nbconvert") is None:
    print("Missing Python module: nbconvert", file=sys.stderr)
    print("Run: make notebook-setup", file=sys.stderr)
    raise SystemExit(2)
PY

mkdir -p "$output_dir"

echo "source_notebook=$source_notebook"
echo "output_notebook=$executed_path"
echo "output_html=$html_path"
echo

echo "1. Execute notebook"
"$python_bin" -m nbconvert \
	--to notebook \
	--execute "$source_notebook" \
	--output-dir "$output_dir" \
	--output "$executed_name" \
	--ExecutePreprocessor.timeout="$timeout_seconds"
echo

echo "2. Render executed notebook to HTML"
"$python_bin" -m nbconvert \
	--to html \
	"$executed_path" \
	--output-dir "$output_dir" \
	--output "$html_name"
echo

echo "3. Demo artifacts"
echo "executed_notebook=$executed_path"
echo "html=$html_path"

if [ "$open_output" != "0" ]; then
	if polinko_command_available open; then
		echo "opening_html=yes"
		open "$html_path"
	else
		echo "opening_html=no"
	fi
else
	echo "opening_html=disabled"
fi
