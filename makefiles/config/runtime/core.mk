# Core runtime application configuration.
DEV_HOST ?= 127.0.0.1
DEV_BACKEND_PORT ?= 8000
CLI_ENTRYPOINT ?= -m polinko.cli
ASGI_APP ?= server:app
DEV_API_DOCS_URL ?= http://$(DEV_HOST):$(DEV_BACKEND_PORT)/docs
DEV_VIZ_URL ?= http://$(DEV_HOST):$(DEV_BACKEND_PORT)/viz/pass-fail
