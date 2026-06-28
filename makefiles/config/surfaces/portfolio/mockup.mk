# Portfolio mockup server defaults.
PORTFOLIO_MOCKUP_DIR ?= docs/peanut/assets/portfolio-mockups
PORTFOLIO_MOCKUP_PORT ?= 8765
PORTFOLIO_MOCKUP_URL ?= http://127.0.0.1:$(PORTFOLIO_MOCKUP_PORT)/landing-mockups.html
PORTFOLIO_MOCKUP_SCRIPT ?= ./tools/run_portfolio_mockups.sh
PORTFOLIO_MOCKUP_PID_FILE ?= /tmp/polinko-portfolio-mockups.pid
PORTFOLIO_MOCKUP_LOG ?= /tmp/polinko-portfolio-mockups.log
PORTFOLIO_MOCKUP_LAUNCHER_PYTHON ?= $(PYTHON)
