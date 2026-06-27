# Local browser and Playwright surface configuration.
PLAYWRIGHT_SNAPSHOT_BASE_DIR ?= docs/peanut/assets/screenshots/playwright
PLAYWRIGHT_SNAPSHOT_DAY ?= $(shell date +%d-%m-%y)
PLAYWRIGHT_SESSION ?= polinko
PWCLI_TOOL ?= tools/pwcli_daily.sh
