# Portfolio Quarantine Bundle

Date: 2026-06-29

This bundle preserves the deprecated Polinko portfolio app, static output,
Netlify config, preview/mockup helpers, and related Make fragments for porting
to the separate `krystian.io` repo.

These files are not part of the active Polinko runtime, dependency install,
build, or closeout. GitHub still tracks the archived npm lockfile for security:
Dependabot is configured for security updates only, and the Node security job
audits the lockfile without installing or building the archived app.

Active evidence Sankey code now lives in
`src/polinko/api/evidence_sankey.py`.
