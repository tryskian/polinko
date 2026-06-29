# Portfolio preview alias targets.
.PHONY: portfolio-rebuild rebuild portfolio-open portfolio-playwright

portfolio-rebuild rebuild: portfolio

portfolio-open: PORTFOLIO_LAUNCH = system
portfolio-open: portfolio

portfolio-playwright: PORTFOLIO_LAUNCH = playwright
portfolio-playwright: portfolio
