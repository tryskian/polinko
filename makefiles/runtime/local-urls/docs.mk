# API docs local URL print and launch targets.
.PHONY: docs docs-open

docs: server-daemon
	@$(PYTHON) -m tools.local_url --url "$(DEV_API_DOCS_URL)" --label "API docs URL" --mode "$(LOCAL_BROWSER_LAUNCH)" $(if $(filter system,$(LOCAL_BROWSER_LAUNCH)),--launcher "$(LOCAL_URL_LAUNCHER_SCRIPT)",)

docs-open: server-daemon
	@$(PYTHON) -m tools.local_url --url "$(DEV_API_DOCS_URL)" --label "API docs URL" --mode system --launcher "$(LOCAL_URL_LAUNCHER_SCRIPT)"
