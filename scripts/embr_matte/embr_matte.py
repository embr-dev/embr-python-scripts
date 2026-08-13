################################################################################
# Embr Matte
#
# Main Menu: Embr / Matte
# Phase 0: list jobs, Add (export), Import to saved parent, cache.
#
# Flame + DL_PYTHON_HOOK_PATH loads each .py by basename. Helpers use unique
# names (embr_mt_*.py).
################################################################################

from __future__ import annotations

import sys
from pathlib import Path

__version__ = "0.2.1"

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


def _open_matte(_selection) -> None:
    _ensure_import_paths()
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        existing = getattr(app, "_embr_matte", None) if app else None
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

    import embr_log as log
    import embr_version as version

    version.require_min("2025.0")
    try:
        import embr_mt_window

        embr_mt_window.open_matte()
    except Exception as exc:
        log.error(f"Embr Matte: failed to open - {exc}", duration=10)
        raise


def get_main_menu_custom_ui_actions():
    _ensure_import_paths()
    try:
        import embr_menus as menus

        return menus.group(
            "main_menu",
            [
                menus.action(
                    "main_menu",
                    "matte",
                    caption="Matte",
                    execute=_open_matte,
                ),
            ],
        )
    except Exception:
        try:
            import embr_log as log

            log.error(
                "Embr Matte: menu build failed; using fallback entry.",
                duration=8,
            )
        except Exception:
            pass
        return [
            {
                "name": "Embr",
                "actions": [
                    {
                        "name": "Matte",
                        "execute": _open_matte,
                        "minimumVersion": "2025.0.0.0",
                        "order": 150,
                    }
                ],
            }
        ]
