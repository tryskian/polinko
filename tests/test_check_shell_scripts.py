from __future__ import annotations

import ast
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from tools import check_shell_scripts


class CheckShellScriptsTests(unittest.TestCase):
    def test_check_script_reports_shell_syntax_errors(self) -> None:
        original_repo_root = check_shell_scripts.REPO_ROOT
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "tools" / "bad.sh"
            script.parent.mkdir()
            script.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        "set -euo pipefail",
                        "if true; then",
                        "  echo broken",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            check_shell_scripts.REPO_ROOT = root
            try:
                failures = check_shell_scripts.check_script(Path("tools/bad.sh"))
            finally:
                check_shell_scripts.REPO_ROOT = original_repo_root

        self.assertTrue(
            any("fails bash syntax check" in failure for failure in failures),
            failures,
        )

    def test_check_script_reports_missing_root_helper_for_executables(self) -> None:
        original_repo_root = check_shell_scripts.REPO_ROOT
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "tools" / "rootless.sh"
            script.parent.mkdir()
            script.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        "set -euo pipefail",
                        "echo ok",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            check_shell_scripts.REPO_ROOT = root
            try:
                failures = check_shell_scripts.check_script(Path("tools/rootless.sh"))
            finally:
                check_shell_scripts.REPO_ROOT = original_repo_root

        self.assertIn(
            "does not include root-helper script_dir resolver",
            failures,
        )
        self.assertIn(
            "does not include root-helper snippet 'source \"$script_dir/repo_root.sh\"'",
            failures,
        )
        self.assertIn(
            "does not include root-helper snippet 'polinko_cd_repo_root'",
            failures,
        )

    def test_check_script_reports_missing_script_dir_resolver(self) -> None:
        original_repo_root = check_shell_scripts.REPO_ROOT
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "tools" / "unsafe-root.sh"
            helper = root / "tools" / "repo_root.sh"
            script.parent.mkdir()
            helper.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        "set -euo pipefail",
                        "polinko_cd_repo_root() { :; }",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            script.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        "set -euo pipefail",
                        'source "$script_dir/repo_root.sh"',
                        "polinko_cd_repo_root",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            check_shell_scripts.REPO_ROOT = root
            try:
                failures = check_shell_scripts.check_script(
                    Path("tools/unsafe-root.sh")
                )
            finally:
                check_shell_scripts.REPO_ROOT = original_repo_root

        self.assertEqual(failures, ["does not include root-helper script_dir resolver"])

    def test_root_helper_exempt_executables_are_valid(self) -> None:
        for script in (
            Path("tools/open_local_url.sh"),
            Path("tools/repo_root.sh"),
        ):
            with self.subTest(script=str(script)):
                self.assertEqual(check_shell_scripts.check_script(script), [])

    def test_shell_libraries_are_valid(self) -> None:
        for script in check_shell_scripts.SHELL_LIBRARIES:
            with self.subTest(script=str(script)):
                self.assertEqual(check_shell_scripts.check_script(script), [])

    def test_sourced_shell_libraries_are_registered(self) -> None:
        missing = check_shell_scripts.unregistered_sourced_shell_libraries(
            check_shell_scripts.tracked_shell_scripts()
        )

        self.assertEqual(missing, set())

    def test_unregistered_sourced_shell_libraries_are_reported(self) -> None:
        original_repo_root = check_shell_scripts.REPO_ROOT
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tools = root / "tools"
            tools.mkdir()
            (tools / "wrapper.sh").write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        "set -euo pipefail",
                        'script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"',
                        '. "$script_dir/new_common.sh"',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (tools / "new_common.sh").write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        "set -euo pipefail",
                        "new_common() { :; }",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            check_shell_scripts.REPO_ROOT = root
            try:
                missing = check_shell_scripts.unregistered_sourced_shell_libraries(
                    [Path("tools/wrapper.sh"), Path("tools/new_common.sh")]
                )
            finally:
                check_shell_scripts.REPO_ROOT = original_repo_root

        self.assertEqual(missing, {Path("tools/new_common.sh")})

    def test_shell_library_registry_has_unique_paths(self) -> None:
        source = Path(check_shell_scripts.__file__).read_text(encoding="utf-8")
        module = ast.parse(source)
        library_paths: list[str] = []

        for node in module.body:
            if not isinstance(node, ast.Assign):
                continue
            if not any(
                isinstance(target, ast.Name) and target.id == "SHELL_LIBRARIES"
                for target in node.targets
            ):
                continue
            self.assertIsInstance(node.value, ast.Dict)
            for key in node.value.keys:
                if (
                    isinstance(key, ast.Call)
                    and isinstance(key.func, ast.Name)
                    and key.func.id == "Path"
                    and len(key.args) == 1
                    and isinstance(key.args[0], ast.Constant)
                    and isinstance(key.args[0].value, str)
                ):
                    library_paths.append(key.args[0].value)
            break
        else:
            self.fail("SHELL_LIBRARIES registry not found")

        duplicate_paths = sorted(
            path for path, count in Counter(library_paths).items() if count > 1
        )
        self.assertEqual(duplicate_paths, [])


if __name__ == "__main__":
    unittest.main()
