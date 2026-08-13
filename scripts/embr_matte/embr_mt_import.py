"""Import job frames back to the saved parent reel and cache media."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import embr_mt_jobs as jobs

IMPORT_NAME_SUFFIX = "-ML-Matte"


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


def _apply_source_resolution(clip: Any, width: int, height: int) -> None:
    if width <= 0 or height <= 0:
        return
    ratio = float(width) / float(height) if height else 0.0
    try:
        clip.reformat(
            width=width,
            height=height,
            ratio=ratio,
            resize_mode="Fit",
        )
        return
    except TypeError:
        pass
    except Exception:
        pass
    try:
        clip.reformat(width=width, height=height)
    except Exception:
        pass


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
        _apply_source_resolution(clip, job.source_width, job.source_height)
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
