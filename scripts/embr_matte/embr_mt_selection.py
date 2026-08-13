"""Selection helpers for Embr Matte."""

from __future__ import annotations

from typing import Any


def _clip_name(obj: Any) -> str:
    name = getattr(obj, "name", None)
    if name is None:
        return type(obj).__name__
    if hasattr(name, "get_value"):
        try:
            return str(name.get_value())
        except Exception:
            pass
    text = str(name).strip().strip("'\"")
    return text or type(obj).__name__


def is_clip(obj: Any) -> bool:
    return type(obj).__name__ in {"PyClip", "PySequence"}


def resolve_parent(obj: Any) -> Any | None:
    """Return Media Panel container suitable for ``import_clips`` destination."""
    parent = getattr(obj, "parent", None)
    if parent is None:
        return None
    # Prefer immediate parent (reel / folder / library).
    return parent


def iter_selected_clips() -> list[Any]:
    """Clips from Media Panel selection (live)."""
    import flame

    entries = []
    try:
        selected = flame.media_panel.selected_entries
        if selected:
            entries = list(selected)
    except Exception:
        entries = []

    clips: list[Any] = []
    for item in entries:
        if is_clip(item):
            clips.append(item)
    return clips


def clip_label(obj: Any) -> str:
    return _clip_name(obj)


def parent_label(parent: Any | None) -> tuple[str, str]:
    if parent is None:
        return "", ""
    return _clip_name(parent), type(parent).__name__


def _as_int(value: Any) -> int:
    if value is None:
        return 0
    if hasattr(value, "get_value"):
        try:
            value = value.get_value()
        except Exception:
            return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def clip_resolution(clip: Any) -> tuple[int, int]:
    """Best-effort source width/height for later import reformat."""
    width = _as_int(getattr(clip, "width", None))
    height = _as_int(getattr(clip, "height", None))
    if width > 0 and height > 0:
        return width, height

    versions = getattr(clip, "versions", None) or []
    for version in versions:
        width = _as_int(getattr(version, "width", None))
        height = _as_int(getattr(version, "height", None))
        if width > 0 and height > 0:
            return width, height
    return 0, 0
