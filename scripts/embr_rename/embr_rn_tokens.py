"""Token expansion and find/replace for Embr Rename."""

from __future__ import annotations

import re
from datetime import date
from typing import Iterable, Sequence

# Pattern tokens look like <name> or <date@YYMMDD>.
_TOKEN_RE = re.compile(r"<([a-zA-Z_][a-zA-Z0-9_]*)(?:@([^>]*))?>")

# Compact date tokens → strftime. Unknown letters pass through strftime rules.
_DATE_TOKEN_MAP = {
    "YYYY": "%Y",
    "YY": "%y",
    "MM": "%m",
    "DD": "%d",
    "HH": "%H",
    "mm": "%M",
    "SS": "%S",
}

DEFAULT_PATTERN = "<name>"
DEFAULT_DATE_FORMAT = "YYMMDD"


def date_format_to_strftime(fmt: str) -> str:
    """Convert compact tokens (YYMMDD, YYYY-MM-DD, …) to strftime."""
    text = (fmt or DEFAULT_DATE_FORMAT).strip() or DEFAULT_DATE_FORMAT
    # Longest keys first so YYYY wins over YY.
    for key in sorted(_DATE_TOKEN_MAP, key=len, reverse=True):
        text = text.replace(key, _DATE_TOKEN_MAP[key])
    return text


def expand_tokens(
    pattern: str,
    *,
    original_name: str,
    today: date | None = None,
) -> str:
    """Expand ``<name>`` / ``<date@FORMAT>`` in ``pattern``."""
    when = today or date.today()

    def _replace(match: re.Match[str]) -> str:
        kind = match.group(1).lower()
        arg = match.group(2)
        if kind == "name":
            return original_name
        if kind == "date":
            fmt = date_format_to_strftime(arg if arg is not None else DEFAULT_DATE_FORMAT)
            try:
                return when.strftime(fmt)
            except ValueError:
                return when.strftime(date_format_to_strftime(DEFAULT_DATE_FORMAT))
        # Unknown token: leave literal.
        return match.group(0)

    return _TOKEN_RE.sub(_replace, pattern)


def apply_replacements(text: str, pairs: Sequence[tuple[str, str]]) -> str:
    """Apply find/replace pairs in order. Empty find strings are skipped."""
    result = text
    for find, replace in pairs:
        if not find:
            continue
        result = result.replace(find, replace)
    return result


def compute_new_name(
    original_name: str,
    pattern: str,
    pairs: Sequence[tuple[str, str]] | None = None,
    *,
    today: date | None = None,
) -> str:
    """Pattern tokens then find/replace. May return empty string."""
    expanded = expand_tokens(pattern, original_name=original_name, today=today)
    return apply_replacements(expanded, pairs or ())


def object_name(obj: object) -> str:
    """Return a plain string name from a Flame object or mock."""
    name = getattr(obj, "name", None)
    if name is None:
        return ""
    # Flame PyString-like: prefer get_value when present.
    getter = getattr(name, "get_value", None)
    if callable(getter):
        try:
            return str(getter())
        except Exception:
            pass
    return str(name)


def is_renameable(obj: object) -> bool:
    """True if ``obj`` has a usable ``name`` attribute."""
    return hasattr(obj, "name")


def renameable_items(selection: Iterable[object]) -> list[object]:
    """Filter selection to objects that look renameable."""
    return [item for item in selection if is_renameable(item)]
