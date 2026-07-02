# Local browser and Playwright helper targets.
.PHONY: pwcli playwright-cli playwright-snapshot-dir

pwcli playwright-cli:
	@$(call repo_activity,make $@,$@)
	@test -x "$(PWCLI_TOOL)" || { echo "local browser helper: missing executable: $(PWCLI_TOOL)" >&2; exit 127; }
	@PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" \
		PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" \
		PLAYWRIGHT_SNAPSHOT_STAMP="$(PLAYWRIGHT_SNAPSHOT_STAMP)" \
		PLAYWRIGHT_SESSION="$(PLAYWRIGHT_SESSION)" \
		"$(PWCLI_TOOL)" $(ARGS)

playwright-snapshot-dir:
	@$(call repo_activity,make playwright-snapshot-dir,playwright-snapshot-dir)
	@test -x "$(PWCLI_TOOL)" || { echo "local browser helper: missing executable: $(PWCLI_TOOL)" >&2; exit 127; }
	@PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" \
		PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" \
		"$(PWCLI_TOOL)" --print-dir
