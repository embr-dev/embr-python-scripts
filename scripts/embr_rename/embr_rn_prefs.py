"""Persist Rename UI state under prefs.json ``rename`` key."""

from __future__ import annotations

from typing import Any

import embr_menus as menus
import embr_rn_tokens as tokens


def load_rename_prefs(config_root=None) -> dict[str, Any]:
    """Return ``{pattern, replacements}`` with defaults."""
    data = menus.load_prefs(config_root)
    raw = data.get("rename") if isinstance(data.get("rename"), dict) else {}
    pattern = str(raw.get("pattern") or tokens.DEFAULT_PATTERN)
    pairs_raw = raw.get("replacements") or []
    pairs: list[tuple[str, str]] = []
    if isinstance(pairs_raw, list):
        for item in pairs_raw:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                pairs.append((str(item[0]), str(item[1])))
            elif isinstance(item, dict):
                pairs.append((str(item.get("find") or ""), str(item.get("replace") or "")))
    return {"pattern": pattern, "replacements": pairs}


def save_rename_prefs(
    *,
    pattern: str,
    replacements: list[tuple[str, str]],
    config_root=None,
) -> None:
    """Merge rename section into prefs.json without wiping menus."""
    data = menus.load_prefs(config_root)
    data["rename"] = {
        "pattern": pattern,
        "replacements": [{"find": a, "replace": b} for a, b in replacements],
    }
    menus.save_prefs(data, config_root=config_root)
