# Public diagram render checks.
.PHONY: mermaid-render d3-render public-diagrams-render

mermaid-render:
	$(PYTHON) -m tools.render_mermaid_diagrams

d3-render:
	$(PYTHON) -m tools.render_public_d3_diagrams

public-diagrams-render: mermaid-render d3-render
