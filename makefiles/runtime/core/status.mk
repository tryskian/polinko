# Consolidated runtime status target.
.PHONY: session-status

session-status:
	@echo "== Server =="
	@$(MAKE) --no-print-directory server-daemon-status || true
	@echo ""
	@echo "== Eval sidecar =="
	@$(MAKE) --no-print-directory eval-sidecar-status || true
	@echo ""
	@echo "== Keep-awake =="
	@$(MAKE) --no-print-directory caffeinate-status || true
