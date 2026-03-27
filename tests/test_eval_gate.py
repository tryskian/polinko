import unittest

from tools.eval_gate import resolve_binary_gate


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


if __name__ == "__main__":
    unittest.main()
