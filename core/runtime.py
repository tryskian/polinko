"""Compatibility shim for ``polinko.core.runtime``."""

from importlib import import_module
import sys

_module = import_module("polinko.core.runtime")
sys.modules[__name__] = _module
