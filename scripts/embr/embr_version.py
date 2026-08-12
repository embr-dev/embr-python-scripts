"""Flame version helpers."""

from __future__ import annotations

from typing import Iterable


class VersionError(RuntimeError):
    """Raised when the running Flame version does not meet a requirement."""


def get_version() -> str:
    """Return Flame version string, e.g. ``\"2025.2.1\"``."""
    import flame

    return str(flame.get_version())


def parse_version(value: str) -> tuple[int, ...]:
    """Parse a Flame version string into comparable ints.

    Examples:
        ``\"2025\"`` -> ``(2025,)``
        ``\"2025.2.1\"`` -> ``(2025, 2, 1)``
        ``\"2025.1.pr145\"`` -> ``(2025, 1)``
    """
    text = value.strip()
    if ".pr" in text:
        text = text.split(".pr", 1)[0]

    parts: list[int] = []
    for token in text.split("."):
        if not token:
            continue
        if not token.isdigit():
            break
        parts.append(int(token))

    if not parts:
        raise ValueError(f"Cannot parse Flame version: {value!r}")
    return tuple(parts)


def _pad(a: Iterable[int], b: Iterable[int]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    aa = tuple(a)
    bb = tuple(b)
    length = max(len(aa), len(bb))
    return aa + (0,) * (length - len(aa)), bb + (0,) * (length - len(bb))


def is_at_least(minimum: str, current: str | None = None) -> bool:
    """Return True if ``current`` (default: running Flame) >= ``minimum``."""
    running = current if current is not None else get_version()
    left, right = _pad(parse_version(running), parse_version(minimum))
    return left >= right


def require_min(minimum: str = "2025.0", current: str | None = None) -> str:
    """Require a minimum Flame version; raise ``VersionError`` if unmet.

    Returns the running version string when the check passes.
    """
    running = current if current is not None else get_version()
    if not is_at_least(minimum, running):
        raise VersionError(
            f"Flame {minimum}+ required, but running version is {running}"
        )
    return running
