# k6 smoke targets.
.PHONY: k6-chat-smoke

k6-chat-smoke:
	@$(call repo_activity,make k6-chat-smoke,k6-chat-smoke)
	@$(PYTHON) -m tools.require_command --command "$(K6)" --label "k6 helper"
	$(K6) run tests/perf/chat_smoke.js -e BASE_URL="$(K6_BASE_URL)" -e VUS="$(K6_VUS)" -e DURATION="$(K6_DURATION)"
