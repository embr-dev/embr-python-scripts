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

__version__ = "0.1.0"

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
    import importlib

    _ensure_import_paths()

    # Drop stale helper modules only (keep this hook module).
    for name in list(sys.modules):
        if name.startswith("embr_sm_") or name in {
            "embr_paths",
            "embr_log",
            "embr_hooks",
            "embr_names",
            "embr_version",
            "embr_ui",
        }:
            del sys.modules[name]
        if name == "embr" or name.startswith("embr."):
            del sys.modules[name]

    importlib.invalidate_caches()
    _ensure_import_paths()

    # Import helpers by unique basename — do not rely on package relative imports.
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
    return [
        {
            "name": "Embr",
            "actions": [
                {
                    "name": "Script Manager",
                    "execute": _open_manager,
                    "minimumVersion": "2025.0.0.0",
                }
            ],
        }
    ]
