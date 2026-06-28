# Unit test entrypoints.
.PHONY: test test-one test-targeted

test:
	@$(call repo_activity,make test,test)
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

test-one:
	@set -eu; \
	if [ -z "$(TEST)" ]; then \
		echo 'Usage: make test-one TEST=tests.test_eval_file_search'; \
		exit 2; \
	fi; \
	$(PYTHON) -m unittest $(TEST)

test-targeted:
	@set -eu; \
	if [ -z "$(TESTS)" ]; then \
		echo 'Usage: make test-targeted TESTS="tests.test_eval_file_search tests.test_eval_retrieval"'; \
		exit 2; \
	fi; \
	$(PYTHON) -m unittest $(TESTS)
