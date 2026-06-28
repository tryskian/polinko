# OCR focus-run defaults.
OCR_FOCUS_CASES_JSON ?= .local/eval_cases/ocr_growth_focus_cases.json
OCR_FOCUS_RUNS ?= 3
OCR_FOCUS_MAX_CASES ?= 40
OCR_FOCUS_INCLUDE_FAIL_HISTORY ?= true
OCR_FOCUS_INCLUDE_EXPLORATORY ?= true
OCR_FOCUS_OUTPUT ?= .local/eval_reports/ocr_focus_stability.json
OCR_FOCUS_REPORT_DIR ?= .local/eval_reports/ocr_focus_runs
OCR_FOCUS_FAIL_PATTERNS_JSON ?= .local/eval_reports/ocr_focus_fail_patterns.json
OCR_FOCUS_FAIL_PATTERNS_MD ?= .local/eval_reports/ocr_focus_fail_patterns.md
OCR_FOCUS_OCR_RETRIES ?= 3
OCR_FOCUS_OCR_RETRY_DELAY_MS ?= 1000
OCR_FOCUS_CASE_DELAY_MS ?= 1200
OCR_FOCUS_RATE_LIMIT_COOLDOWN_MS ?= 12000
OCR_FOCUS_SKIP_RECENT_RATE_LIMIT ?= true
OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS ?= 900
