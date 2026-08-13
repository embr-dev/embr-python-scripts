"""Selection helpers for Embr Matte."""

from __future__ import annotations

from dataclasses import dataclass
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


def _unwrap(value: Any) -> Any:
    """Unwrap Flame get_value() wrappers (same pattern as Logik scripts)."""
    if value is None:
        return None
    try:
        return value.get_value()
    except AttributeError:
        return value
    except Exception:
        return value


def _as_int(value: Any) -> int:
    value = _unwrap(value)
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        pass
    text = str(value).strip().strip("'\"")
    if not text:
        return 0
    try:
        return int(float(text.split()[0]))
    except (TypeError, ValueError):
        return 0


def _as_float(value: Any) -> float:
    value = _unwrap(value)
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        pass
    text = str(value).strip().strip("'\"")
    if not text:
        return 0.0
    try:
        return float(text.split()[0])
    except (TypeError, ValueError):
        return 0.0


def _as_str(value: Any) -> str:
    value = _unwrap(value)
    if value is None:
        return ""
    return str(value).strip().strip("'\"")


@dataclass(frozen=True)
class ClipFormat:
    width: int = 0
    height: int = 0
    ratio: float = 0.0
    bit_depth: int = 0
    scan_mode: str = ""
    frame_rate: str = ""

    def label(self) -> str:
        parts: list[str] = []
        if self.width > 0 and self.height > 0:
            parts.append(f"{self.width}x{self.height}")
        if self.frame_rate:
            parts.append(self.frame_rate)
        if self.bit_depth > 0:
            parts.append(f"{self.bit_depth}-bit")
        return " · ".join(parts)


def _read_format_from(obj: Any) -> ClipFormat:
    width = _as_int(getattr(obj, "width", None))
    height = _as_int(getattr(obj, "height", None))
    ratio = _as_float(getattr(obj, "ratio", None))
    bit_depth = _as_int(getattr(obj, "bit_depth", None))
    scan_mode = _as_str(getattr(obj, "scan_mode", None))
    frame_rate = _as_str(getattr(obj, "frame_rate", None))
    if not frame_rate:
        start = getattr(obj, "start_time", None)
        if start is not None:
            frame_rate = _as_str(getattr(start, "frame_rate", None))
    if ratio <= 0.0 and width > 0 and height > 0:
        ratio = float(width) / float(height)
    return ClipFormat(
        width=width,
        height=height,
        ratio=ratio,
        bit_depth=bit_depth,
        scan_mode=scan_mode,
        frame_rate=frame_rate,
    )


def clip_format(clip: Any) -> ClipFormat:
    """Best-effort source format for later import reformat."""
    fmt = _read_format_from(clip)
    if fmt.width > 0 and fmt.height > 0:
        return fmt

    versions = getattr(clip, "versions", None) or []
    for version in versions:
        fmt = _read_format_from(version)
        if fmt.width > 0 and fmt.height > 0:
            return fmt
        tracks = getattr(version, "tracks", None) or []
        for track in tracks:
            segments = getattr(track, "segments", None) or []
            for segment in segments:
                fmt = _read_format_from(segment)
                if fmt.width > 0 and fmt.height > 0:
                    return fmt
    return fmt


def clip_resolution(clip: Any) -> tuple[int, int]:
    """Backward-compatible width/height accessor."""
    fmt = clip_format(clip)
    return fmt.width, fmt.height
