################################################################################
# Embr Script Manager
#
# Main Menu: Embr / Script Manager
#
# Flame + DL_PYTHON_HOOK_PATH loads each .py by basename (not as a package).
# Helpers use unique names (embr_sm_*.py). Import them as top-level modules
# after putting this directory (and scripts/embr) on sys.path.
################################################################################

from __future__ import annotations

import sys
from pathlib import Path

__version__ = "0.1.12"

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


def _open_manager(_selection) -> None:
    _ensure_import_paths()

    # Reuse an open window (avoids duplicate UIs and skip re-import cost).
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        existing = getattr(app, "_embr_script_manager", None) if app else None
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

    # Do not wipe sys.modules here — Flame Rescan uses importlib.reload on the
    # same module objects; deleting them first floods the log with ImportError.
    import embr_log as log
    import embr_version as version

    version.require_min("2025.0")
    try:
        import embr_sm_window

        embr_sm_window.open_script_manager()
    except Exception as exc:
        log.error(f"Embr Script Manager: failed to open - {exc}", duration=10)
        raise


def get_main_menu_custom_ui_actions():
    """Register Script Manager under Main Menu -> Embr.

    Import ``embr_menus`` by basename (Flame-safe). Never raise — an empty or
    failing hook would remove the whole Embr submenu.
    """
    _ensure_import_paths()
    try:
        import embr_menus as menus

        built = menus.group(
            "main_menu",
            [
                menus.action(
                    "main_menu",
                    "script_manager",
                    caption="Script Manager",
                    execute=_open_manager,
                ),
            ],
        )
        if built:
            return built
    except Exception:
        try:
            import embr_log as log

            log.error(
                "Embr Script Manager: menu build failed; using fallback entry.",
                duration=8,
            )
        except Exception:
            pass

    return [
        {
            "name": "Embr",
            "actions": [
                {
                    "name": "Script Manager",
                    "execute": _open_manager,
                    "minimumVersion": "2025.0.0.0",
                    "order": 100,
                }
            ],
        }
    ]
