"""Bootstrap Embr into User or Shared Flame python directories."""

from __future__ import annotations

from pathlib import Path

import embr_paths as paths
import embr_sm_actions as actions
import embr_sm_local as local
from embr_sm_catalog import (
    DEFAULT_CHANNEL,
    Catalog,
    fetch_catalog_for_channel,
    normalize_channel,
)


class BootstrapError(RuntimeError):
    """Raised when bootstrap fails."""


BOOTSTRAP_PACKAGES = ("embr", "embr_manager")


def candidate_roots() -> list[tuple[str, Path]]:
    """Return (label, Embr install root) under User / Shared python."""
    return [
        ("User python", paths.vendor_install_root(paths.flame_user_python())),
        ("Shared python", paths.vendor_install_root(paths.flame_shared_python())),
    ]


def is_bootstrapped(root: Path | None = None) -> bool:
    """Return True if Embr Core is present at ``root`` (or this package tree)."""
    if root is None:
        try:
            return (paths.package_dir() / "__init__.py").is_file()
        except Exception:
            return False
    return (root / "embr" / "__init__.py").is_file()


def bootstrap_into(
    target: Path,
    *,
    catalog: Catalog | None = None,
    source_root: Path | None = None,
    channel: str | None = None,
) -> Path:
    """Install embr + embr_manager into ``target`` (usually ``…/python/Embr``)."""
    try:
        # ``target`` is the Embr vendor root; ensure parent hooks dir + Embr.
        if target.name == paths.VENDOR_DIR_NAME:
            paths.ensure_vendor_install_root(target.parent)
        else:
            paths.ensure_writable(target)
    except paths.PathError as exc:
        raise BootstrapError(str(exc)) from exc

    chosen = normalize_channel(channel) if channel else DEFAULT_CHANNEL
    cat = catalog or fetch_catalog_for_channel(chosen)
    for pkg_id in BOOTSTRAP_PACKAGES:
        if cat.by_id(pkg_id) is None:
            raise BootstrapError(
                f"Embr Script Manager: bootstrap package '{pkg_id}' missing from catalog. "
                "Check catalog/catalog.json on the selected channel."
            )
    for pkg_id in BOOTSTRAP_PACKAGES:
        actions.install_package(
            cat, pkg_id, target, force=True, source_root=source_root
        )
    state = local.load_state(target)
    state.channel = chosen
    local.save_state(target, state)
    return target


def prompt_bootstrap_choice_qt() -> Path | None:
    """Show a Qt dialog to choose User vs Shared. Return Embr install path or None."""
    from PySide6.QtWidgets import QInputDialog, QMessageBox, QWidget

    labels = [label for label, _ in candidate_roots()]
    parent = QWidget()
    choice, ok = QInputDialog.getItem(
        parent,
        "Embr Setup",
        "Choose where to install Embr "
        f"(packages go under …/python/{paths.VENDOR_DIR_NAME}/):",
        labels,
        0,
        False,
    )
    if not ok:
        return None
    for label, path in candidate_roots():
        if label == choice:
            try:
                if path.name == paths.VENDOR_DIR_NAME:
                    paths.ensure_vendor_install_root(path.parent)
                else:
                    paths.ensure_writable(path)
            except paths.PathError as exc:
                QMessageBox.critical(parent, "Embr Setup", str(exc))
                return None
            return path
    return None
