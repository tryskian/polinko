# OCR intake, mining, and benchmark case builders.
.PHONY: cgpt-export-index ocr-cases-from-export ocr-cases-from-export-build
.PHONY: ocr-handwriting-benchmark-cases ocr-typed-benchmark-cases ocr-illustration-benchmark-cases
.PHONY: ocr-generalization-review ocr-transcript-delta

cgpt-export-index:
	@set -eu; \
	EXPORT_ROOT="$(CGPT_EXPORT_ROOT)"; \
	if [ -z "$$EXPORT_ROOT" ]; then \
		EXPORT_ROOT="$(CGPT_EXPORT_ROOT_DEFAULT)"; \
	fi; \
	if [ -z "$$EXPORT_ROOT" ]; then \
		echo "CGPT_EXPORT_ROOT is required."; \
		echo "Run: make cgpt-export-index CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 2; \
	fi; \
	if [ ! -d "$$EXPORT_ROOT" ]; then \
		echo "CGPT export root not found: $$EXPORT_ROOT"; \
		echo "Run: make cgpt-export-index CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 2; \
	fi; \
	$(PYTHON) -m tools.index_cgpt_export --export-root "$$EXPORT_ROOT" --output-dir "$(CGPT_EXPORT_OUTPUT_DIR)"

ocr-cases-from-export: ocr-cases-from-export-build ocr-handwriting-benchmark-cases ocr-typed-benchmark-cases ocr-illustration-benchmark-cases ocr-transcript-delta

ocr-cases-from-export-build:
	@set -eu; \
	EXPORT_ROOT="$(CGPT_EXPORT_ROOT)"; \
	if [ -z "$$EXPORT_ROOT" ]; then \
		EXPORT_ROOT="$(CGPT_EXPORT_ROOT_DEFAULT)"; \
	fi; \
	if [ -z "$$EXPORT_ROOT" ]; then \
		echo "CGPT_EXPORT_ROOT is required."; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 2; \
	fi; \
	if [ ! -d "$$EXPORT_ROOT" ]; then \
		echo "CGPT export root not found: $$EXPORT_ROOT"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 2; \
	fi; \
	if [ -f "$(OCR_TRANSCRIPT_REVIEW)" ]; then \
		cp "$(OCR_TRANSCRIPT_REVIEW)" "$(OCR_TRANSCRIPT_REVIEW_PREV)"; \
	fi; \
	$(PYTHON) -m tools.build_ocr_cases_from_export \
		--export-root "$$EXPORT_ROOT" \
		--output-cases "$(OCR_TRANSCRIPT_CASES_ALL)" \
		--output-cases-growth "$(OCR_TRANSCRIPT_CASES_GROWTH)" \
		--output-cases-handwriting "$(OCR_TRANSCRIPT_CASES_HANDWRITING)" \
		--output-cases-typed "$(OCR_TRANSCRIPT_CASES_TYPED)" \
		--output-cases-illustration "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION)" \
		--output-review "$(OCR_TRANSCRIPT_REVIEW)" \
		--output-generalization-candidates "$(OCR_GENERALIZATION_CANDIDATES)" \
		--max-growth-cases "$(OCR_GROWTH_MAX_CASES)" $(OCR_CASES_FROM_EXPORT_ARGS)

ocr-handwriting-benchmark-cases:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_REVIEW)" ]; then \
		echo "Transcript OCR review not found: $(OCR_TRANSCRIPT_REVIEW)"; \
		exit 1; \
	fi; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_HANDWRITING)" ]; then \
		echo "Transcript handwriting OCR cases not found: $(OCR_TRANSCRIPT_CASES_HANDWRITING)"; \
		exit 1; \
	fi; \
	$(PYTHON) -m tools.build_handwriting_benchmark_cases \
		--review "$(OCR_TRANSCRIPT_REVIEW)" \
		--lane "handwriting" \
		--lane-cases "$(OCR_TRANSCRIPT_CASES_HANDWRITING)" \
		--output-cases "$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)" \
		--top-k "$(OCR_HANDWRITING_BENCHMARK_TOP_K)" \
		--min-anchor-terms "$(OCR_HANDWRITING_BENCHMARK_MIN_ANCHORS)"

ocr-generalization-review:
	@set -eu; \
	if [ ! -f "$(OCR_GENERALIZATION_CANDIDATES)" ]; then \
		echo "OCR generalization candidates not found: $(OCR_GENERALIZATION_CANDIDATES)"; \
		echo "Run: make ocrmine CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 1; \
	fi; \
	$(PYTHON) -m tools.build_ocr_generalization_review \
		--candidates "$(OCR_GENERALIZATION_CANDIDATES)" \
		--output-review "$(OCR_GENERALIZATION_REVIEW)" \
		--max-cases "$(OCR_GENERALIZATION_REVIEW_MAX_CASES)" \
		--max-per-conversation "$(OCR_GENERALIZATION_REVIEW_MAX_PER_CONVERSATION)" \
		--include-candidate-ids "$(OCR_GENERALIZATION_REVIEW_INCLUDE_IDS)"

ocr-typed-benchmark-cases:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_REVIEW)" ]; then \
		echo "Transcript OCR review not found: $(OCR_TRANSCRIPT_REVIEW)"; \
		exit 1; \
	fi; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_TYPED)" ]; then \
		echo "Transcript typed OCR cases not found: $(OCR_TRANSCRIPT_CASES_TYPED)"; \
		exit 1; \
	fi; \
	$(PYTHON) -m tools.build_handwriting_benchmark_cases \
		--review "$(OCR_TRANSCRIPT_REVIEW)" \
		--lane "typed" \
		--lane-cases "$(OCR_TRANSCRIPT_CASES_TYPED)" \
		--output-cases "$(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)" \
		--top-k "$(OCR_TYPED_BENCHMARK_TOP_K)" \
		--min-anchor-terms "$(OCR_TYPED_BENCHMARK_MIN_ANCHORS)"

ocr-illustration-benchmark-cases:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_REVIEW)" ]; then \
		echo "Transcript OCR review not found: $(OCR_TRANSCRIPT_REVIEW)"; \
		exit 1; \
	fi; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION)" ]; then \
		echo "Transcript illustration OCR cases not found: $(OCR_TRANSCRIPT_CASES_ILLUSTRATION)"; \
		exit 1; \
	fi; \
	$(PYTHON) -m tools.build_handwriting_benchmark_cases \
		--review "$(OCR_TRANSCRIPT_REVIEW)" \
		--lane "illustration" \
		--lane-cases "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION)" \
		--output-cases "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)" \
		--top-k "$(OCR_ILLUSTRATION_BENCHMARK_TOP_K)" \
		--min-anchor-terms "$(OCR_ILLUSTRATION_BENCHMARK_MIN_ANCHORS)"

ocr-transcript-delta:
	@set -eu; \
	$(PYTHON) -m tools.report_ocr_case_mining_delta \
		--current-review "$(OCR_TRANSCRIPT_REVIEW)" \
		--previous-review "$(OCR_TRANSCRIPT_REVIEW_PREV)" \
		--output-markdown "$(OCR_TRANSCRIPT_DELTA_MD)" \
		--output-json "$(OCR_TRANSCRIPT_DELTA_JSON)"; \
	echo "OCR transcript delta report: $(OCR_TRANSCRIPT_DELTA_MD)"
