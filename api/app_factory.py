"""Compatibility shim for ``polinko.api.app_factory``."""

from importlib import import_module
import sys

_module = import_module("polinko.api.app_factory")
sys.modules[__name__] = _module
