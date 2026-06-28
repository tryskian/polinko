# Transcript formatting and validation checks.
.PHONY: transcript-fix transcript-check

transcript-fix:
	$(PYTHON) -m tools.fix_transcripts

transcript-check:
	$(PYTHON) -m tools.validate_transcripts
