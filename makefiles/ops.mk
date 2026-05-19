# External smoke and container checks.
.PHONY: k6-chat-smoke trivy-fs trivy-image docker-build docker-run

k6-chat-smoke:
	k6 run tests/perf/chat_smoke.js -e BASE_URL="$(K6_BASE_URL)" -e VUS="$(K6_VUS)" -e DURATION="$(K6_DURATION)"

trivy-fs:
	trivy fs --severity "$(TRIVY_SEVERITY)" --exit-code 1 .

trivy-image:
	$(DOCKER) build -t $(DOCKER_IMAGE) . && trivy image --severity "$(TRIVY_SEVERITY)" --exit-code 1 $(DOCKER_IMAGE)

docker-build:
	$(DOCKER) build -t $(DOCKER_IMAGE) .

docker-run:
	$(DOCKER) run --rm -p $(DOCKER_PORT):8000 --env-file $(ENV_FILE) $(DOCKER_IMAGE)
