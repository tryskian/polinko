from agents import Runner
from typing import cast

from api.app_factory import RuntimeDeps, create_app
from config import load_config


config = load_config(dotenv_path=".env")
app = create_app(config)


def get_runtime_deps() -> RuntimeDeps:
    return cast(RuntimeDeps, app.state.runtime_deps)


# Backward-compatible symbols used by tests/dev scripts.
runtime_deps = get_runtime_deps()
