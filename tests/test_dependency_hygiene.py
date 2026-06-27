import json
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class DependencyHygieneTests(unittest.TestCase):
    def test_devcontainer_setup_uses_canonical_paths(self) -> None:
        devcontainer = json.loads(_read(".devcontainer/devcontainer.json"))
        vscode = devcontainer["customizations"]["vscode"]
        extensions = {extension.lower() for extension in vscode["extensions"]}
        payload = json.dumps(devcontainer)

        self.assertEqual(
            devcontainer["postCreateCommand"], "bash ./tools/setup_devcontainer.sh"
        )
        self.assertEqual(
            vscode["settings"]["python.defaultInterpreterPath"],
            "${containerWorkspaceFolder}/.venv/bin/python3",
        )
        self.assertEqual(vscode["settings"]["python.testing.pytestEnabled"], False)
        self.assertEqual(vscode["settings"]["python.testing.unittestEnabled"], True)
        self.assertEqual(
            vscode["settings"]["ruff.path"],
            ["${containerWorkspaceFolder}/.venv/bin/ruff"],
        )
        self.assertEqual(
            vscode["settings"]["mypy-type-checker.path"],
            ["${containerWorkspaceFolder}/.venv/bin/python", "-m", "mypy"],
        )
        self.assertEqual(
            vscode["settings"]["mypy-type-checker.args"],
            ["--config-file", "mypy.ini"],
        )
        self.assertIn(
            "**/apps/portfolio/node_modules/**",
            vscode["settings"]["python.analysis.exclude"],
        )
        self.assertIn(
            "**/docs/peanut/**",
            vscode["settings"]["markdownlint.ignore"],
        )
        self.assertNotIn("frontend/package.json", payload)
        self.assertNotIn("polinko-repositioning-system", payload)
        self.assertNotIn("vue.volar", extensions)
        self.assertNotIn("ms-python.isort", extensions)
        self.assertNotIn("ms-pyright.pyright", extensions)

    def test_devcontainer_setup_script_uses_locked_root_and_portfolio_deps(
        self,
    ) -> None:
        script = _read("tools/setup_devcontainer.sh")

        self.assertIn('source "$script_dir/repo_root.sh"', script)
        self.assertIn("polinko_cd_repo_root", script)
        self.assertIn('ROOT="$POLINKO_REPO_ROOT"', script)
        self.assertIn('venv_dir="${POLINKO_DEVCONTAINER_VENV_DIR:-.venv}"', script)
        self.assertIn(
            'bootstrap_python="${POLINKO_DEVCONTAINER_BOOTSTRAP_PYTHON:-python3.14}"',
            script,
        )
        self.assertIn('venv_python="$venv_dir/bin/python3"', script)
        self.assertIn('"$bootstrap_python" -m venv --copies "$venv_dir"', script)
        self.assertIn('"$venv_python" -m pip install --upgrade pip', script)
        self.assertIn('"$venv_python" -m pip install -r requirements.txt', script)
        self.assertIn("requirements.txt", script)
        self.assertIn("npm ci --no-audit --no-fund", script)
        self.assertIn(
            'portfolio_app_dir="${POLINKO_DEVCONTAINER_PORTFOLIO_APP_DIR:-apps/portfolio}"',
            script,
        )
        self.assertIn(
            'npm --prefix "$portfolio_app_dir" ci --no-audit --no-fund', script
        )
        self.assertNotIn("frontend", script)
        self.assertNotIn("polinko-repositioning-system", script)

    def test_devcontainer_setup_honors_configured_bootstrap_python(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            fake_bin = tmp / "bin"
            fake_bin.mkdir()
            fake_python = fake_bin / "bootstrap-python"
            fake_npm = fake_bin / "npm"
            bootstrap_log = tmp / "bootstrap-python.log"
            venv_python_log = tmp / "venv-python.log"
            npm_log = tmp / "npm.log"
            venv_dir = tmp / ".venv-devcontainer"

            fake_python.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env bash
                    set -euo pipefail
                    printf '%s\\n' "$*" >> "$BOOTSTRAP_PYTHON_LOG"
                    if [ "$1" = "-m" ] && [ "$2" = "venv" ]; then
                            venv_dir="${@: -1}"
                            mkdir -p "$venv_dir/bin"
                            cat > "$venv_dir/bin/python3" <<'PY'
                    #!/usr/bin/env bash
                    set -euo pipefail
                    printf '%s\\n' "$*" >> "$VENV_PYTHON_LOG"
                    PY
                            chmod +x "$venv_dir/bin/python3"
                    fi
                    """
                ),
                encoding="utf-8",
            )
            fake_python.chmod(0o755)
            fake_npm.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env bash
                    set -euo pipefail
                    printf '%s\\n' "$*" >> "$NPM_LOG"
                    """
                ),
                encoding="utf-8",
            )
            fake_npm.chmod(0o755)

            env = os.environ.copy()
            env.update(
                {
                    "BOOTSTRAP_PYTHON_LOG": str(bootstrap_log),
                    "NPM_LOG": str(npm_log),
                    "PATH": f"{fake_bin}{os.pathsep}{env['PATH']}",
                    "POLINKO_DEVCONTAINER_BOOTSTRAP_PYTHON": str(fake_python),
                    "POLINKO_DEVCONTAINER_PORTFOLIO_APP_DIR": "missing-portfolio",
                    "POLINKO_DEVCONTAINER_VENV_DIR": str(venv_dir),
                    "VENV_PYTHON_LOG": str(venv_python_log),
                }
            )

            result = subprocess.run(
                ["bash", "tools/setup_devcontainer.sh"],
                cwd=REPO_ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                bootstrap_log.read_text(encoding="utf-8").strip(),
                f"-m venv --copies {venv_dir}",
            )
            self.assertEqual(
                venv_python_log.read_text(encoding="utf-8").splitlines(),
                ["-m pip install --upgrade pip", "-m pip install -r requirements.txt"],
            )
            self.assertEqual(
                npm_log.read_text(encoding="utf-8").strip(), "ci --no-audit --no-fund"
            )
            self.assertIn("Skipping portfolio npm install", result.stdout)

    def test_python_lockfile_uses_dependabot_visible_pip_tools_convention(
        self,
    ) -> None:
        build_config = _read("makefiles/config/build.mk")
        workflow = _read(".github/workflows/ci.yml")
        requirements_input = _read("requirements.in")
        lockfile = _read("requirements.txt")

        self.assertIn("REQUIREMENTS_IN ?= requirements.in", build_config)
        self.assertIn("REQUIREMENTS_LOCK ?= requirements.txt", build_config)
        self.assertIn("pip install -r requirements.txt", workflow)
        self.assertNotIn("pip install --upgrade pip pip-audit", workflow)
        self.assertIn("--output-file=requirements.txt", lockfile)
        self.assertIn("httpx2==2.4.0", requirements_input)
        self.assertIn("httpx2==2.4.0", lockfile)
        self.assertIn("starlette==1.3.1", requirements_input)
        self.assertIn("starlette==1.3.1", lockfile)
        self.assertIn("pip-audit==2.10.0", requirements_input)
        self.assertIn("pip-audit==2.10.0", lockfile)
        self.assertIn("#   -r requirements.in", lockfile)
        self.assertFalse((REPO_ROOT / "requirements.lock").exists())

    def test_runtime_venv_candidates_exclude_retired_custom_name(self) -> None:
        main_text = _read("main.py")
        doctor_text = _read("tools/doctor_env.py")

        self.assertIn('_PROJECT_VENV_NAMES = (".venv", "venv")', main_text)
        self.assertIn('PREFERRED_VENV_NAMES = (".venv", "venv")', doctor_text)
        self.assertNotIn("polinko-repositioning-system", main_text)
        self.assertNotIn("polinko-repositioning-system", doctor_text)

    def test_node_security_covers_root_and_portfolio_locks(self) -> None:
        build_make = _read("makefiles/build.mk")
        dependabot = _read(".github/dependabot.yml")

        self.assertIn("npm audit --audit-level=moderate", build_make)
        self.assertIn(
            'npm --prefix "$(PORTFOLIO_APP_DIR)" audit --audit-level=moderate',
            build_make,
        )
        self.assertIn('directory: "/"', dependabot)
        self.assertIn('directory: "/apps/portfolio"', dependabot)

    def test_ci_automation_uses_read_only_contents_permissions(self) -> None:
        ci_workflow = _read(".github/workflows/ci.yml")
        dependency_review = _read(".github/workflows/dependency-review.yml")

        self.assertIn("permissions:\n  contents: read", ci_workflow)
        self.assertIn("permissions:\n  contents: read", dependency_review)

    def test_dependency_lock_and_check_use_same_resolver(self) -> None:
        build_make = _read("makefiles/build.mk")

        self.assertEqual(build_make.count("--resolver=backtracking"), 2)

    def test_precommit_uses_repo_owned_lightweight_style_and_doc_checks(self) -> None:
        precommit = _read(".pre-commit-config.yaml")

        self.assertIn("exclude: ^(docs/peanut/|public/portfolio/assets/)", precommit)
        self.assertIn("id: polinko-ruff-check", precommit)
        self.assertIn("entry: make ruff-check", precommit)
        self.assertIn("id: polinko-ruff-format-check", precommit)
        self.assertIn("entry: make ruff-format-check", precommit)
        self.assertIn("id: polinko-markdownlint-docs", precommit)
        self.assertIn("entry: make lint-docs", precommit)
        self.assertNotIn("isort", precommit)
        self.assertNotIn("black", precommit)

    def test_markdownlint_ignores_private_peanut_lane(self) -> None:
        markdownlint = _read(".markdownlint-cli2.yaml")

        self.assertIn('"docs/peanut/**/*.md"', markdownlint)
        self.assertNotIn("docs/peanut/transcripts/**/*.md", markdownlint)


if __name__ == "__main__":
    unittest.main()
