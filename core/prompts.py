"""Compatibility shim for ``polinko.core.prompts``."""

from importlib import import_module
import sys

_module = import_module("polinko.core.prompts")
sys.modules[__name__] = _module
