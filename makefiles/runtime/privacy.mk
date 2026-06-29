# Machine-local privacy guard targets.
.PHONY: privacy-local-on privacy-local-status privacy-local-off

privacy-local-on:
	@$(call repo_activity,make privacy-local-on,privacy-local-on)
	bash tools/local_privacy_guard.sh apply

privacy-local-status:
	bash tools/local_privacy_guard.sh status

privacy-local-off:
	@$(call repo_activity,make privacy-local-off,privacy-local-off)
	bash tools/local_privacy_guard.sh clear
