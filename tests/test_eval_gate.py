import unittest

from tools.eval_gate import gate_counts_from_case_results
from tools.eval_gate import resolve_binary_gate
from tools.eval_gate import resolve_fail_closed_status


class EvalGateTests(unittest.TestCase):
    def test_resolve_binary_gate_passes_when_all_dimensions_pass(self) -> None:
        decision = resolve_binary_gate(
            policy_pass=True,
            high_value_alignment_pass=True,
            evidence_complete=True,
        )
        self.assertTrue(decision.passed)
        self.assertEqual(decision.outcome, "pass")
        self.assertEqual(decision.reasons, ())

    def test_resolve_binary_gate_fails_closed_on_policy(self) -> None:
        decision = resolve_binary_gate(
            policy_pass=False,
            high_value_alignment_pass=True,
            evidence_complete=True,
        )
        self.assertFalse(decision.passed)
        self.assertEqual(decision.outcome, "fail")
        self.assertIn("policy gate failed", decision.reasons)

    def test_resolve_binary_gate_fails_closed_on_alignment(self) -> None:
        decision = resolve_binary_gate(
            policy_pass=True,
            high_value_alignment_pass=False,
            evidence_complete=True,
        )
        self.assertFalse(decision.passed)
        self.assertIn("high-value alignment gate failed", decision.reasons)

    def test_resolve_binary_gate_fails_closed_on_evidence(self) -> None:
        decision = resolve_binary_gate(
            policy_pass=True,
            high_value_alignment_pass=True,
            evidence_complete=False,
        )
        self.assertFalse(decision.passed)
        self.assertIn("evidence completeness gate failed", decision.reasons)

    def test_reason_overrides_are_applied(self) -> None:
        decision = resolve_binary_gate(
            policy_pass=False,
            high_value_alignment_pass=False,
            evidence_complete=False,
            reason_overrides={
                "policy_pass": "policy denied",
                "high_value_alignment_pass": "alignment denied",
                "evidence_complete": "evidence denied",
            },
        )
        self.assertEqual(
            decision.reasons,
            ("policy denied", "alignment denied", "evidence denied"),
        )

    def test_fail_closed_status_maps_pass_to_pass(self) -> None:
        decision = resolve_fail_closed_status(status="PASS")
        self.assertTrue(decision.passed)
        self.assertEqual(decision.outcome, "pass")

    def test_fail_closed_status_maps_error_to_fail(self) -> None:
        decision = resolve_fail_closed_status(status="ERROR", detail="timeout")
        self.assertFalse(decision.passed)
        self.assertEqual(decision.outcome, "fail")
        self.assertIn("case status=error (timeout)", decision.reasons)

    def test_gate_counts_from_case_results_counts_non_pass_as_fail(self) -> None:
        gate_passed, gate_failed = gate_counts_from_case_results(
            [
                {"gate_outcome": "pass"},
                {"gate_outcome": "fail"},
                {"gate_outcome": "skip"},
                {"gate_outcome": ""},
            ]
        )
        self.assertEqual(gate_passed, 1)
        self.assertEqual(gate_failed, 3)


if __name__ == "__main__":
    unittest.main()
