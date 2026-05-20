"""Compatibility shim for ``polinko.core.history_store``."""

from importlib import import_module
import sys

_module = import_module("polinko.core.history_store")
sys.modules[__name__] = _module
