# Manual eval warehouse database targets.
.PHONY: manual-evals-db manualdb manual-evals-db-refresh manualdb-refresh
.PHONY: manual-evals-db-status manualdb-status manual-evals-db-health manualdb-health

manual-evals-db manualdb manual-evals-db-refresh manualdb-refresh:
	$(PYTHON) -m tools.build_manual_evals_db \
		--optional-history-source beta_1_0=.local/legacy_eval/archive_legacy_eval/databases/.polinko_history.db \
		--history-source current=.local/runtime_dbs/active/history.db \
		--include-eval-sessions \
		--backup-existing \
		--status-summary

manual-evals-db-status manualdb-status:
	$(PYTHON) -m tools.manual_evals_db_status

manual-evals-db-health manualdb-health:
	$(MANUAL_EVALS_DB_HEALTH_COMMAND)
