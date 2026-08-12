#!/usr/bin/env python3
"""Offline tests for Script Manager core (catalog / local / actions / bootstrap / ui)."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
MANAGER = SCRIPTS / "embr_manager"
EMBR = SCRIPTS / "embr"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(EMBR))
sys.path.insert(0, str(MANAGER))


def main() -> None:
    from embr_sm_catalog import CatalogError, load_catalog_from_path, parse_catalog
    import embr_sm_actions as actions
    import embr_sm_bootstrap as bootstrap
    import embr_sm_local as local
    from embr import paths, ui as embr_ui

    cat = load_catalog_from_path(str(ROOT / "catalog" / "catalog.json"))
    assert cat.by_id("embr") and cat.by_id("embr_manager")

    try:
        parse_catalog({})
        raise AssertionError("expected CatalogError")
    except CatalogError:
        pass

    assert paths.flame_user_python().name == "python"
    assert paths.flame_shared_python() == Path("/opt/Autodesk/shared/python")

    source = SCRIPTS
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        actions.install_package(cat, "embr", td_path, source_root=source)
        actions.install_package(cat, "embr_manager", td_path, source_root=source)
        rows = {r["id"]: r["status"] for r in actions.build_status_rows(cat, td_path)}
        assert rows["embr"] == local.STATUS_UP_TO_DATE
        assert rows["embr_manager"] == local.STATUS_UP_TO_DATE

        log_py = td_path / "embr" / "embr_log.py"
        log_py.write_text(log_py.read_text(encoding="utf-8") + "\n# x\n", encoding="utf-8")
        rows = {r["id"]: r["status"] for r in actions.build_status_rows(cat, td_path)}
        assert rows["embr"] == local.STATUS_CORRUPTED
        actions.repair_package(cat, "embr", td_path, source_root=source)
        rows = {r["id"]: r["status"] for r in actions.build_status_rows(cat, td_path)}
        assert rows["embr"] == local.STATUS_UP_TO_DATE

        try:
            actions.uninstall_package(cat, "embr", td_path)
            raise AssertionError("expected protected uninstall to fail")
        except actions.ActionError:
            pass
        try:
            actions.uninstall_package(cat, "embr_manager", td_path)
            raise AssertionError("expected protected uninstall to fail")
        except actions.ActionError:
            pass
        shutil.rmtree(td_path / "embr_manager")
        shutil.rmtree(td_path / "embr")
        assert not (td_path / "embr").exists()

    with tempfile.TemporaryDirectory() as td:
        vendor = Path(td) / "Embr"
        bootstrap.bootstrap_into(
            vendor, catalog=cat, source_root=source, channel="dev"
        )
        assert (vendor / "embr").is_dir()
        assert (vendor / "embr_manager").is_dir()
        assert (vendor / "embr_preferences").is_dir()
        assert local.get_channel(vendor) == "dev"
        assert paths.vendor_install_root(Path(td)).name == "Embr"

    from embr_sm_catalog import CHANNELS, ref_for_channel

    assert ref_for_channel("dev") == "dev"
    assert ref_for_channel("latest") == "main"
    assert set(CHANNELS) >= {"stable", "latest", "dev"}

    from embr_sm_catalog import resolve_ref_sha

    assert resolve_ref_sha("x/y", "a" * 40) == "a" * 40

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    embr_ui._FONT_LOADED = False
    font = embr_ui.embr_font(12)
    assert font.family()
    pix = embr_ui.logo_pixmap("embr-mark.svg", 32)
    assert not pix.isNull()

    import embr_sm_window

    w = embr_sm_window.ScriptManagerWindow(
        root=SCRIPTS,
        catalog_path=ROOT / "catalog" / "catalog.json",
        source_root=SCRIPTS,
    )
    assert w._table.rowCount() >= 2
    print("ALL PASSED")


if __name__ == "__main__":
    main()
