"""Validate the editable package install without importing runtime modules."""

from __future__ import annotations

from importlib import metadata

import polinko


def main() -> None:
    installed_version = metadata.version("polinko")
    if installed_version != polinko.__version__:
        raise SystemExit(
            "polinko metadata version "
            f"{installed_version!r} does not match package version "
            f"{polinko.__version__!r}"
        )


if __name__ == "__main__":
    main()
