#!/usr/bin/env python3
"""Install / repair / uninstall the Embr AI / PyBox runtime under ``~/Embr``.

Flame is not required. Example:

  python3 tools/install_embr_runtime.py
  python3 tools/install_embr_runtime.py --status
  python3 tools/install_embr_runtime.py --repair
  python3 tools/install_embr_runtime.py --uninstall --yes

See ``docs/ai-runtime.md``. Distinct from Flame hooks under ``…/python/Embr/``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS / "embr"))
sys.path.insert(0, str(SCRIPTS))


def _print_status(status) -> None:
    print(f"EMBR_HOME={status.home}")
    for item in status.items:
        mark = "OK" if item.ok else "--"
        detail = f"  {item.detail}" if item.detail else ""
        print(f"  [{mark}] {item.label}{detail}")
    print(f"{status.ok_count}/{len(status.items)} checks OK")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--home",
        type=Path,
        default=None,
        help="Override EMBR_HOME (default: ~/Embr or $EMBR_HOME)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Probe runtime and exit (no install)",
    )
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Repair uv / venv / bootstrap without forcing repo update",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove EMBR_HOME (and optional ~/embr-ml symlink)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip uninstall confirmation",
    )
    parser.add_argument(
        "--no-update-repo",
        action="store_true",
        help="On install: clone if missing, but do not git fetch/pull",
    )
    args = parser.parse_args()

    import embr_runtime as runtime

    home = args.home.resolve() if args.home is not None else None

    def log(message: str) -> None:
        print(message, flush=True)

    try:
        if args.status:
            _print_status(runtime.probe_status(home))
            return 0

        if args.uninstall:
            target = home or runtime.embr_home()
            if not args.yes:
                reply = input(f"Remove runtime at {target}? [y/N] ").strip().lower()
                if reply not in ("y", "yes"):
                    print("Cancelled.")
                    return 1
            runtime.uninstall_runtime(home, log=log)
            print("Uninstall finished.")
            return 0

        if args.repair:
            status = runtime.repair_runtime(home, log=log)
        else:
            status = runtime.install_or_update_runtime(
                home,
                update_repo=not args.no_update_repo,
                log=log,
            )
        _print_status(status)
        return 0 if status.all_ok else 2
    except runtime.EmbrRuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
