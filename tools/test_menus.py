#!/usr/bin/env python3
"""Offline tests for embr.menus defaults / prefs / action builders."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
EMBR = SCRIPTS / "embr"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(EMBR))


def main() -> None:
    import embr_menus as menus
    from embr import paths

    defaults = menus.load_defaults()
    assert "surfaces" in defaults
    main_ids = {e["id"]: e for e in defaults["surfaces"]["main_menu"]}
    assert main_ids["script_manager"].get("locked") is True
    assert main_ids["preferences"].get("locked") is True

    user_embr = paths.flame_user_embr_dir()
    assert user_embr.name == "embr"
    assert user_embr.parent.name == "flame"
    assert menus.prefs_path() == (user_embr / "prefs.json").resolve()

    with tempfile.TemporaryDirectory() as td:
        config_root = Path(td)

        order, visible = menus.resolve(
            "main_menu", "script_manager", config_root=config_root
        )
        assert visible is True
        assert order == 100

        order_pref, visible_pref = menus.resolve(
            "main_menu", "preferences", config_root=config_root
        )
        assert visible_pref is True
        assert order_pref == 200

        # Reorder is allowed; hide requests for locked ids are stripped.
        menus.set_surface_prefs(
            "main_menu",
            order=["preferences", "script_manager"],
            hidden=["script_manager", "preferences"],
            config_root=config_root,
        )
        prefs = menus.load_prefs(config_root)
        assert prefs["menus"]["main_menu"]["order"] == [
            "preferences",
            "script_manager",
        ]
        assert prefs["menus"]["main_menu"]["hidden"] == []

        entries = menus.effective_entries("main_menu", config_root=config_root)
        assert [e["id"] for e in entries] == ["preferences", "script_manager"]
        assert all(e["visible"] for e in entries)
        assert all(e["locked"] for e in entries)
        assert entries[0]["order"] == 100
        assert entries[1]["order"] == 200

        def _noop(_selection):
            return None

        shown_pref = menus.action(
            "main_menu",
            "preferences",
            execute=_noop,
            caption="Preferences",
            config_root=config_root,
        )
        shown_sm = menus.action(
            "main_menu",
            "script_manager",
            execute=_noop,
            caption="Manager",
            config_root=config_root,
        )
        assert shown_pref is not None and shown_sm is not None
        assert shown_pref["order"] == 100
        assert shown_sm["order"] == 200

        group = menus.group("main_menu", [shown_pref, shown_sm])
        assert len(group) == 1
        assert [a["name"] for a in group[0]["actions"]] == [
            "Preferences",
            "Manager",
        ]

        menus.reset_menu_prefs(config_root=config_root)
        restored = menus.effective_entries("main_menu", config_root=config_root)
        assert [e["id"] for e in restored] == ["script_manager", "preferences"]
        assert all(e["visible"] for e in restored)

        path = menus.prefs_path(config_root)
        assert path == (config_root / "prefs.json").resolve()
        assert path.is_file()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["menus"] == {}

    with tempfile.TemporaryDirectory() as td:
        config_root = Path(td)
        order, visible = menus.resolve(
            "timeline", "future_tool", config_root=config_root
        )
        assert visible is True
        assert order == 9000

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    pref_dir = SCRIPTS / "embr_preferences"
    sys.path.insert(0, str(pref_dir))
    import embr_pref_window

    with tempfile.TemporaryDirectory() as td:
        w = embr_pref_window.PreferencesWindow(config_root=Path(td))
        assert w._list.count() >= 2
        # Locked rows are checked and not user-checkable.
        for i in range(w._list.count()):
            item = w._list.item(i)
            assert item.checkState() == __import__(
                "PySide6.QtCore", fromlist=["Qt"]
            ).Qt.CheckState.Checked
            assert not (
                item.flags()
                & __import__("PySide6.QtCore", fromlist=["Qt"]).Qt.ItemFlag.ItemIsUserCheckable
            )
        w.close()

    print("ok")


if __name__ == "__main__":
    main()
