"""Compatibility shim for ``uvicorn server:app``.

The packaged ASGI app lives in ``polinko.asgi``. This module forwards module
identity so older tests, scripts, and local server commands keep working.
"""

from importlib import import_module
import sys

_module = import_module("polinko.asgi")
sys.modules[__name__] = _module
