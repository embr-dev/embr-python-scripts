#!/usr/bin/env python3
"""Offline tests for Embr Rename token / replace helpers."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RENAME = SCRIPTS / "embr_rename"
EMBR = SCRIPTS / "embr"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(EMBR))
sys.path.insert(0, str(RENAME))


def main() -> None:
    import embr_rn_tokens as tokens
    import embr_rn_selection as rn_sel

    today = date(2026, 8, 12)
    assert (
        tokens.expand_tokens("<name>", original_name="Shot_001", today=today)
        == "Shot_001"
    )
    assert (
        tokens.expand_tokens(
            "<name>_<date@YYMMDD>", original_name="Shot_001", today=today
        )
        == "Shot_001_260812"
    )
    assert (
        tokens.expand_tokens("<date@YYYY-MM-DD>", original_name="x", today=today)
        == "2026-08-12"
    )
    assert tokens.apply_replacements("aa_bb_aa", [("aa", "XX"), ("bb", "YY")]) == "XX_YY_XX"
    assert tokens.apply_replacements("keep", [("", "x")]) == "keep"
    assert (
        tokens.compute_new_name(
            "Shot_v001",
            "<name>",
            [("v001", "v002")],
            today=today,
        )
        == "Shot_v002"
    )

    class Obj:
        def __init__(self, name: str) -> None:
            self.name = name

    class NoName:
        pass

    sel = (Obj("A"), NoName(), Obj("B"))
    assert rn_sel.cache_selection("timeline", sel) is True
    assert rn_sel.get_cached_selection("timeline") == sel
    assert rn_sel.cache_selection("timeline", (NoName(),)) is False
    assert rn_sel.get_cached_selection("timeline") == ()

    # execute path ignores live selection — cache is source of truth
    rn_sel.cache_selection("media_panel", (Obj("Clip"),))
    assert len(tokens.renameable_items(rn_sel.get_cached_selection("media_panel"))) == 1

    print("ok")


if __name__ == "__main__":
    main()
