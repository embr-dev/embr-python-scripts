"""Embr menu helpers: defaults, user prefs, and Flame action dicts.

Tools declare actions with stable ids. Display order and user visibility come
from ``menus/defaults.json`` merged with per-user ``…/flame/embr/prefs.json``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Iterable

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

import embr_paths as paths

GROUP_NAME = "Embr"
PREFS_FILE_NAME = "prefs.json"
DEFAULTS_REL = Path("menus") / "defaults.json"
PREFS_SCHEMA = 1

# Surfaces that map to Flame get_*_custom_ui_actions entry points.
SURFACES: tuple[str, ...] = (
    "main_menu",
    "timeline",
    "media_panel",
    "batch",
    "action",
    "mediahub_files",
    "mediahub_projects",
    "mediahub_archives",
)

SURFACE_LABELS: dict[str, str] = {
    "main_menu": "Main Menu",
    "timeline": "Timeline",
    "media_panel": "Media Panel",
    "batch": "Batch",
    "action": "Action",
    "mediahub_files": "MediaHub Files",
    "mediahub_projects": "MediaHub Projects",
    "mediahub_archives": "MediaHub Archives",
}

_DEFAULT_ORDER_FALLBACK = 9000
_ORDER_STEP = 100

IsVisible = bool | Callable[[Any], bool]
IsEnabled = bool | Callable[[Any], bool]


class MenuError(RuntimeError):
    """Raised when menu defaults or prefs cannot be read or written."""


def defaults_path() -> Path:
    """Return path to bundled ``menus/defaults.json``."""
    return paths.package_dir() / DEFAULTS_REL


def prefs_path(config_root: Path | None = None) -> Path:
    """Return ``…/flame/embr/prefs.json`` (always per-user, not install root).

    ``config_root`` overrides the directory for tests; production code should
    leave it ``None`` so ``paths.flame_user_embr_dir()`` is used.
    """
    base = (config_root or paths.flame_user_embr_dir()).resolve()
    return base / PREFS_FILE_NAME


def _empty_prefs() -> dict[str, Any]:
    return {"schema": PREFS_SCHEMA, "menus": {}}


def load_defaults() -> dict[str, Any]:
    """Load bundled menu defaults."""
    path = defaults_path()
    if not path.is_file():
        raise MenuError(
            f"Embr menus: defaults file missing at {path}. "
            "Reinstall Embr Core or check the package layout."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MenuError(
            f"Embr menus: cannot read defaults at {path} - {exc}."
        ) from exc
    if not isinstance(data, dict):
        raise MenuError(f"Embr menus: defaults at {path} must be a JSON object.")
    surfaces = data.get("surfaces")
    if not isinstance(surfaces, dict):
        raise MenuError(f"Embr menus: defaults at {path} need a surfaces object.")
    return data


def _defaults_or_empty() -> dict[str, Any]:
    """Return defaults, or an empty surfaces map if the file is missing/broken."""
    try:
        return load_defaults()
    except MenuError:
        return {"schema": 1, "surfaces": {}}


def load_prefs(config_root: Path | None = None) -> dict[str, Any]:
    """Load user prefs; missing or invalid file yields empty menus prefs."""
    path = prefs_path(config_root)
    if not path.is_file():
        return _empty_prefs()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _empty_prefs()
    if not isinstance(data, dict):
        return _empty_prefs()
    menus = data.get("menus")
    if not isinstance(menus, dict):
        return _empty_prefs()
    return {"schema": int(data.get("schema") or PREFS_SCHEMA), "menus": menus}


def save_prefs(prefs: dict[str, Any], config_root: Path | None = None) -> Path:
    """Write prefs JSON under the per-user ``flame/embr`` dir. Returns the path."""
    path = prefs_path(config_root)
    try:
        paths.ensure_writable(path.parent)
        payload = {
            "schema": int(prefs.get("schema") or PREFS_SCHEMA),
            "menus": prefs.get("menus") if isinstance(prefs.get("menus"), dict) else {},
        }
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except paths.PathError as exc:
        raise MenuError(str(exc)) from exc
    except OSError as exc:
        raise MenuError(
            f"Embr menus: cannot write prefs at {path} - {exc}. "
            "Check that the per-user flame/embr directory is writable."
        ) from exc
    return path


def reset_menu_prefs(config_root: Path | None = None) -> Path:
    """Clear all menu overrides (keep prefs file with empty menus)."""
    return save_prefs(_empty_prefs(), config_root=config_root)


def set_surface_prefs(
    surface: str,
    *,
    order: Iterable[str] | None = None,
    hidden: Iterable[str] | None = None,
    config_root: Path | None = None,
) -> dict[str, Any]:
    """Update one surface in prefs and save. Returns the full prefs dict."""
    if surface not in SURFACES:
        raise MenuError(
            f"Embr menus: unknown surface {surface!r}. "
            f"Expected one of: {', '.join(SURFACES)}."
        )
    prefs = load_prefs(config_root)
    menus = prefs.setdefault("menus", {})
    entry: dict[str, Any] = {}
    locked_ids = {e["id"] for e in _default_entries(surface) if e.get("locked")}
    if order is not None:
        entry["order"] = [str(x) for x in order]
    if hidden is not None:
        # Locked actions (Script Manager / Preferences) cannot be hidden.
        entry["hidden"] = [str(x) for x in hidden if str(x) not in locked_ids]
    if entry:
        menus[surface] = entry
    elif surface in menus:
        del menus[surface]
    save_prefs(prefs, config_root=config_root)
    return prefs


def _default_entries(surface: str) -> list[dict[str, Any]]:
    data = _defaults_or_empty()
    raw = (data.get("surfaces") or {}).get(surface) or []
    if not isinstance(raw, list):
        return []
    entries: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        action_id = str(item.get("id") or "").strip()
        if not action_id:
            continue
        entries.append(
            {
                "id": action_id,
                "caption": str(item.get("caption") or action_id),
                "order": int(item.get("order") or _DEFAULT_ORDER_FALLBACK),
                "visible": bool(item.get("visible", True)),
                "locked": bool(item.get("locked", False)),
            }
        )
    entries.sort(key=lambda e: (e["order"], e["id"]))
    return entries


def _prefs_surface(prefs: dict[str, Any], surface: str) -> dict[str, Any]:
    menus = prefs.get("menus") or {}
    raw = menus.get(surface) if isinstance(menus, dict) else None
    return raw if isinstance(raw, dict) else {}


def resolve(
    surface: str, action_id: str, config_root: Path | None = None
) -> tuple[int, bool]:
    """Return ``(order, visible)`` for ``action_id`` on ``surface``."""
    entries = effective_entries(surface, config_root=config_root)
    for entry in entries:
        if entry["id"] == action_id:
            return int(entry["order"]), bool(entry["visible"])
    return _DEFAULT_ORDER_FALLBACK, True


def effective_entries(
    surface: str, config_root: Path | None = None
) -> list[dict[str, Any]]:
    """Return merged default + prefs entries for Preferences UI and resolve()."""
    defaults = _default_entries(surface)
    by_id = {e["id"]: e for e in defaults}
    prefs_surf = _prefs_surface(load_prefs(config_root), surface)
    hidden = {str(x) for x in (prefs_surf.get("hidden") or [])}
    pref_order = [str(x) for x in (prefs_surf.get("order") or []) if str(x)]

    ordered_ids: list[str] = []
    seen: set[str] = set()
    if pref_order:
        for action_id in pref_order:
            if action_id in by_id and action_id not in seen:
                ordered_ids.append(action_id)
                seen.add(action_id)
        for entry in defaults:
            if entry["id"] not in seen:
                ordered_ids.append(entry["id"])
                seen.add(entry["id"])
    else:
        ordered_ids = [e["id"] for e in defaults]

    result: list[dict[str, Any]] = []
    for index, action_id in enumerate(ordered_ids):
        base = by_id[action_id]
        locked = bool(base.get("locked"))
        user_hidden = action_id in hidden and not locked
        result.append(
            {
                "id": action_id,
                "caption": base["caption"],
                "order": (index + 1) * _ORDER_STEP,
                "visible": bool(base["visible"]) and not user_hidden,
                "locked": locked,
                "default_order": base["order"],
                "default_visible": base["visible"],
            }
        )
    return result


def action(
    surface: str,
    action_id: str,
    *,
    execute: Callable[..., Any],
    caption: str | None = None,
    is_visible: IsVisible | None = None,
    is_enabled: IsEnabled | None = None,
    minimum_version: str = "2025.0.0.0",
    config_root: Path | None = None,
    **extra: Any,
) -> dict[str, Any] | None:
    """Build one Flame action dict, or ``None`` if the user hid it.

    ``is_visible`` is the selection-scope callback/bool; user hide omits the
    item entirely. Extra keys are passed through to the action dict.
    """
    order, visible = resolve(surface, action_id, config_root=config_root)
    if not visible:
        return None

    defaults = {e["id"]: e for e in _default_entries(surface)}
    label = caption or (defaults.get(action_id) or {}).get("caption") or action_id

    item: dict[str, Any] = {
        "name": label,
        "execute": execute,
        "minimumVersion": minimum_version,
        "order": order,
    }
    if is_visible is not None:
        item["isVisible"] = is_visible
    if is_enabled is not None:
        item["isEnabled"] = is_enabled
    item.update(extra)
    return item


def group(
    surface: str,
    actions: Iterable[dict[str, Any] | None],
    *,
    name: str = GROUP_NAME,
) -> list[dict[str, Any]]:
    """Wrap action dicts in an Embr submenu group, sorted by ``order``."""
    del surface  # reserved for future hierarchy / separators per surface
    items = [a for a in actions if a]
    items.sort(
        key=lambda a: (
            int(a.get("order") or _DEFAULT_ORDER_FALLBACK),
            str(a.get("name") or ""),
        )
    )
    if not items:
        return []
    return [{"name": name, "actions": items}]


def surfaces_with_entries() -> list[str]:
    """Return surfaces that have at least one default entry (for Preferences)."""
    data = _defaults_or_empty()
    surfaces = data.get("surfaces") or {}
    result: list[str] = []
    for surface in SURFACES:
        raw = surfaces.get(surface) or []
        if isinstance(raw, list) and raw:
            result.append(surface)
    return result


def refresh_hooks_after_prefs() -> None:
    """Rescan Flame hooks so menu order/visibility updates."""
    import embr_hooks as hooks

    hooks.refresh()
