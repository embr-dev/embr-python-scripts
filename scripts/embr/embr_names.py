"""Unique name helpers."""

from __future__ import annotations

from typing import Iterable, Sequence


def unique_name(base: str, existing: Iterable[str]) -> str:
    """Return ``base`` or ``base1``, ``base2``, ... not present in ``existing``."""
    taken = set(existing)
    if base not in taken:
        return base

    index = 1
    while f"{base}{index}" in taken:
        index += 1
    return f"{base}{index}"


def unique_names(bases: Sequence[str], existing: Iterable[str]) -> list[str]:
    """Make each name in ``bases`` unique against ``existing`` and prior results."""
    taken = set(existing)
    result: list[str] = []
    for base in bases:
        name = unique_name(base, taken)
        result.append(name)
        taken.add(name)
    return result
