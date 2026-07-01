# Trivy scan targets.
.PHONY: trivy-fs trivy-image

trivy-fs:
	@$(call repo_activity,make trivy-fs,trivy-fs)
	@set -eu; \
	if ! command -v "$(TRIVY)" >/dev/null 2>&1; then \
		echo "trivy helper: missing required command: $(TRIVY)" >&2; \
		exit 127; \
	fi
	$(TRIVY) fs --severity "$(TRIVY_SEVERITY)" --exit-code 1 .

trivy-image:
	@$(call repo_activity,make trivy-image,trivy-image)
	@set -eu; \
	if ! command -v "$(DOCKER)" >/dev/null 2>&1; then \
		echo "trivy helper: missing required command: $(DOCKER)" >&2; \
		exit 127; \
	fi; \
	if ! command -v "$(TRIVY)" >/dev/null 2>&1; then \
		echo "trivy helper: missing required command: $(TRIVY)" >&2; \
		exit 127; \
	fi
	$(DOCKER) build -t $(DOCKER_IMAGE) . && $(TRIVY) image --severity "$(TRIVY_SEVERITY)" --exit-code 1 $(DOCKER_IMAGE)
