# Portfolio app URL and path defaults.
DEV_PORTFOLIO_URL ?= http://$(DEV_HOST):$(DEV_BACKEND_PORT)/portfolio
# Legacy compatibility only: prefer PORTFOLIO_APP_DIR for new usage.
ifneq ($(origin FRONTEND_DIR), undefined)
PORTFOLIO_APP_DIR ?= $(FRONTEND_DIR)
else
PORTFOLIO_APP_DIR ?= apps/portfolio
endif
FRONTEND_DIR ?= $(PORTFOLIO_APP_DIR)
PORTFOLIO_STATIC_DIR ?= public/portfolio
