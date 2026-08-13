"""Job folder helpers for Embr Matte (Phase 0)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".exr", ".tif", ".tiff"}


@dataclass
class MatteJob:
    id: str
    clip_name: str
    job_dir: str
    parent_name: str = ""
    parent_type: str = ""
    status: str = "ready"
    thumbnail: str = ""
    export_dir: str = ""
    input_dir: str = ""
    created_at: str = ""
    message: str = ""
    # Live Flame object — never serialize (asdict/deepcopy pickles and fails).
    parent_ref: Any = field(default=None, repr=False, compare=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "clip_name": self.clip_name,
            "job_dir": self.job_dir,
            "parent_name": self.parent_name,
            "parent_type": self.parent_type,
            "status": self.status,
            "thumbnail": self.thumbnail,
            "export_dir": self.export_dir,
            "input_dir": self.input_dir,
            "created_at": self.created_at,
            "message": self.message,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MatteJob:
        return cls(
            id=str(data.get("id") or ""),
            clip_name=str(data.get("clip_name") or ""),
            job_dir=str(data.get("job_dir") or ""),
            parent_name=str(data.get("parent_name") or ""),
            parent_type=str(data.get("parent_type") or ""),
            status=str(data.get("status") or "ready"),
            thumbnail=str(data.get("thumbnail") or ""),
            export_dir=str(data.get("export_dir") or ""),
            input_dir=str(data.get("input_dir") or ""),
            created_at=str(data.get("created_at") or ""),
            message=str(data.get("message") or ""),
        )


def jobs_root(ml_root: Path | None = None) -> Path:
    import embr_runtime as runtime

    root = ml_root or runtime.embr_ml_root()
    path = root / "jobs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _safe_name(text: str) -> str:
    cleaned = re.sub(r"[^\w.\-]+", "_", text.strip()) or "clip"
    return cleaned[:80]


def new_job_id(clip_name: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{_safe_name(clip_name)}_{stamp}"


def create_job_dirs(job_id: str, ml_root: Path | None = None) -> Path:
    job = jobs_root(ml_root) / job_id
    for name in ("export", "input", "guide", "_work", "alpha", "fgr"):
        (job / name).mkdir(parents=True, exist_ok=True)
    return job


def status_path(job_dir: Path) -> Path:
    return job_dir / "status.json"


def save_job(job: MatteJob) -> None:
    path = status_path(Path(job.job_dir))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(job.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_job(job_dir: Path) -> MatteJob | None:
    path = status_path(job_dir)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return MatteJob.from_dict(data)


def list_jobs(ml_root: Path | None = None) -> list[MatteJob]:
    root = jobs_root(ml_root)
    result: list[MatteJob] = []
    for child in sorted(root.iterdir(), reverse=True):
        if not child.is_dir():
            continue
        job = load_job(child)
        if job is not None:
            result.append(job)
    return result


def first_image(folder: Path) -> Path | None:
    if not folder.is_dir():
        return None
    files = sorted(
        p
        for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )
    return files[0] if files else None


def collect_images(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(
        p
        for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )


def normalize_export_to_input(export_dir: Path, input_dir: Path) -> Path | None:
    """Copy exported frames into ``input/`` as a flat sequence; return first frame."""
    import shutil

    frames = collect_images(export_dir)
    if not frames:
        for child in sorted(export_dir.rglob("*")):
            if child.is_file() and child.suffix.lower() in IMAGE_EXTS:
                frames.append(child)
        frames = sorted(frames)
    if not frames:
        return None

    input_dir.mkdir(parents=True, exist_ok=True)
    for old in collect_images(input_dir):
        old.unlink(missing_ok=True)

    for index, src in enumerate(frames, start=1):
        dest = input_dir / f"{index:06d}{src.suffix.lower()}"
        shutil.copy2(src, dest)
    return input_dir / f"{1:06d}{frames[0].suffix.lower()}"
