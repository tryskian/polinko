# Portfolio dependency install targets.
.PHONY: portfolio-install portfolio-app-install frontend-install

portfolio-install:
	@set -eu; \
	if [ ! -f "$(PORTFOLIO_APP_DIR)/package.json" ]; then \
		echo "Portfolio app source not present at $(PORTFOLIO_APP_DIR)/package.json; skipping npm install."; \
		exit 0; \
	fi; \
	if [ -f "$(PORTFOLIO_APP_DIR)/package-lock.json" ]; then \
		npm --prefix "$(PORTFOLIO_APP_DIR)" ci --no-audit --no-fund; \
	else \
		npm --prefix "$(PORTFOLIO_APP_DIR)" install --no-audit --no-fund; \
	fi

portfolio-app-install frontend-install: portfolio-install
	@echo "Legacy alias: use make portfolio-install."
