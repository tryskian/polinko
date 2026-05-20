import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = "docs/research/pre-beta-2-4-research-model-contract-2026-05-19.md"


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class ResearchModelContractTests(unittest.TestCase):
    def test_pre_beta_2_4_contract_is_staged_and_source_bound(self) -> None:
        contract = _read(CONTRACT_PATH)

        for expected in (
            "Pre-Beta 2.4 Research Model Contract",
            "Status: `staged`",
            "`Beta 2.3`",
            "`pre-Beta 2.4`",
            "docs/eval/beta_2_3/",
            "discarded run-level rollup hypothesis",
            "source-first research claims",
            "`POST /chat`",
            "`/chats/*`",
            "`.local/runtime_dbs/active/manual_evals.db`",
            "`.local/runtime_dbs/active/history.db`",
            "`pass` / `fail`",
            "Run-level verdicts are not canonical rollups",
            "docs/eval/beta_2_4/",
        ):
            self.assertIn(expected, contract)

        normalized = " ".join(contract.split())
        self.assertIn("is not being carried forward as the next method", normalized)

        for rejected in (
            "Non-OCR research pulses can use run-level",
            "final pulse verdict",
            "source artifact to row label to pulse verdict",
            "Pulse-level verdicts are not canonical rollups",
        ):
            self.assertNotIn(rejected, contract)

    def test_current_truth_surfaces_name_the_staged_contract(self) -> None:
        for path in (
            "README.md",
            "docs/research/README.md",
            "docs/eval/README.md",
            "docs/governance/STATE.md",
            "docs/public/HYPOTHESIS.md",
        ):
            self.assertIn("pre-Beta 2.4", _read(path), path)

    def test_current_truth_surfaces_reject_pulse_carry_forward(self) -> None:
        expectations = {
            "README.md": "run-level rollup path is not being carried forward",
            "docs/research/README.md": (
                "run-level rollup hypothesis is not being carried forward"
            ),
            "docs/eval/README.md": (
                "run-level rollup hypothesis is not being carried forward"
            ),
            "docs/governance/STATE.md": (
                "run-level rollup hypothesis is not being carried forward"
            ),
            "docs/public/HYPOTHESIS.md": ("run-level verdicts are not carried forward"),
        }

        for path, expected in expectations.items():
            self.assertIn(expected, _read(path), path)

    def test_active_contract_surfaces_do_not_expose_pulse_as_live_method(self) -> None:
        for path in (
            "README.md",
            CONTRACT_PATH,
            "docs/eval/README.md",
            "docs/governance/STATE.md",
            "docs/public/HYPOTHESIS.md",
        ):
            self.assertNotIn("pulse", _read(path).lower(), path)

    def test_research_index_and_manifest_include_the_contract(self) -> None:
        research_index = _read("docs/research/README.md")
        self.assertIn(
            "[Pre-Beta 2.4 research model contract]",
            research_index,
        )
        self.assertIn(Path(CONTRACT_PATH).name, research_index)

        manifest = json.loads(_read("docs/research/research-manifest.json"))
        artifact_paths = {artifact["path"] for artifact in manifest["artifacts"]}

        self.assertIn(CONTRACT_PATH, artifact_paths)

        labels = {artifact["label"] for artifact in manifest["artifacts"]}
        self.assertIn(
            "Fail-pressure pulse hypothesis (not carried forward)",
            labels,
        )

    def test_fail_pressure_pulse_hypothesis_is_historical(self) -> None:
        pulse_hypothesis = _read(
            "docs/research/fail-pressure-pulse-hypothesis-2026-05-16.md"
        )
        normalized = " ".join(pulse_hypothesis.split())

        self.assertIn("Current disposition: `not carried forward`", pulse_hypothesis)
        self.assertIn("not the pre-Beta 2.4 forward path", normalized)

    def test_decision_log_supersedes_the_pulse_contract(self) -> None:
        decisions = _read("docs/governance/DECISIONS.md")

        self.assertIn("Current disposition: Superseded by `D-028`.", decisions)
        self.assertIn(
            "## D-028: Do not carry fail-pressure pulses into pre-Beta 2.4",
            decisions,
        )
        self.assertIn(
            "## D-041: Keep source-first workbench payloads free of run-level rollups",
            decisions,
        )

    def test_eval_map_keeps_manual_chat_sources_canonical(self) -> None:
        eval_map = _read("docs/eval/README.md")

        for expected in (
            "`POST /chat`",
            "`/chats/*`",
            "`.local/runtime_dbs/active/manual_evals.db`",
            "manual evals and chat workbench sources stay canonical inputs",
        ):
            self.assertIn(expected, eval_map)


if __name__ == "__main__":
    unittest.main()
