"""Validate the editable package install without importing runtime modules."""

from __future__ import annotations

from importlib import metadata, resources
from importlib.util import find_spec


EDITABLE_INSTALL_HINT = (
    "run `make package-install-check` or install the package editable with "
    "`python -m pip install --no-build-isolation --no-deps -e .`"
)


def require_importable_package(module_name: str = "polinko") -> None:
    if find_spec(module_name) is None:
        raise SystemExit(
            f"{module_name} package is not importable; {EDITABLE_INSTALL_HINT}"
        )


def main() -> None:
    require_importable_package()

    import polinko
    from polinko.config import AppConfig, load_config

    try:
        installed_version = metadata.version("polinko")
    except metadata.PackageNotFoundError as exc:
        raise SystemExit(
            f"polinko package metadata is not installed; {EDITABLE_INSTALL_HINT}"
        ) from exc

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
    if find_spec("polinko.cli") is None:
        raise SystemExit("polinko.cli is not discoverable")
    if find_spec("polinko.asgi") is None:
        raise SystemExit("polinko.asgi is not discoverable")
    if not resources.files("polinko.api").joinpath("static/favicon.png").is_file():
        raise SystemExit("polinko.api static favicon is not packaged")
    scripts = metadata.entry_points(group="console_scripts")
    if not any(
        entry_point.name == "polinko-chat" and entry_point.value == "polinko.cli:main"
        for entry_point in scripts
    ):
        raise SystemExit("polinko-chat console script is not installed")


if __name__ == "__main__":
    main()
