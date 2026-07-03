# Docker lifecycle targets.
.PHONY: docker-build docker-run

docker-build:
	@$(call repo_activity,make docker-build,docker-build)
	@$(PYTHON) -m tools.require_command --command "$(DOCKER)" --label "docker helper"
	$(DOCKER) build -t $(DOCKER_IMAGE) .

docker-run:
	@$(call repo_activity,make docker-run,docker-run)
	@$(PYTHON) -m tools.require_command --command "$(DOCKER)" --label "docker helper"
	$(DOCKER) run --rm -p $(DOCKER_PORT):8000 --env-file $(ENV_FILE) $(DOCKER_IMAGE)
