"""Embr shared utilities for Autodesk Flame 2025.0+ scripts.

Import explicitly, e.g. ``from embr import log, version``.
Do not define Flame hook entry points in this package.

Under ``DL_PYTHON_HOOK_PATH``, Flame loads each ``.py`` by basename. Helper
files therefore use unique names (``embr_paths.py``, …). This ``__init__``
re-exports them. Avoid relative imports — Flame may execute this file without
package context.
"""

from __future__ import annotations

import sys
from pathlib import Path

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

import embr_hooks as hooks
import embr_log as log
import embr_menus as menus
import embr_names as names
import embr_paths as paths
import embr_runtime as runtime
import embr_ui as ui
import embr_version as version

__all__ = [
    "hooks",
    "log",
    "menus",
    "names",
    "paths",
    "runtime",
    "ui",
    "version",
]

__version__ = "0.2.26"
