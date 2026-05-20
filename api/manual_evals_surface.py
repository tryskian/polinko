"""Compatibility shim for ``polinko.api.manual_evals_surface``."""

from importlib import import_module
import sys

_module = import_module("polinko.api.manual_evals_surface")
sys.modules[__name__] = _module
