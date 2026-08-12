"""Python hook helpers."""

from __future__ import annotations

import sys
from typing import Iterable


def invalidate_imports(package_name: str = "embr") -> None:
    """Drop ``package_name`` modules from ``sys.modules`` (dev escape hatch).

    Prefer Flame's own Rescan reload for ``embr_*.py`` basename modules. Deleting
    those names and then calling Rescan makes Flame ``importlib.reload`` stale
    module objects and spams:

    ``ImportError: module 'embr_hooks' not in sys.modules``

    Use this only when you must force-drop a *package* import that Flame does
    not reload (rare). Do not pair broad basename deletes with ``refresh()``.
    """
    prefix = package_name + "."
    for name in list(sys.modules):
        if name == package_name or name.startswith(prefix):
            del sys.modules[name]


def refresh(*, invalidate: Iterable[str] | None = None) -> None:
    """Rescan Python hooks via Flame's ``Rescan Python Hooks`` shortcut.

    Flame reloads previously loaded hook modules from disk (``Reloading '…'``).
    That is enough after Install / Update / Preferences Apply.

    Parameters
    ----------
    invalidate:
        Optional package names to remove from ``sys.modules`` *before* Rescan.
        Default ``None`` (recommended). Passing basename-style helpers
        (``embr_hooks``, …) or wiping them elsewhere causes reload errors.
    """
    import flame

    if invalidate:
        for package_name in invalidate:
            invalidate_imports(package_name)

    flame.execute_shortcut("Rescan Python Hooks")
