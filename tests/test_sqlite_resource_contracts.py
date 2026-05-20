import ast
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _is_sqlite_connect_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "connect"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "sqlite3"
    )


class SqliteResourceContractTests(unittest.TestCase):
    def test_sqlite_connections_are_not_used_as_context_managers(self) -> None:
        tracked_python = subprocess.check_output(
            ["git", "ls-files", "src/**/*.py", "tools/**/*.py", "tests/**/*.py"],
            cwd=REPO_ROOT,
            text=True,
        ).splitlines()
        violations = []

        for relative_path in tracked_python:
            tree = ast.parse(
                (REPO_ROOT / relative_path).read_text(encoding="utf-8"),
                filename=relative_path,
            )
            for node in ast.walk(tree):
                if not isinstance(node, ast.With):
                    continue
                for item in node.items:
                    if _is_sqlite_connect_call(item.context_expr):
                        violations.append(f"{relative_path}:{node.lineno}")

        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
