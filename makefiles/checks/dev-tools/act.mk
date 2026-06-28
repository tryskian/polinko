# Local GitHub Actions runner helper targets.
.PHONY: act-list act-ci

act-list:
	$(ACT) -l

act-ci:
	$(ACT) -W .github/workflows/ci.yml
