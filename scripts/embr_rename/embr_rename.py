################################################################################
# Embr Rename
#
# Context menus: Embr / Rename (Timeline, Media Panel, Batch)
#
# Selection always comes from isVisible (cached per surface). execute() ignores
# its selection argument.
################################################################################

from __future__ import annotations

import sys
from pathlib import Path

__version__ = "0.1.0"

_DIR = Path(__file__).resolve().parent
_SCRIPTS = _DIR.parent
_EMBR = _SCRIPTS / "embr"


def _ensure_import_paths() -> None:
    for path in (_DIR, _EMBR, _SCRIPTS):
        text = str(path)
        if text in sys.path:
            sys.path.remove(text)
        sys.path.insert(0, text)


_ensure_import_paths()


def _scope(surface: str, selection) -> bool:
    _ensure_import_paths()
    import embr_rn_selection as rn_sel

    return rn_sel.cache_selection(surface, selection)


def _open(surface: str, _selection) -> None:
    """Open Rename using the isVisible-cached selection only."""
    _ensure_import_paths()
    import embr_log as log
    import embr_rn_selection as rn_sel
    import embr_version as version

    version.require_min("2025.0")
    cached = rn_sel.get_cached_selection(surface)
    if not cached:
        log.error(
            "Embr Rename: no cached selection from the context menu. "
            "Right-click the objects again and choose Rename.",
            duration=8,
        )
        return
    try:
        import embr_rn_window

        embr_rn_window.open_rename(cached, surface=surface)
    except Exception as exc:
        log.error(f"Embr Rename: failed to open - {exc}", duration=10)
        raise


def _menu_actions(surface: str):
    _ensure_import_paths()
    try:
        import embr_menus as menus

        return menus.group(
            surface,
            [
                menus.action(
                    surface,
                    "rename",
                    caption="Rename",
                    execute=lambda sel, s=surface: _open(s, sel),
                    is_visible=lambda sel, s=surface: _scope(s, sel),
                ),
            ],
        )
    except Exception:
        try:
            import embr_log as log

            log.error(
                "Embr Rename: menu build failed; using fallback entry.",
                duration=8,
            )
        except Exception:
            pass
        return [
            {
                "name": "Embr",
                "actions": [
                    {
                        "name": "Rename",
                        "execute": lambda sel, s=surface: _open(s, sel),
                        "isVisible": lambda sel, s=surface: _scope(s, sel),
                        "minimumVersion": "2025.0.0.0",
                        "order": 100,
                    }
                ],
            }
        ]


def get_timeline_custom_ui_actions():
    return _menu_actions("timeline")


def get_media_panel_custom_ui_actions():
    return _menu_actions("media_panel")


def get_batch_custom_ui_actions():
    return _menu_actions("batch")
