# OCR growth and fail-cohort defaults.
OCR_GROWTH_MAX_CASES ?= 600
OCR_GROWTH_STABILITY_OUTPUT ?= .local/eval_reports/ocr_growth_stability.json
OCR_GROWTH_STABILITY_REPORT_DIR ?= .local/eval_reports/ocr_growth_stability_runs
OCR_GROWTH_STABILITY_RUNS ?= $(OCR_STABILITY_RUNS)
OCR_GROWTH_METRICS_OUTPUT ?= .local/eval_reports/ocr_growth_metrics.json
OCR_GROWTH_METRICS_MARKDOWN ?= .local/eval_reports/ocr_growth_metrics.md
OCR_GROWTH_FAIL_COHORT_JSON ?= .local/eval_cases/ocr_growth_fail_cohort.json
OCR_GROWTH_FAIL_COHORT_MARKDOWN ?= .local/eval_reports/ocr_growth_fail_cohort.md
OCR_FAIL_COHORT_MIN_RUNS ?= 1
OCR_FAIL_COHORT_INCLUDE_UNSTABLE ?= true
OCR_FAIL_COHORT_REQUIRE_OCR_FRAMING ?= true
OCR_FAIL_COHORT_INCLUDE_EXPLORATORY ?= true
OCR_FAIL_COHORT_EXPLORATORY_MAX_CASES ?= 18
