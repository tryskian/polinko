"""Packaged ASGI app entrypoint for Polinko."""

from typing import cast

from agents import Runner
from fastapi import FastAPI

from polinko.api.app_factory import RuntimeDeps, create_app
from polinko.config import AppConfig, load_config

__all__ = [
    "Runner",
    "RuntimeDeps",
    "app",
    "config",
    "create_asgi_app",
    "get_runtime_deps",
    "runtime_deps",
]


def create_asgi_app(config: AppConfig | None = None) -> FastAPI:
    resolved_config = config if config is not None else load_config(dotenv_path=".env")
    return create_app(resolved_config)


config = load_config(dotenv_path=".env")
app = create_asgi_app(config)


def get_runtime_deps() -> RuntimeDeps:
    return cast(RuntimeDeps, app.state.runtime_deps)


# Backward-compatible symbol used by tests/dev scripts through root server.py.
runtime_deps = get_runtime_deps()
