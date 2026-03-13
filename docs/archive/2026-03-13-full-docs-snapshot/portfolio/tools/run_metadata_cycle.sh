#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
RAW_EVIDENCE_DIR="${REPO_ROOT}/docs/portfolio/raw_evidence"
TIMESTAMP_UTC="$(date -u +%Y%m%d-%H%M%SZ)"
SNAPSHOT_DIR="${RAW_EVIDENCE_DIR}/snapshots/${TIMESTAMP_UTC}"
PYTHON_BIN="${PYTHON:-python3}"

mkdir -p "${SNAPSHOT_DIR}"

cd "${REPO_ROOT}"

make evidence-index PYTHON="${PYTHON_BIN}"
make portfolio-metadata-audit PYTHON="${PYTHON_BIN}"

cp "${RAW_EVIDENCE_DIR}/index.json" "${SNAPSHOT_DIR}/index.json"
cp "${RAW_EVIDENCE_DIR}/index.md" "${SNAPSHOT_DIR}/index.md"
cp "${RAW_EVIDENCE_DIR}/metadata_audit.json" "${SNAPSHOT_DIR}/metadata_audit.json"
cp "${RAW_EVIDENCE_DIR}/metadata_audit.md" "${SNAPSHOT_DIR}/metadata_audit.md"

if [[ -f "${RAW_EVIDENCE_DIR}/triage_overrides.json" ]]; then
  cp "${RAW_EVIDENCE_DIR}/triage_overrides.json" "${SNAPSHOT_DIR}/triage_overrides.json"
fi

"${PYTHON_BIN}" - <<'PY' "${RAW_EVIDENCE_DIR}/metadata_audit.json" "${SNAPSHOT_DIR}/SUMMARY.txt" "${TIMESTAMP_UTC}"
import json
import sys

metadata_path = sys.argv[1]
summary_path = sys.argv[2]
timestamp = sys.argv[3]

with open(metadata_path, "r", encoding="utf-8") as f:
    findings = json.load(f)

errors = sum(1 for x in findings if x.get("level") == "ERROR")
warns = sum(1 for x in findings if x.get("level") == "WARN")

lines = [
    f"timestamp_utc={timestamp}",
    f"errors={errors}",
    f"warnings={warns}",
    f"status={'PASS' if errors == 0 else 'FAIL'}",
]

with open(summary_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
PY

echo "Metadata cycle complete."
echo "Snapshot: ${SNAPSHOT_DIR}"
