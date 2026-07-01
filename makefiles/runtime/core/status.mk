# Consolidated runtime status target.
.PHONY: session-status

session-status:
	@status=0; \
	echo "== Server =="; \
	$(MAKE) --no-print-directory server-daemon-status || status=$$?; \
	echo ""; \
	echo "== Eval sidecar =="; \
	$(MAKE) --no-print-directory eval-sidecar-status || status=$$?; \
	echo ""; \
	echo "== Keep-awake =="; \
	$(MAKE) --no-print-directory caffeinate-status || status=$$?; \
	exit $$status
