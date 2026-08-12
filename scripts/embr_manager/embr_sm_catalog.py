"""Fetch and validate the Embr package catalog from GitHub."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

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
    # Prefer a commit SHA for ``ref`` — branch names are CDN-cached (~5 min) on
    # raw.githubusercontent.com and query strings do not reliably bust that cache.
    return f"https://raw.githubusercontent.com/{repo}/{ref}/catalog/catalog.json"


def raw_file_url(repo: str, ref: str, repo_path: str) -> str:
    return f"https://raw.githubusercontent.com/{repo}/{ref}/{repo_path}"


def commits_api_url(repo: str, ref: str) -> str:
    """GitHub API URL that resolves a branch/tag/ref to a commit."""
    return f"https://api.github.com/repos/{repo}/commits/{quote(ref, safe='')}"


def contents_api_url(repo: str, path: str, ref: str) -> str:
    """GitHub Contents API URL for a file at ``ref`` (branch, tag, or SHA)."""
    return (
        f"https://api.github.com/repos/{repo}/contents/{quote(path, safe='/')}"
        f"?ref={quote(ref, safe='')}"
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
            "Accept": "application/vnd.github+json",
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


def resolve_ref_sha(
    repo: str,
    ref: str,
    *,
    timeout: float = 30.0,
) -> str:
    """Resolve a branch/tag/ref to a full commit SHA via the GitHub API.

    Raw URLs keyed by branch name are CDN-cached; pinning to a SHA avoids
    stale catalog.json / package files after a push to ``dev``.
    """
    # Already a full SHA — skip the API round-trip.
    if len(ref) == 40 and all(c in "0123456789abcdef" for c in ref.lower()):
        return ref.lower()

    url = commits_api_url(repo, ref)
    raw = fetch_bytes(url, timeout=timeout)
    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise CatalogError(
            f"Embr Script Manager: invalid GitHub commits JSON from {url} - {exc}"
        ) from exc
    sha = str(data.get("sha") or "").strip().lower()
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise CatalogError(
            f"Embr Script Manager: could not resolve ref '{ref}' on {repo} to a "
            "commit SHA. Check the channel / branch name."
        )
    return sha


def fetch_catalog(
    repo: str = DEFAULT_REPO,
    ref: str = DEFAULT_REF,
    *,
    timeout: float = 30.0,
) -> Catalog:
    """Fetch and parse catalog.json, pinned to the resolved commit SHA.

    Uses the GitHub Contents API (not branch-named raw URLs) so Refresh is not
    blocked by raw.githubusercontent.com CDN lag after a push.
    """
    import base64

    sha = resolve_ref_sha(repo, ref, timeout=timeout)
    url = contents_api_url(repo, "catalog/catalog.json", sha)
    raw = fetch_bytes(url, timeout=timeout)
    try:
        meta = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise CatalogError(
            f"Embr Script Manager: invalid GitHub contents JSON from {url} - {exc}"
        ) from exc

    encoding = str(meta.get("encoding") or "")
    if encoding == "base64" and meta.get("content"):
        try:
            text = base64.b64decode(meta["content"]).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise CatalogError(
                f"Embr Script Manager: cannot decode catalog from {url} - {exc}"
            ) from exc
    elif meta.get("download_url"):
        text = fetch_bytes(str(meta["download_url"]), timeout=timeout).decode("utf-8")
    else:
        raise CatalogError(
            f"Embr Script Manager: catalog contents response missing file data ({url})."
        )

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CatalogError(
            f"Embr Script Manager: invalid catalog JSON from {url} - {exc}"
        ) from exc
    catalog = parse_catalog(data)
    # Pin package downloads to the same commit that produced this catalog.
    catalog.ref = sha
    return catalog


def fetch_catalog_for_channel(
    channel: str | None = None,
    *,
    repo: str = DEFAULT_REPO,
    timeout: float = 30.0,
) -> Catalog:
    """Fetch catalog.json for a named channel (stable / latest / dev)."""
    name = normalize_channel(channel)
    return fetch_catalog(repo=repo, ref=ref_for_channel(name), timeout=timeout)
