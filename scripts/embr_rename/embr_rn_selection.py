"""Selection cache for Embr Rename — always use isVisible selection."""

from __future__ import annotations

from typing import Any

import embr_rn_tokens as tokens

# surface -> tuple of Flame objects from the last successful isVisible call.
_CACHED: dict[str, tuple[Any, ...]] = {}


def cache_selection(surface: str, selection: Any) -> bool:
    """Store selection for ``surface`` if it has renameable items.

    Returns True when the menu should be visible. Clears the cache for this
    surface when there is nothing renameable.
    """
    items = tuple(selection or ())
    renameable = tokens.renameable_items(items)
    if renameable:
        _CACHED[surface] = items
        return True
    _CACHED.pop(surface, None)
    return False


def get_cached_selection(surface: str) -> tuple[Any, ...]:
    """Return the selection cached by ``isVisible`` for ``surface``."""
    return _CACHED.get(surface, ())


def clear_cached_selection(surface: str | None = None) -> None:
    """Clear one surface cache, or all caches when ``surface`` is None."""
    if surface is None:
        _CACHED.clear()
    else:
        _CACHED.pop(surface, None)


def selection_summary(selection: tuple[Any, ...] | list[Any]) -> str:
    """Short English summary for the Rename window header."""
    renameable = tokens.renameable_items(selection)
    total = len(selection)
    n = len(renameable)
    type_counts: dict[str, int] = {}
    for item in renameable:
        label = type(item).__name__
        type_counts[label] = type_counts.get(label, 0) + 1
    parts = [f"{count} {name}" for name, count in sorted(type_counts.items())]
    detail = ", ".join(parts) if parts else "none"
    skipped = total - n
    if skipped:
        return f"{n} renameable ({detail}); {skipped} skipped"
    return f"{n} object{'s' if n != 1 else ''} ({detail})"
