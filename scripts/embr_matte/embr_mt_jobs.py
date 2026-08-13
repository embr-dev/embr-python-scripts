"""Job folder helpers for Embr Matte (Phase 0)."""

from __future__ import annotations

import json
import uuid
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
    source_width: int = 0
    source_height: int = 0
    source_ratio: float = 0.0
    source_bit_depth: int = 0
    source_scan_mode: str = ""
    source_frame_rate: str = ""
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
            "source_width": self.source_width,
            "source_height": self.source_height,
            "source_ratio": self.source_ratio,
            "source_bit_depth": self.source_bit_depth,
            "source_scan_mode": self.source_scan_mode,
            "source_frame_rate": self.source_frame_rate,
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
            source_width=int(data.get("source_width") or 0),
            source_height=int(data.get("source_height") or 0),
            source_ratio=float(data.get("source_ratio") or 0.0),
            source_bit_depth=int(data.get("source_bit_depth") or 0),
            source_scan_mode=str(data.get("source_scan_mode") or ""),
            source_frame_rate=str(data.get("source_frame_rate") or ""),
            created_at=str(data.get("created_at") or ""),
            message=str(data.get("message") or ""),
        )


def jobs_root(ml_root: Path | None = None) -> Path:
    import embr_runtime as runtime

    root = ml_root or runtime.embr_ml_root()
    path = root / "jobs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def new_job_id(*_args, **_kwargs) -> str:
    """Allocate a unique job id used as the job folder name.

    Extra args are ignored so a stale Matte window (pre-0.1.2) that still
    calls ``new_job_id(clip_name)`` keeps working until the singleton is
    closed and reopened.
    """
    return uuid.uuid4().hex[:12]


def create_job_dirs(job_id: str, ml_root: Path | None = None) -> Path:
    job = jobs_root(ml_root) / job_id
    # export/ holds Add PNG sequence and is also Phase-0 RGB input.
    # guide/_work/alpha/fgr reserved for later ML stages.
    for name in ("export", "guide", "_work", "alpha", "fgr"):
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


def delete_job(job: MatteJob, ml_root: Path | None = None) -> None:
    """Remove the job folder under ``jobs_root`` (and its status.json)."""
    import shutil

    root = jobs_root(ml_root).resolve()
    job_dir = Path(job.job_dir).expanduser().resolve()
    if job_dir.parent != root:
        raise ValueError(
            f"Refusing to delete job outside jobs root: {job_dir}"
        )
    if not job_dir.is_dir():
        return
    shutil.rmtree(job_dir)


def first_image(folder: Path) -> Path | None:
    frames = collect_images(folder)
    return frames[0] if frames else None


def collect_images(folder: Path) -> list[Path]:
    """Flat images first; fall back to nested export trees."""
    if not folder.is_dir():
        return []
    flat = sorted(
        p
        for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )
    if flat:
        return flat
    return sorted(
        p
        for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )
