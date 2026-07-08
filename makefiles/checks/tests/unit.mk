# Unit test entrypoints.
TEST_TIMING_LIMIT ?= 30
TEST_TIMING_MIN ?= 0.1

.PHONY: test test-one test-targeted test-timing

test:
	@$(call repo_activity,make test,test)
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

test-one:
	@$(PYTHON) -m tools.validate_make_variable --value "$(TEST)" --usage 'Usage: make test-one TEST=tests.test_eval_file_search'
	@$(call repo_activity,make test-one,test-one)
	$(PYTHON) -m unittest $(TEST)

test-targeted:
	@$(PYTHON) -m tools.validate_make_variable --value "$(TESTS)" --usage 'Usage: make test-targeted TESTS="tests.test_eval_file_search tests.test_eval_retrieval"'
	@$(call repo_activity,make test-targeted,test-targeted)
	$(PYTHON) -m unittest $(TESTS)

test-timing:
	@$(call repo_activity,make test-timing,test-timing)
	$(PYTHON) -m pytest tests --durations="$(TEST_TIMING_LIMIT)" --durations-min="$(TEST_TIMING_MIN)"
