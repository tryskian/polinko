"""Compatibility shim for legacy ``python app.py`` CLI launches.

New code should call ``main.py`` or ``make chat``. This module stays lazy so
importing ``app`` does not load the full CLI runtime.
"""

__all__ = ["main"]


def main() -> None:
    from main import main as run_main

    run_main()


if __name__ == "__main__":
    main()
