# Portfolio build targets.
.PHONY: portfolio-build frontend-build

portfolio-build: portfolio-install
	@set -eu; \
	if [ ! -f "$(PORTFOLIO_APP_DIR)/package.json" ]; then \
		echo "Portfolio app source not present at $(PORTFOLIO_APP_DIR)/package.json; using tracked /portfolio fallback."; \
		exit 0; \
	fi; \
	POLINKO_PORTFOLIO_STATIC_DIR="$(abspath $(PORTFOLIO_STATIC_DIR))" npm --prefix "$(PORTFOLIO_APP_DIR)" run build

frontend-build: portfolio-build
	@echo "Legacy alias: use make portfolio-build."
