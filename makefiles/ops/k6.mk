# k6 smoke targets.
.PHONY: k6-chat-smoke

k6-chat-smoke:
	k6 run tests/perf/chat_smoke.js -e BASE_URL="$(K6_BASE_URL)" -e VUS="$(K6_VUS)" -e DURATION="$(K6_DURATION)"
