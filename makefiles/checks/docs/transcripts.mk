# Transcript formatting and validation checks.
.PHONY: transcript-fix transcript-check

transcript-fix:
	@$(call repo_activity,make transcript-fix,transcript-fix)
	$(PYTHON) -m tools.fix_transcripts

transcript-check:
	@$(call repo_activity,make transcript-check,transcript-check)
	$(PYTHON) -m tools.validate_transcripts
