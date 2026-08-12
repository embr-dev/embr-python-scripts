"""Install / update / uninstall / repair packages into the Embr install root."""

from __future__ import annotations

import hashlib
import shutil
import tempfile
from pathlib import Path

from embr_sm_catalog import (
    Catalog,
    PackageInfo,
    fetch_bytes,
    raw_file_url,
)
import embr_sm_local as local_mod


class ActionError(RuntimeError):
    """Raised when a package action fails."""


PROTECTED_FROM_UNINSTALL = frozenset({"embr", "embr_manager", "embr_preferences"})



def _dependents(catalog: Catalog, package_id: str, state: local_mod.LocalState) -> list[str]:
    """Return installed package ids that depend on ``package_id``."""
    found: list[str] = []
    for pkg in catalog.packages:
        if (
            pkg.id != package_id
            and package_id in pkg.depends
            and pkg.id in state.packages
        ):
            found.append(pkg.id)
    return found


def _download_package_tree(
    catalog: Catalog,
    package: PackageInfo,
    dest: Path,
) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for entry in package.files:
        rel = entry["path"]
        expected = entry.get("sha256", "")
        url = raw_file_url(catalog.repo, catalog.ref, f"{package.path}/{rel}")
        data = fetch_bytes(url)
        digest = hashlib.sha256(data).hexdigest()
        if expected and digest != expected:
            raise ActionError(
                f"Embr Script Manager: checksum mismatch for {package.id}/{rel} - "
                f"expected {expected[:12]}..., got {digest[:12]}.... "
                "Catalog and files are out of sync (often a brief GitHub CDN lag on "
                "the 'dev' channel). Wait a minute, Refresh, then try Update again."
            )
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def _atomic_replace(src_dir: Path, dest_dir: Path) -> None:
    parent = dest_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if dest_dir.exists():
        backup = Path(
            tempfile.mkdtemp(prefix=f".{dest_dir.name}_bak_", dir=str(parent))
        )
        # move existing aside
        dest_dir.rename(backup)
    try:
        shutil.move(str(src_dir), str(dest_dir))
    except Exception:
        if backup is not None and not dest_dir.exists():
            backup.rename(dest_dir)
        raise
    if backup is not None:
        shutil.rmtree(backup, ignore_errors=True)


def _copy_package_tree(source_pkg_dir: Path, dest: Path) -> None:
    if not source_pkg_dir.is_dir():
        raise ActionError(
            f"Embr Script Manager: local package source not found: {source_pkg_dir}"
        )
    dest.mkdir(parents=True, exist_ok=True)
    for path in sorted(source_pkg_dir.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.name.startswith("."):
            continue
        rel = path.relative_to(source_pkg_dir)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def install_package(
    catalog: Catalog,
    package_id: str,
    root: Path,
    *,
    force: bool = False,
    source_root: Path | None = None,
) -> None:
    """Install or overwrite a package (and dependencies) under ``root``.

    If ``source_root`` is set (directory containing ``embr/``, ``embr_*/``),
    files are copied locally instead of downloaded from GitHub.
    """
    package = catalog.by_id(package_id)
    if package is None:
        raise ActionError(
            f"Embr Script Manager: package '{package_id}' not found in catalog. "
            "Refresh the catalog and try again."
        )

    for dep in package.depends:
        dep_pkg = catalog.by_id(dep)
        if dep_pkg is None:
            raise ActionError(
                f"Embr Script Manager: dependency '{dep}' for '{package_id}' "
                "is missing from the catalog."
            )
        state = local_mod.load_state(root)
        status = local_mod.compare_package(
            package_id=dep,
            root=root,
            remote_version=dep_pkg.version,
            remote_digest=dep_pkg.digest,
            state=state,
        )
        if status != local_mod.STATUS_UP_TO_DATE or force:
            install_package(
                catalog, dep, root, force=force, source_root=source_root
            )

    staging_parent = root / ".embr" / "staging"
    staging_parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f"{package_id}_", dir=str(staging_parent)))
    try:
        if source_root is not None:
            _copy_package_tree(source_root / package_id, staging)
        else:
            _download_package_tree(catalog, package, staging)
        dest = local_mod.package_dir(root, package_id)
        _atomic_replace(staging, dest)
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)

    digest, _ = local_mod.compute_local_digest(local_mod.package_dir(root, package_id))
    state = local_mod.load_state(root)
    state.packages[package_id] = local_mod.InstalledPackage(
        version=package.version,
        digest=digest,
        installed_at=local_mod.utc_now_iso(),
    )
    local_mod.save_state(root, state)


def update_package(
    catalog: Catalog,
    package_id: str,
    root: Path,
    *,
    source_root: Path | None = None,
) -> None:
    install_package(catalog, package_id, root, force=True, source_root=source_root)


def repair_package(
    catalog: Catalog,
    package_id: str,
    root: Path,
    *,
    source_root: Path | None = None,
) -> None:
    update_package(catalog, package_id, root, source_root=source_root)


def uninstall_package(
    catalog: Catalog | None,
    package_id: str,
    root: Path,
) -> None:
    if package_id in PROTECTED_FROM_UNINSTALL:
        raise ActionError(
            f"Embr Script Manager: cannot uninstall '{package_id}' - "
            "core packages (Embr Core / Script Manager / Preferences) are protected. "
            "Remove them manually from the install root if you really need to."
        )
    state = local_mod.load_state(root)
    if catalog is not None:
        deps = _dependents(catalog, package_id, state)
        if deps:
            raise ActionError(
                f"Embr Script Manager: cannot uninstall '{package_id}' - "
                f"required by {', '.join(deps)}. Uninstall dependents first."
            )

    target = local_mod.package_dir(root, package_id)
    if target.is_dir():
        shutil.rmtree(target)
    if package_id in state.packages:
        del state.packages[package_id]
        local_mod.save_state(root, state)


def build_status_rows(catalog: Catalog, root: Path) -> list[dict[str, str]]:
    """Return rows for the manager table."""
    state = local_mod.load_state(root)
    remote_ids = {p.id for p in catalog.packages}
    local_ids = set(local_mod.list_local_package_ids(root)) | set(state.packages)
    all_ids = sorted(remote_ids | local_ids)

    rows: list[dict[str, str]] = []
    for pkg_id in all_ids:
        remote = catalog.by_id(pkg_id)
        recorded = state.packages.get(pkg_id)
        local_version = recorded.version if recorded else ""
        if not local_version and local_mod.package_dir(root, pkg_id).is_dir():
            local_version = "(present)"
        status = local_mod.compare_package(
            package_id=pkg_id,
            root=root,
            remote_version=remote.version if remote else None,
            remote_digest=remote.digest if remote else None,
            state=state,
        )
        rows.append(
            {
                "id": pkg_id,
                "name": remote.name if remote else pkg_id,
                "status": status,
                "local": local_version,
                "remote": remote.version if remote else "",
            }
        )
    return rows
