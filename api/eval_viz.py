"""Compatibility shim for ``polinko.api.eval_viz``."""

from importlib import import_module
import sys

_module = import_module("polinko.api.eval_viz")
sys.modules[__name__] = _module
