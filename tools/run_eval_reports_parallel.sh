#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root
# shellcheck source=tools/python_runtime.sh
. "$script_dir/python_runtime.sh"

if [ "$#" -ne 0 ]; then
	echo "Usage: run_eval_reports_parallel.sh" >&2
	exit 2
fi

python_bin=$(polinko_default_python_bin)
base_url=${BASE_URL:-http://127.0.0.1:8000}
run_id=${EVAL_REPORTS_PARALLEL_RUN_ID:-$(date +%Y%m%d-%H%M%S)}
hallucination_mode=${HALLUCINATION_EVAL_MODE:-judge}
hallucination_min_acceptable_score=${HALLUCINATION_MIN_ACCEPTABLE_SCORE:-5}

exec "$python_bin" -m tools.eval_parallel_orchestrator \
	--base-url "$base_url" \
	--run-id "$run_id" \
	--hallucination-mode "$hallucination_mode" \
	--hallucination-min-acceptable-score "$hallucination_min_acceptable_score"
