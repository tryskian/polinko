import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    "docs/research/pre-beta-2-4-research-model-contract-2026-05-19.md"
)


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
            "`POST /chat`",
            "`/chats/*`",
            "`.local/runtime_dbs/active/manual_evals.db`",
            "`.local/runtime_dbs/active/history.db`",
            "`anchor`",
            "`counted seam`",
            "`excluded noise`",
            "`PASS` / `FAIL`",
            "`pass` / `fail`",
            "docs/eval/beta_2_4/",
        ):
            self.assertIn(expected, contract)

    def test_current_truth_surfaces_name_the_staged_contract(self) -> None:
        for path in (
            "README.md",
            "docs/research/README.md",
            "docs/eval/README.md",
            "docs/governance/STATE.md",
            "docs/public/HYPOTHESIS.md",
        ):
            self.assertIn("pre-Beta 2.4", _read(path), path)

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
