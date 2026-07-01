# Docker lifecycle targets.
.PHONY: docker-build docker-run

docker-build:
	@$(call repo_activity,make docker-build,docker-build)
	@set -eu; \
	if ! command -v "$(DOCKER)" >/dev/null 2>&1; then \
		echo "docker helper: missing required command: $(DOCKER)" >&2; \
		exit 127; \
	fi
	$(DOCKER) build -t $(DOCKER_IMAGE) .

docker-run:
	@$(call repo_activity,make docker-run,docker-run)
	@set -eu; \
	if ! command -v "$(DOCKER)" >/dev/null 2>&1; then \
		echo "docker helper: missing required command: $(DOCKER)" >&2; \
		exit 127; \
	fi
	$(DOCKER) run --rm -p $(DOCKER_PORT):8000 --env-file $(ENV_FILE) $(DOCKER_IMAGE)
