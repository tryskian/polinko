# Manual eval warehouse database targets.
.PHONY: manual-evals-db manual-evals-db-refresh
.PHONY: manual-evals-db-status manual-evals-db-health

manual-evals-db manual-evals-db-refresh:
	$(PYTHON) -m tools.build_manual_evals_db \
		--optional-history-source beta_1_0=.local/legacy_eval/archive_legacy_eval/databases/.polinko_history.db \
		--history-source current=.local/runtime_dbs/active/history.db \
		--include-eval-sessions \
		--backup-existing \
		--status-summary

manual-evals-db-status:
	$(PYTHON) -m tools.manual_evals_db_status

manual-evals-db-health:
	$(MANUAL_EVALS_DB_HEALTH_COMMAND)
