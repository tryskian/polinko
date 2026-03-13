# Nautorus Runbook

## Local Baseline

1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `make test`

## Keep-Awake (Optional)

1. Start: `nohup caffeinate -di >/tmp/nautorus-caffeinate.log 2>&1 &`
2. Verify: `pmset -g assertions | rg "PreventUserIdleDisplaySleep|PreventUserIdleSystemSleep"`
3. Stop: `pkill -x caffeinate`

## Inspect Archived Frontend

1. `git show archive/polinko-frontend-2026-03-13:frontend/README.md`
2. `git ls-tree -r --name-only archive/polinko-frontend-2026-03-13 frontend`
