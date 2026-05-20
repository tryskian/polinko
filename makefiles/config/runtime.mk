# Runtime, lifecycle, and local operator configuration.
DEV_HOST ?= 127.0.0.1
DEV_BACKEND_PORT ?= 8000
CLI_ENTRYPOINT ?= main.py
ASGI_APP ?= server:app
DEV_API_DOCS_URL ?= http://$(DEV_HOST):$(DEV_BACKEND_PORT)/docs
DEV_VIZ_URL ?= http://$(DEV_HOST):$(DEV_BACKEND_PORT)/viz/pass-fail
OPENAI_LIMITS_URL ?= https://platform.openai.com/settings/organization/limits
OPENAI_USAGE_URL ?= https://platform.openai.com/settings/organization/usage
OPENAI_BILLING_URL ?= https://platform.openai.com/settings/organization/billing/overview
CAFFEINATE_PID_FILE ?= /tmp/polinko-caffeinate.pid
CAFFEINATE_LOG ?= /tmp/polinko-caffeinate.log
CAFFEINATE_CMD ?= /usr/bin/caffeinate -d -i -m
SERVER_PID_FILE ?= /tmp/polinko-server.pid
SERVER_LOG ?= /tmp/polinko-server.log
