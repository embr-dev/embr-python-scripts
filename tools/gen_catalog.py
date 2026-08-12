#!/usr/bin/env python3
"""Generate catalog/catalog.json from scripts/embr and scripts/embr_* packages."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
OUT = ROOT / "catalog" / "catalog.json"

REPO = "embr-dev/embr-python-scripts"
SCHEMA = 1
MIN_FLAME = "2025.0"


def detect_ref() -> str:
    """Prefer EMBR_CATALOG_REF, else current git branch, else main."""
    env = os.environ.get("EMBR_CATALOG_REF", "").strip()
    if env:
        return env
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if out and out != "HEAD":
            return out
    except (OSError, subprocess.CalledProcessError):
        pass
    return "main"


REF = detect_ref()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def package_digest(files: list[dict[str, str]]) -> str:
    lines = [f"{entry['path']}:{entry['sha256']}" for entry in sorted(files, key=lambda e: e["path"])]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def read_version(pkg_dir: Path, pkg_id: str) -> str:
    init = pkg_dir / "__init__.py"
    if init.is_file():
        text = init.read_text(encoding="utf-8")
        m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
        if m:
            return m.group(1)
    entry = pkg_dir / f"{pkg_id}.py"
    if entry.is_file():
        text = entry.read_text(encoding="utf-8")
        m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
        if m:
            return m.group(1)
    return "0.1.0"


def collect_files(pkg_dir: Path) -> list[dict[str, str]]:
    files: list[dict[str, str]] = []
    for path in sorted(pkg_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        rel = path.relative_to(pkg_dir).as_posix()
        files.append({"path": rel, "sha256": sha256_file(path)})
    return files


def discover_packages() -> list[Path]:
    packages: list[Path] = []
    embr = SCRIPTS / "embr"
    if embr.is_dir():
        packages.append(embr)
    for path in sorted(SCRIPTS.glob("embr_*")):
        if path.is_dir():
            packages.append(path)
    return packages


def build_package(pkg_dir: Path) -> dict:
    pkg_id = pkg_dir.name
    files = collect_files(pkg_dir)
    kind = "library" if pkg_id == "embr" else "tool"
    entry: dict = {
        "id": pkg_id,
        "name": "Embr Core" if pkg_id == "embr" else pkg_id.replace("_", " ").title(),
        "version": read_version(pkg_dir, pkg_id),
        "kind": kind,
        "path": f"scripts/{pkg_id}",
        "min_flame": MIN_FLAME,
        "digest": package_digest(files),
        "files": files,
    }
    if pkg_id != "embr":
        entry["depends"] = ["embr"]
        if pkg_id == "embr_manager":
            entry["name"] = "Script Manager"
        elif pkg_id == "embr_preferences":
            entry["name"] = "Preferences"
        elif pkg_id == "embr_rename":
            entry["name"] = "Rename"
    return entry


def main() -> None:
    packages = [build_package(p) for p in discover_packages()]
    catalog = {
        "schema": SCHEMA,
        "repo": REPO,
        "ref": REF,
        "packages": packages,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} (ref={REF}, {len(packages)} package(s))")
    for pkg in packages:
        print(f"  - {pkg['id']} {pkg['version']} files={len(pkg['files'])} digest={pkg['digest'][:12]}...")


if __name__ == "__main__":
    main()
