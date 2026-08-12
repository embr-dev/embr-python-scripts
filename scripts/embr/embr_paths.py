"""Filesystem and Flame Python environment paths."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))


class PathError(RuntimeError):
    """Raised when an Embr path cannot be resolved or written."""


# Vendor folder under Flame user/shared python (distribution layout).
VENDOR_DIR_NAME = "Embr"


def package_dir() -> Path:
    """Return the directory of the ``embr`` package."""
    return Path(__file__).resolve().parent


def scripts_root() -> Path:
    """Return the directory that contains ``embr/``.

    In the git repo this is ``scripts/``. After distribution install it is
    ``…/python/Embr`` (same role as install root).
    """
    return package_dir().parent


def install_root() -> Path:
    """Return the Embr install root (parent of ``embr/`` and ``embr_*/``)."""
    return scripts_root()


def flame_user_python() -> Path:
    """Return the Flame per-user python hooks directory (macOS or Linux)."""
    if sys.platform == "darwin":
        return (
            Path.home()
            / "Library"
            / "Preferences"
            / "Autodesk"
            / "flame"
            / "python"
        )
    return Path.home() / "flame" / "python"


def flame_shared_python() -> Path:
    """Return the studio shared Flame python hooks directory."""
    return Path("/opt/Autodesk/shared/python")


def vendor_install_root(hooks_python: str | Path) -> Path:
    """Return ``<hooks_python>/Embr`` — distribution install root."""
    return Path(hooks_python) / VENDOR_DIR_NAME


def ensure_vendor_install_root(hooks_python: str | Path) -> Path:
    """Create ``<hooks_python>/Embr`` if needed and ensure it is writable."""
    hooks = Path(hooks_python)
    ensure_writable(hooks)
    return ensure_writable(vendor_install_root(hooks))


def ensure_writable(path: str | Path) -> Path:
    """Ensure ``path`` exists and is writable; raise ``PathError`` if not."""
    target = Path(path)
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise PathError(
            f"Embr: cannot create directory {target} - {exc}. "
            "Choose User python, or ask an admin to grant write access."
        ) from exc

    probe = target / ".embr_write_probe"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        raise PathError(
            f"Embr: cannot write to {target} - {exc}. "
            "Choose User python, or ask an admin to grant write access."
        ) from exc
    return target


def flame_python_home() -> Path:
    """Return ``/opt/Autodesk/python/<version>`` for the running Flame."""
    import embr_version

    base = Path("/opt/Autodesk/python")
    text = embr_version.get_version().split(".pr", 1)[0]
    tokens = [t for t in text.split(".") if t]

    for length in range(len(tokens), 0, -1):
        candidate = base / ".".join(tokens[:length])
        if candidate.is_dir():
            return candidate

    raise FileNotFoundError(
        f"No Flame python home under {base} for version {text!r}"
    )


def flame_site_packages() -> Path:
    """Return Flame's ``site-packages`` directory."""
    home = flame_python_home()
    lib = home / "lib"
    if not lib.is_dir():
        raise FileNotFoundError(f"No lib directory under {home}")

    py_dirs = sorted(lib.glob("python3.*"), reverse=True)
    for py_dir in py_dirs:
        site = py_dir / "site-packages"
        if site.is_dir():
            return site

    raise FileNotFoundError(f"No site-packages under {lib}")


def ensure_dir(path: str | Path) -> Path:
    """Create ``path`` if needed and return it as ``Path``."""
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def make_temp_dir(parent: str | Path | None = None, name: str = "embr_temp") -> Path:
    """Create (or recreate) a temp folder under ``parent`` (default: scripts root)."""
    root = Path(parent) if parent is not None else scripts_root()
    target = root / name
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    return target


def cleanup_dir(path: str | Path, *, missing_ok: bool = True) -> None:
    """Remove a directory tree."""
    target = Path(path)
    if not target.exists():
        if missing_ok:
            return
        raise FileNotFoundError(target)
    shutil.rmtree(target)


def is_hook_path_configured() -> bool:
    """Return True if this ``scripts`` root appears related to the running env.

    Heuristic: ``scripts_root`` exists and is on ``sys.path`` or equals
    ``DL_PYTHON_HOOK_PATH`` (first entry).
    """
    root = scripts_root().resolve()
    path_entries = [Path(p).resolve() for p in sys.path if p]
    if root in path_entries:
        return True

    hook_path = os.environ.get("DL_PYTHON_HOOK_PATH", "")
    for entry in hook_path.split(":"):
        if entry and Path(entry).resolve() == root:
            return True
    return False


def describe_install_root(root: str | Path | None = None) -> str:
    """Return ``User (path)`` / ``Shared (path)`` / bare path."""
    path = Path(root).resolve() if root is not None else install_root().resolve()
    try:
        user = flame_user_python().resolve()
        if path == user or path == (user / VENDOR_DIR_NAME):
            return f"User ({path})"
    except OSError:
        pass
    try:
        shared = flame_shared_python().resolve()
        if path == shared or path == (shared / VENDOR_DIR_NAME):
            return f"Shared ({path})"
    except OSError:
        pass
    return str(path)
