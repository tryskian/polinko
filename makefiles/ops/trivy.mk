# Trivy scan targets.
.PHONY: trivy-fs trivy-image

trivy-fs:
	@$(call repo_activity,make trivy-fs,trivy-fs)
	@$(PYTHON) -m tools.require_command --command "$(TRIVY)" --label "trivy helper"
	$(TRIVY) fs --severity "$(TRIVY_SEVERITY)" --exit-code 1 .

trivy-image:
	@$(call repo_activity,make trivy-image,trivy-image)
	@$(PYTHON) -m tools.require_command --command "$(DOCKER)" --label "trivy helper"
	@$(PYTHON) -m tools.require_command --command "$(TRIVY)" --label "trivy helper"
	$(DOCKER) build -t $(DOCKER_IMAGE) . && $(TRIVY) image --severity "$(TRIVY_SEVERITY)" --exit-code 1 $(DOCKER_IMAGE)
