# Portfolio preview non-Playwright launch modes.
define portfolio_preview_system
bash "$(LOCAL_URL_LAUNCHER_SCRIPT)" "$(1)"
endef

define portfolio_preview_none
echo "Portfolio URL: $(1)"
endef

define portfolio_preview_invalid_mode
echo "Invalid PORTFOLIO_LAUNCH='$(PORTFOLIO_LAUNCH)' (expected playwright, system, or none)."
endef
