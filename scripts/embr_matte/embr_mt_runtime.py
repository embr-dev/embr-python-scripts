"""Embr Matte — AI runtime gate (probe + Install via embr_runtime)."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QThread, Signal
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


def matte_compact(status: runtime.RuntimeStatus) -> str:
    """Short one-line label for the runtime bar (not the footer)."""
    ch = status.channel
    by_id = {item.id: item for item in status.items}
    if matte_ready(status):
        detail = (by_id.get("matte").detail if by_id.get("matte") else "") or "ok"
        device = detail
        if "(" in detail and detail.endswith(")"):
            device = detail[detail.rfind("(") + 1 : -1].strip() or detail
        return f"Ready · {device} · {ch}"

    missing = [
        by_id[cid].label
        for cid in _MATTE_CHECK_IDS
        if cid in by_id and not by_id[cid].ok
    ]
    if not missing:
        return f"Need Install · {ch}"
    if len(missing) == 1:
        return f"Need Install · {missing[0]} · {ch}"
    return f"Need Install · {len(missing)} checks · {ch}"


# Back-compat alias for callers/docs.
def matte_summary(status: runtime.RuntimeStatus) -> str:
    return matte_compact(status)


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
    """One-line runtime probe + Install; log only while installing."""

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
        self._summary = QLabel("Checking…")
        self._summary.setObjectName("embrMuted")
        self._summary.setWordWrap(False)
        self._summary.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        row.addWidget(self._summary, 1)

        self._btn_check = QPushButton("Check")
        self._btn_install = QPushButton("Install")
        for btn in (self._btn_check, self._btn_install):
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        row.addWidget(self._btn_check)
        row.addWidget(self._btn_install)
        root.addLayout(row)

        self._log = QPlainTextEdit()
        self._log.setObjectName("embrLog")
        self._log.setReadOnly(True)
        self._log.setMaximumBlockCount(4000)
        self._log.setPlaceholderText("Install log…")
        self._log.setMaximumHeight(120)
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
        self._update_install_style()

    @property
    def ready(self) -> bool:
        return self._ready

    def _set_status(self, text: str) -> None:
        if self._set_status_fn is not None:
            self._set_status_fn(text)

    def _update_install_style(self) -> None:
        # Accent only when runtime is not ready (Add owns accent otherwise).
        if self._ready:
            self._btn_install.setObjectName("")
        else:
            self._btn_install.setObjectName("embrAccent")
        style = self._btn_install.style()
        if style is not None:
            style.unpolish(self._btn_install)
            style.polish(self._btn_install)
        self._btn_install.update()

    def refresh(self, *, check_remote: bool = False) -> None:
        if self._busy:
            return
        self._channel = runtime.get_channel()
        self._set_status(f"Checking runtime (“{self._channel}”)…")
        try:
            status = runtime.probe_status(
                channel=self._channel, check_remote=check_remote
            )
        except Exception as exc:
            self._summary.setText(f"Check failed: {exc}")
            self._summary.setStyleSheet("")
            self._ready = False
            self._update_install_style()
            self.readiness_changed.emit(False)
            self._set_status("Runtime check failed.")
            return
        self._apply_status(status)
        home = status.home
        ml = runtime.embr_ml_root(status.home)
        self._summary.setToolTip(f"{home}\nml {ml}")

    def _apply_status(self, status: runtime.RuntimeStatus) -> None:
        self._last_status = status
        self._channel = status.channel
        self._ready = matte_ready(status)
        self._summary.setText(matte_compact(status))
        if self._ready:
            self._summary.setStyleSheet(f"color: {embr_ui.EMBR_EMBER};")
        else:
            self._summary.setStyleSheet("")
        self._update_install_style()
        self.readiness_changed.emit(self._ready)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self._btn_check.setEnabled(not busy)
        self._btn_install.setEnabled(not busy)

    def _show_log(self, visible: bool) -> None:
        self._log.setVisible(visible)

    def _append_log(self, line: str) -> None:
        if not self._log.isVisible():
            self._show_log(True)
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
        self._show_log(True)
        self._set_busy(True)
        self._set_status(f"Installing runtime (“{self._channel}”)…")

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
        else:
            self.refresh(check_remote=False)
        self._show_log(False)
        self._log.clear()
        if self._ready:
            self._set_status("Runtime ready.")
        else:
            self._show_log(True)
            self._set_status(
                "Install finished but checks incomplete — see log."
            )

    def _on_install_failed(self, message: str) -> None:
        self._append_log(f"ERROR: {message}")
        self._show_log(True)
        try:
            status = runtime.probe_status(
                channel=self._channel, check_remote=False
            )
            self._apply_status(status)
        except Exception:
            self._ready = False
            self._update_install_style()
            self.readiness_changed.emit(False)
        box = QMessageBox(None)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle("Embr Matte")
        box.setText(f"Runtime Install failed:\n{message}")
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()
        self._set_status("Runtime Install failed.")
