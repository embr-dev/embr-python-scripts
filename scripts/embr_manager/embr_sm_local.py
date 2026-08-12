"""Local install root state, digests, and package scanning."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from embr_sm_catalog import DEFAULT_CHANNEL

STATE_DIR_NAME = ".embr"
STATE_FILE_NAME = "state.json"


@dataclass
class InstalledPackage:
    version: str
    digest: str
    installed_at: str


@dataclass
class LocalState:
    install_root: str
    packages: dict[str, InstalledPackage]
    channel: str = DEFAULT_CHANNEL

    def to_dict(self) -> dict[str, Any]:
        return {
            "install_root": self.install_root,
            "channel": self.channel,
            "packages": {
                pkg_id: {
                    "version": info.version,
                    "digest": info.digest,
                    "installed_at": info.installed_at,
                }
                for pkg_id, info in sorted(self.packages.items())
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LocalState:
        packages: dict[str, InstalledPackage] = {}
        for pkg_id, info in (data.get("packages") or {}).items():
            packages[str(pkg_id)] = InstalledPackage(
                version=str(info.get("version", "")),
                digest=str(info.get("digest", "")),
                installed_at=str(info.get("installed_at", "")),
            )
        channel = str(data.get("channel") or DEFAULT_CHANNEL).strip().lower()
        return cls(
            install_root=str(data.get("install_root", "")),
            packages=packages,
            channel=channel or DEFAULT_CHANNEL,
        )


def state_path(root: Path) -> Path:
    return root / STATE_DIR_NAME / STATE_FILE_NAME


def load_state(root: Path) -> LocalState:
    path = state_path(root)
    if not path.is_file():
        return LocalState(
            install_root=str(root.resolve()),
            packages={},
            channel=DEFAULT_CHANNEL,
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    state = LocalState.from_dict(data)
    if not state.install_root:
        state.install_root = str(root.resolve())
    if not state.channel:
        state.channel = DEFAULT_CHANNEL
    return state


def save_state(root: Path, state: LocalState) -> None:
    path = state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    state.install_root = str(root.resolve())
    path.write_text(json.dumps(state.to_dict(), indent=2) + "\n", encoding="utf-8")


def get_channel(root: Path) -> str:
    return load_state(root).channel or DEFAULT_CHANNEL


def set_channel(root: Path, channel: str) -> LocalState:
    state = load_state(root)
    state.channel = channel
    save_state(root, state)
    return state


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def package_digest_from_files(files: list[dict[str, str]]) -> str:
    lines = [
        f"{entry['path']}:{entry['sha256']}"
        for entry in sorted(files, key=lambda e: e["path"])
    ]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def compute_local_digest(package_dir: Path) -> tuple[str, list[dict[str, str]]]:
    """Return digest and file list for an on-disk package directory."""
    files: list[dict[str, str]] = []
    if not package_dir.is_dir():
        return "", files
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        rel = path.relative_to(package_dir).as_posix()
        files.append({"path": rel, "sha256": sha256_file(path)})
    return package_digest_from_files(files), files


def package_dir(root: Path, package_id: str) -> Path:
    return root / package_id


def list_local_package_ids(root: Path) -> list[str]:
    ids: list[str] = []
    for path in sorted(root.iterdir()):
        if not path.is_dir():
            continue
        name = path.name
        if name.startswith("."):
            continue
        if name == "embr" or name.startswith("embr_"):
            ids.append(name)
    return ids


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# Status labels used by the manager UI / actions.
STATUS_NOT_INSTALLED = "Not installed"
STATUS_UP_TO_DATE = "Up to date"
STATUS_UPDATE_AVAILABLE = "Update available"
STATUS_CORRUPTED = "Corrupted"
STATUS_LOCAL_ONLY = "Local only"


def compare_package(
    *,
    package_id: str,
    root: Path,
    remote_version: str | None,
    remote_digest: str | None,
    state: LocalState,
) -> str:
    """Classify a package relative to catalog + disk + state."""
    disk = package_dir(root, package_id)
    on_disk = disk.is_dir()
    local_digest, _ = compute_local_digest(disk) if on_disk else ("", [])
    recorded = state.packages.get(package_id)

    if remote_version is None:
        return STATUS_LOCAL_ONLY if on_disk else STATUS_NOT_INSTALLED

    if not on_disk:
        return STATUS_NOT_INSTALLED

    if remote_digest and local_digest and local_digest != remote_digest:
        # Same version but files differ, or any digest mismatch → repair
        if recorded and recorded.version == remote_version:
            return STATUS_CORRUPTED
        # Could also be an older/newer tree; prefer update if versions differ
        if recorded and recorded.version != remote_version:
            return STATUS_UPDATE_AVAILABLE
        return STATUS_CORRUPTED

    if recorded and recorded.version != remote_version:
        return STATUS_UPDATE_AVAILABLE

    if recorded is None and remote_version:
        # Installed files match digest but no state — treat as up to date if digest matches
        if remote_digest and local_digest == remote_digest:
            return STATUS_UP_TO_DATE
        return STATUS_CORRUPTED

    return STATUS_UP_TO_DATE
