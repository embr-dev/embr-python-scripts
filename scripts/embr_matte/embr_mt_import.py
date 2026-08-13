"""Import job frames back to the saved parent reel and cache media."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import embr_mt_jobs as jobs

IMPORT_NAME_SUFFIX = "-ML-Matte"

# Official reformat resize_mode values (not "Fit").
_RESIZE_MODES = ("Fill", "Letterbox", "Crop Edges", "Centre/Crop")


class MatteImportError(RuntimeError):
    """Raised when import or cache fails."""


def _find_destination(job: jobs.MatteJob) -> Any:
    if job.parent_ref is not None:
        return job.parent_ref

    import flame

    name = (job.parent_name or "").strip()
    if not name:
        raise MatteImportError("No parent reel recorded for this job.")

    found = flame.find_by_name(name) or []
    if not found:
        raise MatteImportError(
            f"Parent “{name}” not found in the project. "
            "It may have been renamed or deleted."
        )

    wanted = (job.parent_type or "").strip()
    if wanted:
        for obj in found:
            if type(obj).__name__ == wanted:
                return obj
    return found[0]


def import_clip_name(job: jobs.MatteJob) -> str:
    base = (job.clip_name or job.id or "clip").strip() or "clip"
    return f"{base}{IMPORT_NAME_SUFFIX}"


def _set_clip_name(clip: Any, name: str) -> None:
    try:
        clip.name = name
        return
    except Exception:
        pass
    setter = getattr(clip, "name", None)
    if hasattr(setter, "set_value"):
        setter.set_value(name)


def _apply_source_format(clip: Any, job: jobs.MatteJob) -> None:
    """Match imported clip metadata to the source recorded at Add time."""
    width = int(job.source_width or 0)
    height = int(job.source_height or 0)
    if width <= 0 or height <= 0:
        raise MatteImportError(
            "Source resolution was not recorded for this job "
            f"(width={width}, height={height}). "
            "Close Matte, Update/Rescan, Add the clip again, then Import."
        )

    ratio = float(job.source_ratio or 0.0)
    if ratio <= 0.0:
        ratio = float(width) / float(height)

    kwargs: dict[str, Any] = {
        "width": width,
        "height": height,
        "ratio": ratio,
        "resize_mode": "Fill",
    }
    if job.source_bit_depth in (8, 10, 12, 16, 32):
        kwargs["bit_depth"] = int(job.source_bit_depth)
    scan = (job.source_scan_mode or "").strip()
    if scan in {"P", "F1", "F2"}:
        kwargs["scan_mode"] = scan
    rate = (job.source_frame_rate or "").strip()
    if rate:
        kwargs["frame_rate"] = rate

    last_error: Exception | None = None
    # Try Fill first, then other official modes if Flame rejects one.
    for mode in _RESIZE_MODES:
        attempt = dict(kwargs)
        attempt["resize_mode"] = mode
        try:
            clip.reformat(**attempt)
            return
        except Exception as exc:
            last_error = exc

    # Last resort: width/height only.
    try:
        clip.reformat(width=width, height=height, ratio=ratio)
        return
    except Exception as exc:
        last_error = exc

    raise MatteImportError(
        "reformat failed while matching source format "
        f"({width}x{height}, {rate or 'fps?'}, "
        f"{job.source_bit_depth or '?'}bit): {last_error}"
    )


def import_job_to_parent(job: jobs.MatteJob) -> list[Any]:
    """Import export/ RGB sequence into the parent recorded at Add time."""
    import flame

    destination = _find_destination(job)
    media_dir = Path(
        job.input_dir
        or job.export_dir
        or (Path(job.job_dir) / "export")
    )
    frames = jobs.collect_images(media_dir)
    if not frames:
        raise MatteImportError(f"No frames to import under {media_dir}")

    imported = flame.import_clips(str(media_dir), destination)
    if imported is None:
        clips: list[Any] = []
    elif not isinstance(imported, (list, tuple)):
        clips = [imported]
    else:
        clips = list(imported)

    target_name = import_clip_name(job)
    for clip in clips:
        _set_clip_name(clip, target_name)
        _apply_source_format(clip, job)
    return clips


def cache_imported(clips: list[Any]) -> None:
    for clip in clips:
        cache = getattr(clip, "cache_media", None)
        if not callable(cache):
            continue
        try:
            cache("current")
        except TypeError:
            try:
                cache()
            except Exception:
                pass
        except Exception:
            pass
