# k6 smoke targets.
.PHONY: k6-chat-smoke

k6-chat-smoke:
	@$(call repo_activity,make k6-chat-smoke,k6-chat-smoke)
	@set -eu; \
	if ! command -v "$(K6)" >/dev/null 2>&1; then \
		echo "k6 helper: missing required command: $(K6)" >&2; \
		exit 127; \
	fi
	$(K6) run tests/perf/chat_smoke.js -e BASE_URL="$(K6_BASE_URL)" -e VUS="$(K6_VUS)" -e DURATION="$(K6_DURATION)"
