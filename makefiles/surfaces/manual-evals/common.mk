# Shared manual eval target helpers.
manual_evals_db_health = @$(call repo_activity,make $@,$@) && $(MANUAL_EVALS_DB_HEALTH_COMMAND) $(1) $(strip $(2))
