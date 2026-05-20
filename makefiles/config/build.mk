# Build and dependency management configuration.
REQUIREMENTS_IN ?= requirements.in
REQUIREMENTS_LOCK ?= requirements.lock
PIP_TOOLS_VERSION ?= 7.5.3
# PYSEC-2025-183 / CVE-2025-45768 is a disputed PyJWT advisory with no
# released fix. PyJWT is present transitively through mcp, and Polinko has no
# direct JWT use. Keep the exception narrow so other audit findings still fail.
PIP_AUDIT_IGNORED_VULNS ?= PYSEC-2025-183
PIP_AUDIT_ARGS = $(foreach vuln,$(PIP_AUDIT_IGNORED_VULNS),--ignore-vuln $(vuln))
