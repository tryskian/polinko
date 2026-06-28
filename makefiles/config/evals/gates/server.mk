# Quality-gate local server configuration.
GATE_PORT ?= 8066
GATE_BASE_URL ?= http://127.0.0.1:$(GATE_PORT)
GATE_SESSION_DB ?= /tmp/polinko-quality-gate-sessions.db
GATE_VECTOR_DB ?= /tmp/polinko-quality-gate-vector.db
