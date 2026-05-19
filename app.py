"""Compatibility launcher for the Polinko CLI.

New code should call ``main.py`` or ``make chat``. This module remains for old
local scripts that still invoke ``python app.py``.
"""

from main import main

__all__ = ["main"]


if __name__ == "__main__":
    main()
