"""Embr Matte — AI runtime gate (probe + Install via embr_runtime)."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import embr_runtime as runtime
import embr_ui as embr_ui

StatusFn = Callable[[str], None]

# Checks Matte needs before SAM2 / MatAnyone2 work.
_MATTE_CHECK_IDS = ("home", "uv", "venv", "media", "matte", "weights")


def matte_ready(status: runtime.RuntimeStatus) -> bool:
    by_id = {item.id: item for item in status.items}
    return all(by_id.get(cid) and by_id[cid].ok for cid in _MATTE_CHECK_IDS)


def matte_summary(status: runtime.RuntimeStatus) -> str:
    """One-line status for the Matte runtime bar."""
    ch = status.channel
    by_id = {item.id: item for item in status.items}
    if matte_ready(status):
        matte = by_id.get("matte")
        detail = matte.detail if matte else "ok"
        return f"Runtime ready — {detail} · channel “{ch}”"

    missing = [
        by_id[cid].label
        for cid in _MATTE_CHECK_IDS
        if cid in by_id and not by_id[cid].ok
    ]
    if not missing:
        missing = ["runtime"]
    return (
        f"Runtime incomplete — missing: {', '.join(missing)} · "
        f"channel “{ch}”. Use Install."
    )


class _InstallWorker(QObject):
    log_line = Signal(str)
    finished_ok = Signal(object)  # RuntimeStatus
    failed = Signal(str)

    def __init__(self, channel: str) -> None:
        super().__init__()
        self._channel = channel

    def run(self) -> None:
        def log(message: str) -> None:
            self.log_line.emit(message)

        try:
            status = runtime.install_or_update_runtime(
                channel=self._channel, log=log
            )
            self.finished_ok.emit(status)
        except Exception as exc:
            self.failed.emit(str(exc))


class RuntimePanel(QWidget):
    """Compact runtime probe + Install for Embr Matte."""

    readiness_changed = Signal(bool)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        set_status: StatusFn | None = None,
    ) -> None:
        super().__init__(parent)
        self._set_status_fn = set_status
        self._busy = False
        self._thread: QThread | None = None
        self._worker: _InstallWorker | None = None
        self._channel = runtime.get_channel()
        self._last_status: runtime.RuntimeStatus | None = None
        self._ready = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(embr_ui.EMBR_SPACE_1)

        row = QHBoxLayout()
        row.setSpacing(embr_ui.EMBR_SPACE_2)
        self._summary = QLabel("Checking runtime…")
        self._summary.setObjectName("embrMuted")
        self._summary.setWordWrap(True)
        self._summary.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        row.addWidget(self._summary, 1)

        self._btn_check = QPushButton("Check")
        self._btn_install = QPushButton("Install")
        self._btn_install.setObjectName("embrAccent")
        for btn in (self._btn_check, self._btn_install):
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        row.addWidget(self._btn_check)
        row.addWidget(self._btn_install)
        root.addLayout(row)

        self._home = QLabel()
        self._home.setObjectName("embrMuted")
        self._home.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        root.addWidget(self._home)

        self._log = QPlainTextEdit()
        self._log.setObjectName("embrLog")
        self._log.setReadOnly(True)
        self._log.setMaximumBlockCount(4000)
        self._log.setPlaceholderText("Install log…")
        self._log.setMaximumHeight(140)
        self._log.setVisible(False)
        mono = QFont("Menlo")
        mono.setStyleHint(QFont.StyleHint.Monospace)
        mono.setPointSize(11)
        self._log.setFont(mono)
        self._log.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        root.addWidget(self._log)

        self._btn_check.clicked.connect(self.refresh)
        self._btn_install.clicked.connect(self._start_install)

    @property
    def ready(self) -> bool:
        return self._ready

    def _set_status(self, text: str) -> None:
        if self._set_status_fn is not None:
            self._set_status_fn(text)

    def refresh(self, *, check_remote: bool = False) -> None:
        if self._busy:
            return
        self._channel = runtime.get_channel()
        self._set_status(f"Checking Matte runtime (channel “{self._channel}”)…")
        try:
            status = runtime.probe_status(
                channel=self._channel, check_remote=check_remote
            )
        except Exception as exc:
            self._summary.setText(f"Runtime check failed: {exc}")
            self._ready = False
            self.readiness_changed.emit(False)
            self._set_status("Runtime check failed.")
            return
        self._apply_status(status)

    def _apply_status(self, status: runtime.RuntimeStatus) -> None:
        self._last_status = status
        self._channel = status.channel
        self._ready = matte_ready(status)
        self._summary.setText(matte_summary(status))
        self._home.setText(f"{status.home}  ·  ml {runtime.embr_ml_root(status.home)}")
        if self._ready:
            self._summary.setStyleSheet(f"color: {embr_ui.EMBR_EMBER};")
        else:
            self._summary.setStyleSheet("")
        self.readiness_changed.emit(self._ready)
        self._set_status(matte_summary(status))

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self._btn_check.setEnabled(not busy)
        self._btn_install.setEnabled(not busy)

    def _append_log(self, line: str) -> None:
        if not self._log.isVisible():
            self._log.setVisible(True)
        self._log.appendPlainText(line)

    def _start_install(self) -> None:
        if self._busy:
            return
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle("Embr Matte")
        box.setText(
            "Install / Update the AI runtime under EMBR_HOME?\n\n"
            "This installs uv, handlers, worker venv, media deps, "
            "torch, and MatAnyone2 (S-Lab non-commercial). "
            "First Install may take a long time and needs network."
        )
        box.setStandardButtons(
            QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes
        )
        box.setDefaultButton(QMessageBox.StandardButton.Cancel)
        if box.exec() != QMessageBox.StandardButton.Yes:
            return

        self._channel = runtime.get_channel()
        self._log.clear()
        self._log.setVisible(True)
        self._set_busy(True)
        self._set_status(
            f"Installing Matte runtime (channel “{self._channel}”)…"
        )

        thread = QThread(self)
        worker = _InstallWorker(self._channel)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.log_line.connect(self._append_log)
        worker.finished_ok.connect(self._on_install_ok)
        worker.failed.connect(self._on_install_failed)
        worker.finished_ok.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_thread)
        self._thread = thread
        self._worker = worker
        thread.start()

    def _clear_thread(self) -> None:
        self._thread = None
        self._worker = None
        self._set_busy(False)

    def _on_install_ok(self, status: object) -> None:
        if isinstance(status, runtime.RuntimeStatus):
            self._apply_status(status)
            self._append_log(
                f"Done — {status.ok_count}/{len(status.items)} checks OK."
            )
        else:
            self.refresh(check_remote=False)
        if self._ready:
            self._set_status("Matte runtime ready.")
        else:
            self._set_status(
                "Install finished but Matte checks are still incomplete. "
                "See the log / Check again."
            )

    def _on_install_failed(self, message: str) -> None:
        self._append_log(f"ERROR: {message}")
        self.refresh(check_remote=False)
        box = QMessageBox(None)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle("Embr Matte")
        box.setText(f"Runtime Install failed:\n{message}")
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()
        self._set_status("Runtime Install failed.")
