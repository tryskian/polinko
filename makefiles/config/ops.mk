# External operator tooling configuration.
ACT ?= act
DOCKER ?= docker
DOCKER_IMAGE ?= polinko:dev
DOCKER_PORT ?= 8000
ENV_FILE ?= .env
K6_BASE_URL ?= http://127.0.0.1:8000
K6_VUS ?= 3
K6_DURATION ?= 10s
TRIVY_SEVERITY ?= HIGH,CRITICAL
