################################################################################
# Embr Preferences
#
# Main Menu: Embr / Preferences
#
# Flame + DL_PYTHON_HOOK_PATH loads each .py by basename (not as a package).
# Helpers use unique names (embr_pref_*.py).
################################################################################

from __future__ import annotations

import sys
from pathlib import Path

__version__ = "0.1.4"

_DIR = Path(__file__).resolve().parent
_SCRIPTS = _DIR.parent
_EMBR = _SCRIPTS / "embr"


def _ensure_import_paths() -> None:
    """Prefer Embr dirs on sys.path (Flame may not keep subdirectory paths)."""
    for path in (_DIR, _EMBR, _SCRIPTS):
        text = str(path)
        if text in sys.path:
            sys.path.remove(text)
        sys.path.insert(0, text)


_ensure_import_paths()


def _open_preferences(_selection) -> None:
    _ensure_import_paths()

    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        existing = getattr(app, "_embr_preferences", None) if app else None
        if existing is not None:
            try:
                existing.show()
                existing.raise_()
                existing.activateWindow()
                return
            except RuntimeError:
                pass
    except Exception:
        pass

    # Do not wipe sys.modules — see embr_manager._open_manager.
    import embr_log as log
    import embr_version as version

    version.require_min("2025.0")
    try:
        import embr_pref_window

        embr_pref_window.open_preferences()
    except Exception as exc:
        log.error(f"Embr Preferences: failed to open - {exc}", duration=10)
        raise


def get_main_menu_custom_ui_actions():
    """Register Preferences under Main Menu -> Embr.

    Import ``embr_menus`` by basename (Flame-safe). Never raise — failing hooks
    would drop the Embr submenu when combined with other Embr tools.
    """
    _ensure_import_paths()
    try:
        import embr_menus as menus

        built = menus.group(
            "main_menu",
            [
                menus.action(
                    "main_menu",
                    "preferences",
                    caption="Preferences",
                    execute=_open_preferences,
                ),
            ],
        )
        if built:
            return built
    except Exception:
        try:
            import embr_log as log

            log.error(
                "Embr Preferences: menu build failed; using fallback entry.",
                duration=8,
            )
        except Exception:
            pass

    return [
        {
            "name": "Embr",
            "actions": [
                {
                    "name": "Preferences",
                    "execute": _open_preferences,
                    "minimumVersion": "2025.0.0.0",
                    "order": 200,
                }
            ],
        }
    ]
