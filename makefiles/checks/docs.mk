# Documentation, diagram, and transcript validation targets.
.PHONY: lint-docs mermaid-render d3-render public-diagrams-render transcript-fix transcript-check end-docs-check

lint-docs:
	@$(call repo_activity,make lint-docs,lint-docs)
	npm run lint:docs

mermaid-render:
	$(PYTHON) -m tools.render_mermaid_diagrams

d3-render:
	$(PYTHON) -m tools.render_public_d3_diagrams

public-diagrams-render: mermaid-render d3-render

transcript-fix:
	$(PYTHON) -m tools.fix_transcripts

transcript-check:
	$(PYTHON) -m tools.validate_transcripts

end-docs-check:
	@$(call repo_activity,make end-docs-check,end-docs-check)
	$(PYTHON) -m tools.check_end_docs
