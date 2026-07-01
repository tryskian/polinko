# Local GitHub Actions runner helper targets.
.PHONY: act-list act-ci

act-list:
	@$(call repo_activity,make act-list,act-list)
	@set -eu; \
	if ! command -v "$(ACT)" >/dev/null 2>&1; then \
		echo "act helper: missing required command: $(ACT)" >&2; \
		exit 127; \
	fi; \
	$(ACT) -l

act-ci:
	@$(call repo_activity,make act-ci,act-ci)
	@set -eu; \
	if ! command -v "$(ACT)" >/dev/null 2>&1; then \
		echo "act helper: missing required command: $(ACT)" >&2; \
		exit 127; \
	fi; \
	$(ACT) -W .github/workflows/ci.yml
