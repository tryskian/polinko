# Unit test entrypoints.
.PHONY: test test-one test-targeted

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
