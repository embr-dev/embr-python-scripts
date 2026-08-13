"""Export selected clips with the bundled Embr PNG preset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

PRESET_NAME = "Embr.xml"


class MatteExportError(RuntimeError):
    """Raised when PyExporter fails or produces no frames."""


def preset_path() -> Path:
    return Path(__file__).resolve().parent / "presets" / PRESET_NAME


def export_clip_to_job(clip: Any, export_dir: Path) -> None:
    """Foreground-export ``clip`` into ``export_dir`` using Embr.xml.

    Preset uses ``startFrame=1`` (6-digit padding). Prefer 1 over 0 so
    sequences match Flame/timecode-style numbering and MatAnyone prepare
    (1-based ``000001`` …).
    """
    import flame

    preset = preset_path()
    if not preset.is_file():
        raise MatteExportError(f"Export preset missing: {preset}")

    export_dir.mkdir(parents=True, exist_ok=True)
    exporter = flame.PyExporter()
    exporter.foreground = True
    # Match common script practice; marks optional for full clip.
    try:
        exporter.export_between_marks = False
    except Exception:
        pass
    try:
        exporter.use_top_video_track = True
    except Exception:
        pass

    exporter.export([clip], str(preset), str(export_dir))
