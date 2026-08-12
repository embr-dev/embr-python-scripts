"""Logging to the terminal and Flame message console."""

from __future__ import annotations

from typing import Any


def _console(message: str, level: str, duration: int) -> None:
    print(message)
    try:
        import flame

        flame.messages.show_in_console(message, level, duration)
    except Exception:
        # Outside Flame, or message API unavailable: terminal print is enough.
        pass


def info(message: Any, duration: int = 3) -> None:
    """Info message (terminal + Flame console)."""
    _console(str(message), "info", duration)


def warning(message: Any, duration: int = 5) -> None:
    """Warning message (terminal + Flame console)."""
    _console(str(message), "warning", duration)


def error(message: Any, duration: int = 8) -> None:
    """Error message (terminal + Flame console)."""
    _console(str(message), "error", duration)


def title(text: Any) -> None:
    """Print a simple banner to the terminal (and a short console line)."""
    label = str(text)
    line = f"====[ {label} ]===="
    banner = line.center(72, "-")
    print(banner)
    try:
        import flame

        flame.messages.show_in_console(label, "info", 2)
    except Exception:
        pass
