"""Compatibility shim for ``polinko.core.vector_store``."""

from importlib import import_module
import sys

_module = import_module("polinko.core.vector_store")
sys.modules[__name__] = _module
