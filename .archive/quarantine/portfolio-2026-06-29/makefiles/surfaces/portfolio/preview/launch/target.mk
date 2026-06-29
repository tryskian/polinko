# Portfolio preview launch target.
.PHONY: portfolio

portfolio: portfolio-build server-daemon-stop server-daemon
	@set -eu; \
	$(portfolio_preview_open_url); \
	case "$(PORTFOLIO_LAUNCH)" in \
		playwright) \
			$(call portfolio_preview_playwright,$$OPEN_URL) ;; \
		system) \
			$(call portfolio_preview_system,$$OPEN_URL) ;; \
		none) \
			$(call portfolio_preview_none,$$OPEN_URL) ;; \
		*) \
			$(portfolio_preview_invalid_mode); \
			exit 2 ;; \
	esac; \
	echo "Portfolio shell URL: $$OPEN_URL"
