"""Compatibility shim for ``polinko.api.portfolio_sankey``."""

from importlib import import_module
import sys

_module = import_module("polinko.api.portfolio_sankey")
sys.modules[__name__] = _module
