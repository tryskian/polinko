# Runtime, shell, and local configuration audit targets entrypoint.
include makefiles/checks/runtime-audits/shell.mk
include makefiles/checks/runtime-audits/path-leaks.mk
include makefiles/checks/runtime-audits/runtime-config.mk
include makefiles/checks/runtime-audits/doctor-env.mk
