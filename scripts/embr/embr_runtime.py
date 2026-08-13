"""Embr AI / PyBox runtime under ``$EMBR_HOME`` (default ``~/Embr``).

Distinct from Flame hooks install root (``…/python/Embr/``). See
``docs/ai-runtime.md`` and embr-pybox-handlers handoff.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

LogFn = Callable[[str], None]

HANDLERS_REPO_URL = "https://github.com/embr-dev/embr-pybox-handlers.git"
HANDLERS_DIR_NAME = "embr-pybox-handlers"

# Same channel names as Script Manager; git ref for embr-pybox-handlers.
CHANNELS: dict[str, str] = {
    "stable": "stable",
    "latest": "main",
    "dev": "dev",
}
DEFAULT_CHANNEL = "dev"
CHANNEL_ORDER = ("stable", "latest", "dev")


class EmbrRuntimeError(RuntimeError):
    """Raised when a runtime install / repair step fails."""


def _log(log: LogFn | None, message: str) -> None:
    if log is not None:
        log(message)


def embr_home() -> Path:
    """Return ``$EMBR_HOME`` (default ``~/Embr``)."""
    raw = os.environ.get("EMBR_HOME", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return (Path.home() / "Embr").resolve()


def embr_ml_root(home: Path | None = None) -> Path:
    """Return ``$EMBR_ML_ROOT`` (default ``$EMBR_HOME/ml``)."""
    raw = os.environ.get("EMBR_ML_ROOT", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return (home or embr_home()) / "ml"


def embr_uv_path(home: Path | None = None) -> Path:
    """Return preferred uv binary path (``$EMBR_UV`` or ``$EMBR_HOME/bin/uv``)."""
    raw = os.environ.get("EMBR_UV", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return (home or embr_home()) / "bin" / "uv"


def handlers_repo_path(home: Path | None = None) -> Path:
    """Return ``$EMBR_HOME/repos/embr-pybox-handlers``."""
    return (home or embr_home()) / "repos" / HANDLERS_DIR_NAME


def worker_venv_python(home: Path | None = None) -> Path:
    """Return ``…/worker/.venv/bin/python`` under the handlers repo."""
    return handlers_repo_path(home) / "worker" / ".venv" / "bin" / "python"


def matanyone_weight_path(home: Path | None = None) -> Path:
    return embr_ml_root(home) / "models" / "matanyone2" / "matanyone2.pth"


def legacy_uv_path() -> Path:
    return Path.home() / ".local" / "bin" / "uv"


def legacy_ml_symlink() -> Path:
    return Path.home() / "embr-ml"


def normalize_channel(channel: str | None) -> str:
    name = (channel or DEFAULT_CHANNEL).strip().lower()
    if name not in CHANNELS:
        known = ", ".join(CHANNEL_ORDER)
        raise EmbrRuntimeError(f"Unknown PyBox channel {name!r}; use one of: {known}")
    return name


def channel_ref(channel: str | None = None) -> str:
    """Return git branch/tag for a channel name."""
    return CHANNELS[normalize_channel(channel)]


def state_path(home: Path | None = None) -> Path:
    return (home or embr_home()) / ".embr" / "runtime.json"


def get_channel(home: Path | None = None) -> str:
    path = state_path(home)
    if not path.is_file():
        return DEFAULT_CHANNEL
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_CHANNEL
    raw = str(data.get("channel") or DEFAULT_CHANNEL)
    try:
        return normalize_channel(raw)
    except EmbrRuntimeError:
        return DEFAULT_CHANNEL


def set_channel(home: Path | None = None, channel: str | None = None) -> str:
    root = ensure_layout(home)
    chosen = normalize_channel(channel)
    path = state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"channel": chosen}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return chosen


def _git_capture(
    args: list[str],
    *,
    cwd: Path | None = None,
    timeout: float = 60,
) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, "", str(exc)
    return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()


def local_handlers_sha(repo: Path) -> str:
    if not (repo / ".git").is_dir():
        return ""
    code, out, _ = _git_capture(["git", "rev-parse", "HEAD"], cwd=repo)
    return out if code == 0 else ""


def local_handlers_branch(repo: Path) -> str:
    if not (repo / ".git").is_dir():
        return ""
    code, out, _ = _git_capture(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo
    )
    return out if code == 0 else ""


def remote_handlers_sha(
    ref: str,
    *,
    repo: Path | None = None,
) -> tuple[str, str]:
    """Return ``(sha, error)`` for ``refs/heads/<ref>`` via ``git ls-remote``."""
    if shutil.which("git") is None:
        return "", "git not found"
    target = HANDLERS_REPO_URL
    cwd: Path | None = None
    if repo is not None and (repo / ".git").is_dir():
        cwd = repo
        target = "origin"
    code, out, err = _git_capture(
        ["git", "ls-remote", target, f"refs/heads/{ref}"],
        cwd=cwd,
        timeout=90,
    )
    if code != 0:
        return "", err or f"ls-remote failed ({code})"
    if not out:
        return "", f"branch “{ref}” not found on remote"
    sha = out.split()[0].strip()
    if len(sha) < 7:
        return "", f"unexpected ls-remote output for “{ref}”"
    return sha, ""


@dataclass(frozen=True)
class CheckItem:
    id: str
    label: str
    ok: bool
    detail: str = ""
    mark: str = ""  # OK / — / UPD; empty → derive from ok


@dataclass(frozen=True)
class RuntimeStatus:
    home: Path
    items: tuple[CheckItem, ...]
    channel: str = DEFAULT_CHANNEL
    local_sha: str = ""
    remote_sha: str = ""
    update_available: bool = False
    sync_error: str = ""

    @property
    def ok_count(self) -> int:
        return sum(1 for i in self.items if i.ok)

    @property
    def all_ok(self) -> bool:
        return bool(self.items) and all(i.ok for i in self.items)


def probe_status(
    home: Path | None = None,
    *,
    channel: str | None = None,
    check_remote: bool = True,
) -> RuntimeStatus:
    """Return checklist for the PyBox / AI runtime.

    When ``check_remote`` is True, compares local handlers HEAD to the channel
    branch on GitHub (``git ls-remote``).
    """
    root = (home or embr_home()).expanduser().resolve()
    chosen = normalize_channel(channel if channel is not None else get_channel(root))
    ref = channel_ref(chosen)
    uv = embr_uv_path(root)
    repo = handlers_repo_path(root)
    venv_py = worker_venv_python(root)
    weight = matanyone_weight_path(root)
    bootstrap = repo / "worker" / "embr_ml" / "bootstrap.py"

    local_sha = local_handlers_sha(repo) if repo.is_dir() else ""
    local_branch = local_handlers_branch(repo) if repo.is_dir() else ""
    remote_sha = ""
    sync_error = ""
    update_available = False
    if check_remote and repo.is_dir() and (repo / ".git").is_dir():
        remote_sha, sync_error = remote_handlers_sha(ref, repo=repo)
        if remote_sha and local_sha and remote_sha != local_sha:
            update_available = True
        elif remote_sha and local_branch and local_branch not in (ref, "HEAD"):
            # On another branch than the selected channel.
            if local_sha != remote_sha:
                update_available = True
    elif check_remote and not repo.is_dir():
        # Still probe remote so Install knows the channel exists.
        remote_sha, sync_error = remote_handlers_sha(ref, repo=None)

    if local_sha and remote_sha and not update_available and not sync_error:
        repo_detail = f"{chosen} @{local_sha[:7]} (up to date)"
        repo_mark = "OK"
        repo_ok = True
    elif update_available and local_sha and remote_sha:
        repo_detail = (
            f"{chosen} @{local_sha[:7]} → {remote_sha[:7]} (update available)"
        )
        repo_mark = "UPD"
        repo_ok = True  # installed; update is advisory
    elif local_sha:
        note = sync_error or "remote not checked"
        repo_detail = f"{chosen} @{local_sha[:7]} ({note})"
        repo_mark = "OK"
        repo_ok = True
    else:
        repo_detail = str(repo)
        if remote_sha:
            repo_detail = f"not installed — remote {chosen} @{remote_sha[:7]}"
        elif sync_error:
            repo_detail = f"{repo_detail} — {sync_error}"
        repo_mark = ""
        repo_ok = repo.is_dir() and (repo / "handlers").is_dir()

    items: list[CheckItem] = [
        CheckItem("home", "Embr home", root.is_dir(), str(root)),
        CheckItem(
            "uv",
            "uv (Embr bin)",
            uv.is_file() and os.access(uv, os.X_OK),
            str(uv),
        ),
        CheckItem(
            "repo",
            "handlers repo",
            repo_ok and repo.is_dir() and (repo / "handlers").is_dir(),
            repo_detail,
            mark=repo_mark,
        ),
        CheckItem(
            "bootstrap",
            "worker bootstrap",
            bootstrap.is_file(),
            str(bootstrap),
        ),
        CheckItem(
            "venv",
            "worker venv",
            venv_py.is_file() and os.access(venv_py, os.X_OK),
            str(venv_py),
        ),
        CheckItem(
            "weights",
            "MatAnyone2 weights",
            weight.is_file(),
            str(weight),
        ),
    ]
    legacy = legacy_uv_path()
    if legacy.is_file():
        items.append(
            CheckItem(
                "legacy_uv",
                "Legacy ~/.local/bin/uv",
                True,
                "Present (Embr prefers ~/Embr/bin/uv; optional cleanup)",
            )
        )
    return RuntimeStatus(
        home=root,
        items=tuple(items),
        channel=chosen,
        local_sha=local_sha,
        remote_sha=remote_sha,
        update_available=update_available,
        sync_error=sync_error,
    )


def ensure_layout(home: Path | None = None) -> Path:
    """Create ``bin/ ml/ tools/ repos/ venvs/`` under ``EMBR_HOME``."""
    root = (home or embr_home()).expanduser().resolve()
    for name in ("bin", "ml", "tools", "repos", "venvs"):
        (root / name).mkdir(parents=True, exist_ok=True)
    readme = root / "README.md"
    if not readme.is_file():
        readme.write_text(
            "# Embr runtime\n\n"
            "AI / PyBox data and tools. Distinct from Flame hooks "
            "(`…/python/Embr/`).\n"
            "Uninstall: `rm -rf` this directory (and optional `~/embr-ml`).\n",
            encoding="utf-8",
        )
    return root


def _run(
    cmd: list[str],
    *,
    log: LogFn | None = None,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> None:
    _log(log, "$ " + " ".join(cmd))
    merged = os.environ.copy()
    if env:
        merged.update(env)
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=merged,
        text=True,
        capture_output=True,
    )
    out_lines = []
    if proc.stdout:
        out_lines.extend(proc.stdout.splitlines())
    if proc.stderr:
        out_lines.extend(proc.stderr.splitlines())
    for line in out_lines:
        _log(log, line)
    if proc.returncode != 0:
        tail = "\n".join(out_lines[-25:]) if out_lines else "(no output)"
        raise EmbrRuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{tail}"
        )


def install_uv(home: Path | None = None, *, log: LogFn | None = None) -> Path:
    """Install Astral uv into ``$EMBR_HOME/bin`` (not ``~/.local``)."""
    root = ensure_layout(home)
    uv = embr_uv_path(root)
    if uv.is_file() and os.access(uv, os.X_OK):
        _log(log, f"uv already present: {uv}")
        return uv

    if shutil.which("curl") is None:
        raise EmbrRuntimeError("curl is required to install uv")

    bin_dir = root / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    _log(log, f"Installing uv into {bin_dir} …")
    env = os.environ.copy()
    env["UV_INSTALL_DIR"] = str(bin_dir)
    proc = subprocess.run(
        "curl -LsSf https://astral.sh/uv/install.sh | sh",
        shell=True,
        env=env,
        text=True,
        capture_output=True,
    )
    if proc.stdout:
        for line in proc.stdout.splitlines():
            _log(log, line)
    if proc.stderr:
        for line in proc.stderr.splitlines():
            _log(log, line)
    if proc.returncode != 0 or not (uv.is_file() and os.access(uv, os.X_OK)):
        raise EmbrRuntimeError(f"uv install failed; expected executable at {uv}")
    _log(log, f"uv ready: {uv}")
    return uv


def ensure_handlers_repo(
    home: Path | None = None,
    *,
    channel: str | None = None,
    update: bool = False,
    log: LogFn | None = None,
) -> Path:
    """Clone or optionally update ``embr-pybox-handlers`` under ``repos/``."""
    root = ensure_layout(home)
    chosen = normalize_channel(channel if channel is not None else get_channel(root))
    ref = channel_ref(chosen)
    set_channel(root, chosen)
    repo = handlers_repo_path(root)
    if repo.is_dir() and (repo / ".git").is_dir():
        if update:
            _log(log, f"Updating handlers repo ({chosen} → {ref}): {repo}")
            _run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "fetch",
                    "--depth",
                    "1",
                    "origin",
                    ref,
                ],
                log=log,
            )
            _run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "checkout",
                    "-B",
                    ref,
                    f"origin/{ref}",
                ],
                log=log,
            )
        else:
            _log(log, f"handlers repo present: {repo}")
        return repo

    if repo.exists():
        raise EmbrRuntimeError(f"Refusing to overwrite non-git path: {repo}")

    if shutil.which("git") is None:
        raise EmbrRuntimeError("git is required to clone embr-pybox-handlers")

    repo.parent.mkdir(parents=True, exist_ok=True)
    _log(log, f"Cloning {HANDLERS_REPO_URL} ({chosen} / {ref}) → {repo}")
    _run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            ref,
            HANDLERS_REPO_URL,
            str(repo),
        ],
        log=log,
    )
    return repo


def find_autodesk_python3() -> Path | None:
    """Newest ``/opt/Autodesk/python/<ver>/bin/python3``, if present."""
    override = os.environ.get("FLAME_PYTHON", "").strip()
    if override:
        path = Path(override).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return path.resolve()

    base = Path(os.environ.get("FLAME_PYTHON_ROOT", "/opt/Autodesk/python"))
    if not base.is_dir():
        return None

    newest: Path | None = None
    newest_key: tuple[int, ...] = ()
    for child in base.iterdir():
        if not child.is_dir():
            continue
        py = child / "bin" / "python3"
        if not (py.is_file() and os.access(py, os.X_OK)):
            continue
        parts: list[int] = []
        for token in child.name.split("."):
            if token.isdigit():
                parts.append(int(token))
            else:
                break
        key = tuple(parts) if parts else (0,)
        if newest is None or key >= newest_key:
            newest = py
            newest_key = key
    return newest.resolve() if newest is not None else None


def _python_version_tuple(executable: Path) -> tuple[int, int] | None:
    try:
        proc = subprocess.run(
            [
                str(executable),
                "-c",
                "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')",
            ],
            text=True,
            capture_output=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    text = (proc.stdout or "").strip()
    try:
        major_s, minor_s = text.split(".", 1)
        return int(major_s), int(minor_s)
    except ValueError:
        return None


def bootstrap_command(
    *,
    repo: Path,
    ml: Path,
    home: Path,
    log: LogFn | None = None,
) -> tuple[list[str], Path | None]:
    """Build ``(argv, cwd)`` to run ``python -m embr_ml.bootstrap``.

    Running ``…/embr_ml/bootstrap.py`` as a file fails with
    ``ModuleNotFoundError: embr_ml``. Prefer Embr ``uv run`` with
    ``--directory worker``, else Autodesk / modern python with ``cwd=worker``.
    """
    worker = repo / "worker"
    if not (worker / "embr_ml" / "bootstrap.py").is_file():
        raise EmbrRuntimeError(f"bootstrap package missing under {worker}")

    module_args = [
        "-m",
        "embr_ml.bootstrap",
        "--repo-root",
        str(repo),
        "--ml-root",
        str(ml),
    ]
    uv = embr_uv_path(home)
    if uv.is_file() and os.access(uv, os.X_OK):
        _log(log, f"bootstrap via uv ({uv}) --python 3.10 -m embr_ml.bootstrap")
        return (
            [
                str(uv),
                "run",
                "--python",
                "3.10",
                "--directory",
                str(worker),
                *module_args,
            ],
            None,
        )

    for label, candidate in (
        ("Autodesk python", find_autodesk_python3()),
        ("sys.executable", Path(sys.executable)),
    ):
        if candidate is None:
            continue
        ver = _python_version_tuple(candidate)
        if ver is None:
            _log(log, f"skip {label}: cannot read version ({candidate})")
            continue
        if ver < (3, 10):
            _log(
                log,
                f"skip {label}: Python {ver[0]}.{ver[1]} < 3.10 ({candidate})",
            )
            continue
        _log(log, f"bootstrap via {label}: {candidate} ({ver[0]}.{ver[1]})")
        return [str(candidate), *module_args], worker

    raise EmbrRuntimeError(
        "Need Python 3.10+ (or Embr uv) to run PyBox bootstrap. "
        "Install failed because the current interpreter is too old "
        f"(sys.executable={sys.executable!r})."
    )


def run_bootstrap(
    home: Path | None = None,
    *,
    log: LogFn | None = None,
) -> None:
    """Run handlers ``embr_ml.bootstrap`` with Embr-local uv on ``PATH``."""
    root = (home or embr_home()).expanduser().resolve()
    repo = handlers_repo_path(root)
    bootstrap = repo / "worker" / "embr_ml" / "bootstrap.py"
    if not bootstrap.is_file():
        raise EmbrRuntimeError(f"bootstrap.py missing: {bootstrap}")

    uv = embr_uv_path(root)
    ml = embr_ml_root(root)
    ml.mkdir(parents=True, exist_ok=True)

    env = {
        "EMBR_HOME": str(root),
        "EMBR_ML_ROOT": str(ml),
        "EMBR_UV": str(uv),
        "PATH": f"{root / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}",
        "UV_INSTALL_DIR": str(root / "bin"),
    }
    cmd, cwd = bootstrap_command(repo=repo, ml=ml, home=root, log=log)
    _log(log, "Running worker bootstrap (may take several minutes)…")
    _run(cmd, log=log, env=env, cwd=cwd)


def install_or_update_runtime(
    home: Path | None = None,
    *,
    channel: str | None = None,
    update_repo: bool = True,
    log: LogFn | None = None,
) -> RuntimeStatus:
    """Full Install / Update: layout → uv → clone/pull → bootstrap."""
    root = ensure_layout(home)
    chosen = set_channel(root, channel if channel is not None else get_channel(root))
    _log(log, f"EMBR_HOME={root}")
    _log(log, f"channel={chosen} (ref={channel_ref(chosen)})")
    install_uv(root, log=log)
    ensure_handlers_repo(root, channel=chosen, update=update_repo, log=log)
    run_bootstrap(root, log=log)
    status = probe_status(root, channel=chosen, check_remote=True)
    if status.update_available:
        _log(log, "Warning: still behind remote after update.")
    _log(log, f"Done — {status.ok_count}/{len(status.items)} checks OK.")
    return status


def repair_runtime(
    home: Path | None = None,
    *,
    channel: str | None = None,
    log: LogFn | None = None,
) -> RuntimeStatus:
    """Repair: ensure uv + repo, recreate bootstrap (venv if broken)."""
    root = ensure_layout(home)
    chosen = set_channel(root, channel if channel is not None else get_channel(root))
    install_uv(root, log=log)
    ensure_handlers_repo(root, channel=chosen, update=False, log=log)
    venv = handlers_repo_path(root) / "worker" / ".venv"
    if venv.is_dir() and not worker_venv_python(root).is_file():
        _log(log, f"Removing broken venv: {venv}")
        shutil.rmtree(venv, ignore_errors=True)
    run_bootstrap(root, log=log)
    return probe_status(root, channel=chosen, check_remote=True)


def uninstall_runtime(
    home: Path | None = None,
    *,
    remove_legacy_symlink: bool = True,
    log: LogFn | None = None,
) -> None:
    """Remove ``$EMBR_HOME`` (and optional ``~/embr-ml`` symlink).

    Does **not** remove Flame hooks under ``…/python/Embr/``.
    """
    root = home or embr_home()
    if root.is_dir():
        _log(log, f"Removing {root}")
        shutil.rmtree(root)
    else:
        _log(log, f"Already absent: {root}")

    if remove_legacy_symlink:
        link = legacy_ml_symlink()
        if link.is_symlink() or link.exists():
            _log(log, f"Removing {link}")
            link.unlink(missing_ok=True)
