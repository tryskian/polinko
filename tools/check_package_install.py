"""Validate the editable package install without importing runtime modules."""

from __future__ import annotations

from importlib import metadata

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


if __name__ == "__main__":
    main()
