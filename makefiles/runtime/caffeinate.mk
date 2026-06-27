# Repo-managed keep-awake targets.
.PHONY: caffeinate caffeinate-on caffeinate-status caffeinate-off caffeinate-off-all decaffeinate decaffeinate-status

caffeinate:
	@$(CAFFEINATE_ENV) bash "$(CAFFEINATE_SCRIPT)" start

caffeinate-on: caffeinate

caffeinate-off: decaffeinate

caffeinate-off-all:
	@$(CAFFEINATE_ENV) bash "$(CAFFEINATE_SCRIPT)" stop-all

decaffeinate:
	@$(CAFFEINATE_ENV) bash "$(CAFFEINATE_SCRIPT)" stop

caffeinate-status:
	@$(CAFFEINATE_ENV) bash "$(CAFFEINATE_SCRIPT)" status

decaffeinate-status: caffeinate-status
