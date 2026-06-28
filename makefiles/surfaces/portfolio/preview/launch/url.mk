# Portfolio preview cache-busted URL construction.
define portfolio_preview_open_url
URL="$(DEV_PORTFOLIO_URL)"; \
CACHE_BUST="$$(date +%s)"; \
case "$$URL" in \
	*\?*) OPEN_URL="$$URL&rebuild=$$CACHE_BUST" ;; \
	*) OPEN_URL="$$URL?rebuild=$$CACHE_BUST" ;; \
esac
endef
