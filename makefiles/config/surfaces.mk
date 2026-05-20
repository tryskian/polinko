# Notebook, portfolio, mockup, and local browser surface configuration.
DEV_PORTFOLIO_URL ?= http://$(DEV_HOST):$(DEV_BACKEND_PORT)/portfolio
# Legacy compatibility only: prefer PORTFOLIO_APP_DIR for new usage.
ifneq ($(origin FRONTEND_DIR), undefined)
PORTFOLIO_APP_DIR ?= $(FRONTEND_DIR)
else
PORTFOLIO_APP_DIR ?= apps/portfolio
endif
FRONTEND_DIR ?= $(PORTFOLIO_APP_DIR)
PORTFOLIO_STATIC_DIR ?= public/portfolio
PORTFOLIO_MOCKUP_DIR ?= docs/peanut/assets/portfolio-mockups
PORTFOLIO_MOCKUP_PORT ?= 8765
PORTFOLIO_MOCKUP_URL ?= http://127.0.0.1:$(PORTFOLIO_MOCKUP_PORT)/landing-mockups.html
PORTFOLIO_LAUNCH ?= none
PORTFOLIO_PLAYWRIGHT_SESSION ?= $(PLAYWRIGHT_SESSION)
NOTEBOOK_START_PATH ?= output/jupyter-notebook/ocr-eval-live-filters-starter.ipynb
NOTEBOOK_START_PATH_ABS := $(abspath $(NOTEBOOK_START_PATH))
NOTEBOOK_DIR_ABS := $(abspath output/jupyter-notebook)
PORTFOLIO_MOCKUP_PID_FILE ?= /tmp/polinko-portfolio-mockups.pid
PORTFOLIO_MOCKUP_LOG ?= /tmp/polinko-portfolio-mockups.log
PLAYWRIGHT_SNAPSHOT_BASE_DIR ?= docs/peanut/assets/screenshots/playwright
PLAYWRIGHT_SNAPSHOT_DAY ?= $(shell date +%d-%m-%y)
PLAYWRIGHT_SESSION ?= polinko
PWCLI_TOOL ?= tools/pwcli_daily.sh
