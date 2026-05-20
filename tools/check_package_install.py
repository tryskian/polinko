"""Validate the editable package install without importing runtime modules."""

from __future__ import annotations

from importlib import metadata, resources
from importlib.util import find_spec

import polinko
from polinko.config import AppConfig, load_config


def main() -> None:
    installed_version = metadata.version("polinko")
    if installed_version != polinko.__version__:
        raise SystemExit(
            "polinko metadata version "
            f"{installed_version!r} does not match package version "
            f"{polinko.__version__!r}"
        )
    if not callable(load_config):
        raise SystemExit("polinko.config.load_config is not callable")
    if AppConfig.__name__ != "AppConfig":
        raise SystemExit("polinko.config.AppConfig is not importable")
    if find_spec("polinko.api.app_factory") is None:
        raise SystemExit("polinko.api.app_factory is not discoverable")
    if find_spec("polinko.core.runtime") is None:
        raise SystemExit("polinko.core.runtime is not discoverable")
    if not resources.files("polinko.api").joinpath("static/favicon.png").is_file():
        raise SystemExit("polinko.api static favicon is not packaged")


if __name__ == "__main__":
    main()
