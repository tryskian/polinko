"""Compatibility shim for ``polinko.core.responses_parse``."""

from importlib import import_module
import sys

_module = import_module("polinko.core.responses_parse")
sys.modules[__name__] = _module
