"""Python hook helpers."""

from __future__ import annotations

import sys
from typing import Iterable


def invalidate_imports(package_name: str = "embr") -> None:
    """Drop ``package_name`` modules from ``sys.modules`` so the next import reloads them.

    Flame's \"Rescan Python Hooks\" re-reads hook files, but already-imported
    packages (like ``embr``) can stay cached. Call this before ``refresh()``
    during development when util code changed.
    """
    prefix = package_name + "."
    for name in list(sys.modules):
        if name == package_name or name.startswith(prefix):
            del sys.modules[name]


def refresh(*, invalidate: Iterable[str] | None = ("embr",)) -> None:
    """Rescan Python hooks via Flame's ``Rescan Python Hooks`` shortcut.

    Parameters
    ----------
    invalidate:
        Package names to remove from ``sys.modules`` before rescanning.
        Pass ``None`` or an empty iterable to skip invalidation.
    """
    import flame

    if invalidate:
        for package_name in invalidate:
            invalidate_imports(package_name)

    flame.execute_shortcut("Rescan Python Hooks")
