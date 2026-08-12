"""Fetch and validate the Embr package catalog from GitHub."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

DEFAULT_REPO = "embr-dev/embr-python-scripts"
DEFAULT_REF = "main"
USER_AGENT = "Embr-Script-Manager/0.1"

# Channel name → git ref (branch or tag) that hosts catalog/catalog.json.
CHANNELS: dict[str, str] = {
    "stable": "stable",
    "latest": "main",
    "dev": "dev",
}
DEFAULT_CHANNEL = "dev"
CHANNEL_ORDER = ("stable", "latest", "dev")
CHANNEL_HINTS: dict[str, str] = {
    "stable": "released",
    "latest": "main tip",
    "dev": "validation / pre-release",
}


class CatalogError(RuntimeError):
    """Raised when the catalog cannot be fetched or validated."""


@dataclass
class PackageInfo:
    id: str
    name: str
    version: str
    kind: str
    path: str
    min_flame: str
    digest: str
    files: list[dict[str, str]] = field(default_factory=list)
    depends: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PackageInfo:
        required = ("id", "name", "version", "kind", "path", "min_flame", "digest", "files")
        missing = [k for k in required if k not in data]
        if missing:
            raise CatalogError(
                f"Embr Script Manager: invalid catalog package - missing keys {missing}"
            )
        files = data.get("files") or []
        if not isinstance(files, list):
            raise CatalogError(
                "Embr Script Manager: invalid catalog package - 'files' must be a list"
            )
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            version=str(data["version"]),
            kind=str(data["kind"]),
            path=str(data["path"]),
            min_flame=str(data["min_flame"]),
            digest=str(data["digest"]),
            files=list(files),
            depends=[str(d) for d in (data.get("depends") or [])],
        )


@dataclass
class Catalog:
    schema: int
    repo: str
    ref: str
    packages: list[PackageInfo]

    def by_id(self, package_id: str) -> PackageInfo | None:
        for pkg in self.packages:
            if pkg.id == package_id:
                return pkg
        return None


def catalog_url(repo: str = DEFAULT_REPO, ref: str = DEFAULT_REF) -> str:
    # Query busts raw.githubusercontent.com CDN (often ~5 min); branch tip moves fast on dev.
    return (
        f"https://raw.githubusercontent.com/{repo}/{ref}/catalog/catalog.json"
        f"?t={int(time.time())}"
    )


def raw_file_url(repo: str, ref: str, repo_path: str) -> str:
    return (
        f"https://raw.githubusercontent.com/{repo}/{ref}/{repo_path}"
        f"?t={int(time.time())}"
    )


def normalize_channel(channel: str | None) -> str:
    """Return a known channel name, or raise ``CatalogError``."""
    name = (channel or DEFAULT_CHANNEL).strip().lower()
    if name not in CHANNELS:
        known = ", ".join(CHANNEL_ORDER)
        raise CatalogError(
            f"Embr Script Manager: unknown channel '{channel}'. "
            f"Choose one of: {known}."
        )
    return name


def ref_for_channel(channel: str | None) -> str:
    """Map a channel name to its git ref."""
    return CHANNELS[normalize_channel(channel)]


def channel_label(channel: str) -> str:
    """Short UI label for a channel (stable / latest / dev)."""
    return normalize_channel(channel)


def parse_catalog(data: dict[str, Any]) -> Catalog:
    if not isinstance(data, dict):
        raise CatalogError("Embr Script Manager: catalog root must be a JSON object")
    for key in ("schema", "repo", "ref", "packages"):
        if key not in data:
            raise CatalogError(
                f"Embr Script Manager: invalid catalog - missing key '{key}'"
            )
    packages_raw = data["packages"]
    if not isinstance(packages_raw, list):
        raise CatalogError("Embr Script Manager: invalid catalog - 'packages' must be a list")
    packages = [PackageInfo.from_dict(item) for item in packages_raw]
    return Catalog(
        schema=int(data["schema"]),
        repo=str(data["repo"]),
        ref=str(data["ref"]),
        packages=packages,
    )


def load_catalog_from_path(path: str) -> Catalog:
    """Load catalog JSON from a local file (tests / offline)."""
    from pathlib import Path

    text = Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CatalogError(
            f"Embr Script Manager: invalid catalog JSON in {path} - {exc}"
        ) from exc
    return parse_catalog(data)


def fetch_bytes(url: str, *, timeout: float = 30.0) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise CatalogError(
            f"Embr Script Manager: failed to fetch {url} - HTTP {exc.code}. "
            "Check network / GitHub availability."
        ) from exc
    except urllib.error.URLError as exc:
        raise CatalogError(
            f"Embr Script Manager: failed to fetch {url} - {exc.reason}. "
            "Check network / GitHub availability."
        ) from exc
    except TimeoutError as exc:
        raise CatalogError(
            f"Embr Script Manager: timed out fetching {url}. "
            "Check network / GitHub availability."
        ) from exc


def fetch_catalog(
    repo: str = DEFAULT_REPO,
    ref: str = DEFAULT_REF,
    *,
    timeout: float = 30.0,
) -> Catalog:
    url = catalog_url(repo, ref)
    raw = fetch_bytes(url, timeout=timeout)
    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise CatalogError(
            f"Embr Script Manager: invalid catalog JSON from {url} - {exc}"
        ) from exc
    return parse_catalog(data)


def fetch_catalog_for_channel(
    channel: str | None = None,
    *,
    repo: str = DEFAULT_REPO,
    timeout: float = 30.0,
) -> Catalog:
    """Fetch catalog.json for a named channel (stable / latest / dev)."""
    name = normalize_channel(channel)
    return fetch_catalog(repo=repo, ref=ref_for_channel(name), timeout=timeout)
