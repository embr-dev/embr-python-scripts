#!/usr/bin/env python3
"""Bootstrap Embr from a GitHub channel into User or Shared python/Embr.

Example:

  # Auto-pick newest Flame Python (handles 2025.2.7 style paths):
  "$(./tools/find_flame_python.sh)" tools/bootstrap_from_channel.py --channel dev

  # Or call a versioned interpreter directly:
  /opt/Autodesk/python/2025.2.7/bin/python3 tools/bootstrap_from_channel.py --channel dev

  # Shared install:
  "$(./tools/find_flame_python.sh)" tools/bootstrap_from_channel.py --channel dev --shared

System ``python3`` (3.9+) is also fine for this script; Flame's python is
only required for PySide6 UI tests / in-app use.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS / "embr"))
sys.path.insert(0, str(SCRIPTS / "embr_manager"))
sys.path.insert(0, str(SCRIPTS))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--channel",
        default="dev",
        choices=("stable", "latest", "dev"),
        help="Catalog channel (default: dev)",
    )
    parser.add_argument(
        "--shared",
        action="store_true",
        help="Install under shared python/Embr instead of user python/Embr",
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=None,
        help="Optional local scripts/ tree (offline). Default: download from GitHub.",
    )
    args = parser.parse_args()

    import embr_paths as paths
    import embr_sm_bootstrap as bootstrap
    from embr_sm_catalog import fetch_catalog_for_channel

    hooks = paths.flame_shared_python() if args.shared else paths.flame_user_python()
    target = paths.vendor_install_root(hooks)
    print(f"Channel: {args.channel}")
    print(f"Target:  {target}")

    source_root = args.source_root
    if source_root is not None:
        source_root = source_root.resolve()
        cat = None
        # Prefer local catalog next to source when present.
        local_cat = source_root.parent / "catalog" / "catalog.json"
        if local_cat.is_file():
            from embr_sm_catalog import load_catalog_from_path

            cat = load_catalog_from_path(str(local_cat))
            print(f"Catalog: local {local_cat}")
        else:
            cat = fetch_catalog_for_channel(args.channel)
            print(f"Catalog: GitHub channel {args.channel} (files from source-root)")
    else:
        cat = fetch_catalog_for_channel(args.channel)
        print(f"Catalog: GitHub {cat.repo}@{cat.ref}")

    bootstrap.bootstrap_into(
        target,
        catalog=cat,
        source_root=source_root,
        channel=args.channel,
    )
    print("Bootstrap complete.")
    print("Rescan Python Hooks (or restart Flame), then open Embr → Manager.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
