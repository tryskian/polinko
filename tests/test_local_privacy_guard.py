import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "local_privacy_guard.sh"
REPO_ROOT_HELPER = REPO_ROOT / "tools" / "repo_root.sh"


def _copy_helper_repo(tmp_path: Path) -> Path:
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    shutil.copy2(SCRIPT, tools_dir / SCRIPT.name)
    shutil.copy2(REPO_ROOT_HELPER, tools_dir / REPO_ROOT_HELPER.name)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    return tools_dir / SCRIPT.name


class LocalPrivacyGuardTests(unittest.TestCase):
    def test_apply_installs_current_handoff_exclude(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            script = _copy_helper_repo(tmp_path)

            result = subprocess.run(
                ["bash", str(script), "apply"],
                cwd=tmp_path,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            exclude_text = (tmp_path / ".git" / "info" / "exclude").read_text(
                encoding="utf-8"
            )
            self.assertIn("# polinko-local-privacy begin", exclude_text)
            self.assertIn("docs/peanut/governance/SESSION_HANDOFF.md", exclude_text)
            self.assertIn("Local privacy guard applied.", result.stdout)

    def test_apply_reports_blocked_exclude_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            script = _copy_helper_repo(tmp_path)
            info_dir = tmp_path / ".git" / "info"
            shutil.rmtree(info_dir)
            info_dir.write_text("not a directory", encoding="utf-8")

            result = subprocess.run(
                ["bash", str(script), "apply"],
                cwd=tmp_path,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "local-privacy failed to prepare exclude file parent: .git/info",
                result.stderr,
            )


if __name__ == "__main__":
    unittest.main()
