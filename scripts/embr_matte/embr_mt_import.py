"""Import job frames back to the saved parent reel and cache media."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import embr_mt_jobs as jobs


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


def import_job_to_parent(job: jobs.MatteJob) -> list[Any]:
    """Import ``input/`` (Phase 0) into the parent recorded at Add time."""
    import flame

    destination = _find_destination(job)
    input_dir = Path(job.input_dir or (Path(job.job_dir) / "input"))
    frames = jobs.collect_images(input_dir)
    if not frames:
        raise MatteImportError(f"No frames to import under {input_dir}")

    # Folder import: Flame accepts a directory of media.
    imported = flame.import_clips(str(input_dir), destination)
    if imported is None:
        return []
    if not isinstance(imported, (list, tuple)):
        return [imported]
    return list(imported)


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
