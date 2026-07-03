# PASS/FAIL viz local URL print and launch targets.
.PHONY: viz viz-open

viz: server-daemon
	@$(PYTHON) -m tools.local_url --url "$(DEV_VIZ_URL)" --label "PASS/FAIL viz URL" --mode "$(LOCAL_BROWSER_LAUNCH)" $(if $(filter system,$(LOCAL_BROWSER_LAUNCH)),--launcher "$(LOCAL_URL_LAUNCHER_SCRIPT)",)

viz-open: server-daemon
	@$(PYTHON) -m tools.local_url --url "$(DEV_VIZ_URL)" --label "PASS/FAIL viz URL" --mode system --launcher "$(LOCAL_URL_LAUNCHER_SCRIPT)"
