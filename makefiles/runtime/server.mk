# Local server and server-daemon targets.
.PHONY: localhost server server-daemon server-daemon-stop server-daemon-status

localhost server:
	$(PYTHON) -m uvicorn $(ASGI_APP) --host "$(DEV_HOST)" --port "$(DEV_BACKEND_PORT)" --reload

server-daemon:
	@$(SERVER_DAEMON_ENV) bash "$(SERVER_DAEMON_SCRIPT)" start

server-daemon-stop:
	@$(SERVER_DAEMON_ENV) bash "$(SERVER_DAEMON_SCRIPT)" stop

server-daemon-status:
	@$(SERVER_DAEMON_ENV) bash "$(SERVER_DAEMON_SCRIPT)" status
