"""Compatibility shim for ``polinko.core.rate_limit``."""

from importlib import import_module
import sys

_module = import_module("polinko.core.rate_limit")
sys.modules[__name__] = _module
