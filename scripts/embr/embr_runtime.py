"""Embr AI / PyBox runtime under ``$EMBR_HOME`` (default ``~/Embr``).

Distinct from Flame hooks install root (``…/python/Embr/``). See
``docs/ai-runtime.md`` and embr-pybox-handlers handoff.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

LogFn = Callable[[str], None]

HANDLERS_REPO_URL = "https://github.com/embr-dev/embr-pybox-handlers.git"
HANDLERS_REPO_REF = "dev"
HANDLERS_DIR_NAME = "embr-pybox-handlers"


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


@dataclass(frozen=True)
class CheckItem:
    id: str
    label: str
    ok: bool
    detail: str = ""


@dataclass(frozen=True)
class RuntimeStatus:
    home: Path
    items: tuple[CheckItem, ...]

    @property
    def ok_count(self) -> int:
        return sum(1 for i in self.items if i.ok)

    @property
    def all_ok(self) -> bool:
        return bool(self.items) and all(i.ok for i in self.items)


def probe_status(home: Path | None = None) -> RuntimeStatus:
    """Return checklist for the PyBox / AI runtime."""
    root = (home or embr_home()).expanduser().resolve()
    uv = embr_uv_path(root)
    repo = handlers_repo_path(root)
    venv_py = worker_venv_python(root)
    weight = matanyone_weight_path(root)
    bootstrap = repo / "worker" / "embr_ml" / "bootstrap.py"

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
            repo.is_dir() and (repo / "handlers").is_dir(),
            str(repo),
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
    return RuntimeStatus(home=root, items=tuple(items))


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
    update: bool = False,
    log: LogFn | None = None,
) -> Path:
    """Clone or optionally update ``embr-pybox-handlers`` under ``repos/``."""
    root = ensure_layout(home)
    repo = handlers_repo_path(root)
    if repo.is_dir() and (repo / ".git").is_dir():
        if update:
            _log(log, f"Updating handlers repo: {repo}")
            _run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "fetch",
                    "--depth",
                    "1",
                    "origin",
                    HANDLERS_REPO_REF,
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
                    HANDLERS_REPO_REF,
                    f"origin/{HANDLERS_REPO_REF}",
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
    _log(log, f"Cloning {HANDLERS_REPO_URL} ({HANDLERS_REPO_REF}) → {repo}")
    _run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            HANDLERS_REPO_REF,
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
    update_repo: bool = True,
    log: LogFn | None = None,
) -> RuntimeStatus:
    """Full Install / Update: layout → uv → clone/pull → bootstrap."""
    root = ensure_layout(home)
    _log(log, f"EMBR_HOME={root}")
    install_uv(root, log=log)
    ensure_handlers_repo(root, update=update_repo, log=log)
    run_bootstrap(root, log=log)
    status = probe_status(root)
    _log(log, f"Done — {status.ok_count}/{len(status.items)} checks OK.")
    return status


def repair_runtime(
    home: Path | None = None,
    *,
    log: LogFn | None = None,
) -> RuntimeStatus:
    """Repair: ensure uv + repo, recreate bootstrap (venv if broken)."""
    root = ensure_layout(home)
    install_uv(root, log=log)
    ensure_handlers_repo(root, update=False, log=log)
    venv = handlers_repo_path(root) / "worker" / ".venv"
    if venv.is_dir() and not worker_venv_python(root).is_file():
        _log(log, f"Removing broken venv: {venv}")
        shutil.rmtree(venv, ignore_errors=True)
    run_bootstrap(root, log=log)
    return probe_status(root)


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
