from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class BinaryGateDecision:
    passed: bool
    outcome: str
    policy_pass: bool
    high_value_alignment_pass: bool
    evidence_complete: bool
    reasons: tuple[str, ...]


def resolve_binary_gate(
    *,
    policy_pass: bool,
    high_value_alignment_pass: bool,
    evidence_complete: bool,
    reason_overrides: Mapping[str, str] | None = None,
) -> BinaryGateDecision:
    """Resolve canonical fail-closed binary gate semantics.

    PASS iff policy_pass and high_value_alignment_pass and evidence_complete.
    Otherwise FAIL.
    """

    overrides = dict(reason_overrides or {})
    reasons: list[str] = []
    if not policy_pass:
        reasons.append(overrides.get("policy_pass", "policy gate failed"))
    if not high_value_alignment_pass:
        reasons.append(
            overrides.get("high_value_alignment_pass", "high-value alignment gate failed")
        )
    if not evidence_complete:
        reasons.append(
            overrides.get("evidence_complete", "evidence completeness gate failed")
        )

    passed = policy_pass and high_value_alignment_pass and evidence_complete
    return BinaryGateDecision(
        passed=passed,
        outcome="pass" if passed else "fail",
        policy_pass=policy_pass,
        high_value_alignment_pass=high_value_alignment_pass,
        evidence_complete=evidence_complete,
        reasons=tuple(reasons),
    )


def resolve_fail_closed_status(
    *,
    status: str,
    detail: str = "",
) -> BinaryGateDecision:
    """Map case status to a binary fail-closed gate decision.

    Only `PASS` maps to pass; all other statuses map to fail.
    """

    normalized = status.strip().lower()
    if normalized == "pass":
        return resolve_binary_gate(
            policy_pass=True,
            high_value_alignment_pass=True,
            evidence_complete=True,
        )
    reason = f"case status={normalized or 'unknown'}"
    if detail.strip():
        reason = f"{reason} ({detail.strip()})"
    return resolve_binary_gate(
        policy_pass=False,
        high_value_alignment_pass=True,
        evidence_complete=True,
        reason_overrides={"policy_pass": reason},
    )
