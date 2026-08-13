"""Embr Manager — PyBox tab (AI / PyBox runtime under ``~/Embr``)."""

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


class _RuntimeWorker(QObject):
    """Runs install / repair / uninstall off the UI thread."""

    log_line = Signal(str)
    finished_ok = Signal(object)  # RuntimeStatus | None
    failed = Signal(str)

    def __init__(self, action: str) -> None:
        super().__init__()
        self._action = action

    def run(self) -> None:
        def log(message: str) -> None:
            self.log_line.emit(message)

        try:
            if self._action == "install":
                status = runtime.install_or_update_runtime(log=log)
            elif self._action == "repair":
                status = runtime.repair_runtime(log=log)
            elif self._action == "uninstall":
                runtime.uninstall_runtime(log=log)
                status = None
            else:
                raise runtime.EmbrRuntimeError(f"Unknown action: {self._action}")
            self.finished_ok.emit(status)
        except Exception as exc:
            self.failed.emit(str(exc))


class PyBoxTab(QWidget):
    """Runtime checklist + Install / Repair / Uninstall for ``$EMBR_HOME``."""

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
        self._worker: _RuntimeWorker | None = None
        self._check_labels: dict[str, QLabel] = {}

        body = QVBoxLayout(self)
        body.setContentsMargins(
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
        )
        body.setSpacing(embr_ui.EMBR_SPACE_2)

        self._home_label = QLabel()
        self._home_label.setObjectName("embrRoot")
        self._home_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        body.addWidget(self._home_label)

        note = QLabel(
            "PyBox / AI runtime (uv, handlers, venv, weights). "
            "Separate from Flame scripts under python/Embr/."
        )
        note.setObjectName("embrMuted")
        note.setWordWrap(True)
        body.addWidget(note)

        self._checks = QVBoxLayout()
        self._checks.setSpacing(embr_ui.EMBR_SPACE_1)
        body.addLayout(self._checks)

        license_note = QLabel(
            "MatAnyone2 weights follow S-Lab non-commercial terms — "
            "confirm studio policy before Install."
        )
        license_note.setObjectName("embrMuted")
        license_note.setWordWrap(True)
        body.addWidget(license_note)

        self._log = QPlainTextEdit()
        self._log.setObjectName("embrLog")
        self._log.setReadOnly(True)
        self._log.setMaximumBlockCount(4000)
        self._log.setPlaceholderText("Install / Repair log…")
        mono = QFont("Menlo")
        mono.setStyleHint(QFont.StyleHint.Monospace)
        mono.setPointSize(11)
        self._log.setFont(mono)
        self._log.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        body.addWidget(self._log, 1)

        buttons = QHBoxLayout()
        self._btn_refresh = QPushButton("Refresh")
        self._btn_install = QPushButton("Install / Update")
        self._btn_install.setObjectName("embrAccent")
        self._btn_repair = QPushButton("Repair")
        self._btn_uninstall = QPushButton("Uninstall")
        for btn in (
            self._btn_refresh,
            self._btn_install,
            self._btn_repair,
            self._btn_uninstall,
        ):
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        buttons.addWidget(self._btn_refresh)
        buttons.addStretch(1)
        buttons.addWidget(self._btn_uninstall)
        buttons.addWidget(self._btn_repair)
        buttons.addWidget(self._btn_install)
        body.addLayout(buttons)

        self._btn_refresh.clicked.connect(self.refresh)
        self._btn_install.clicked.connect(lambda: self._start("install"))
        self._btn_repair.clicked.connect(lambda: self._start("repair"))
        self._btn_uninstall.clicked.connect(self._confirm_uninstall)

    def activate(self) -> None:
        """Called when the PyBox tab is shown."""
        self.refresh()

    def _host_window(self) -> QWidget | None:
        win = self.window()
        return win if win is not None and win is not self else None

    def _set_status(self, text: str) -> None:
        if self._set_status_fn is not None:
            self._set_status_fn(text)

    def _append_log(self, line: str) -> None:
        self._log.appendPlainText(line)

    def refresh(self) -> None:
        if self._busy:
            return
        self._apply_status(runtime.probe_status())

    def _apply_status(self, status: runtime.RuntimeStatus) -> None:
        self._home_label.setText(f"Runtime: {status.home}")
        self._rebuild_checks(status)
        self._set_status(self._idle_status(status))

    def _idle_status(self, status: runtime.RuntimeStatus | None = None) -> str:
        status = status or runtime.probe_status()
        n = len(status.items)
        ok = status.ok_count
        if status.all_ok:
            return f"PyBox runtime ready — {ok}/{n} checks OK."
        if ok == 0:
            return f"PyBox runtime not installed — {ok}/{n} checks OK. Use Install / Update."
        return f"PyBox runtime incomplete — {ok}/{n} checks OK. Use Install / Update or Repair."

    def _rebuild_checks(self, status: runtime.RuntimeStatus) -> None:
        while self._checks.count():
            item = self._checks.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._check_labels.clear()

        for check in status.items:
            row = QHBoxLayout()
            mark = QLabel("OK" if check.ok else "—")
            mark.setFixedWidth(28)
            mark.setObjectName("embrMuted" if not check.ok else "embrBrand")
            if check.ok:
                mark.setStyleSheet(f"color: {embr_ui.EMBR_EMBER}; font-weight: 600;")
            else:
                mark.setStyleSheet(f"color: {embr_ui.EMBR_MUTED};")
            label = QLabel(check.label)
            detail = QLabel(check.detail)
            detail.setObjectName("embrMuted")
            detail.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            detail.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
            )
            row.addWidget(mark)
            row.addWidget(label)
            row.addWidget(detail, 1)
            wrap = QWidget()
            wrap.setLayout(row)
            self._checks.addWidget(wrap)
            self._check_labels[check.id] = mark

    def _set_busy(self, busy: bool, message: str | None = None) -> None:
        self._busy = busy
        for btn in (
            self._btn_refresh,
            self._btn_install,
            self._btn_repair,
            self._btn_uninstall,
        ):
            btn.setEnabled(not busy)
        if message:
            self._set_status(message)

    def _alert(self, text: str, *, critical: bool = True) -> None:
        host = self._host_window()
        geo = host.geometry() if host is not None else None
        box = QMessageBox(None)
        box.setIcon(
            QMessageBox.Icon.Critical if critical else QMessageBox.Icon.Information
        )
        box.setWindowTitle("Embr Manager")
        box.setText(text)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()
        if host is not None and geo is not None and not host.isMaximized():
            host.setGeometry(geo)

    def _confirm_uninstall(self) -> None:
        if self._busy:
            return
        home = runtime.embr_home()
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Embr Manager")
        box.setText(
            f"Remove the PyBox / AI runtime at:\n{home}\n\n"
            "This deletes uv, the handlers clone, venv, and weights under "
            "EMBR_HOME. Flame scripts under python/Embr/ are not touched."
        )
        box.setStandardButtons(
            QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes
        )
        box.setDefaultButton(QMessageBox.StandardButton.Cancel)
        if box.exec() != QMessageBox.StandardButton.Yes:
            return
        self._start("uninstall")

    def _start(self, action: str) -> None:
        if self._busy:
            return
        labels = {
            "install": "Installing / updating PyBox runtime…",
            "repair": "Repairing PyBox runtime…",
            "uninstall": "Uninstalling PyBox runtime…",
        }
        self._log.clear()
        self._set_busy(True, labels.get(action, "Working…"))
        self._append_log(f"— {action} —")

        thread = QThread(self)
        worker = _RuntimeWorker(action)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.log_line.connect(self._append_log)
        worker.finished_ok.connect(self._on_finished_ok)
        worker.failed.connect(self._on_failed)
        worker.finished_ok.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_thread_finished)
        self._thread = thread
        self._worker = worker
        thread.start()

    def _on_finished_ok(self, status: object) -> None:
        if isinstance(status, runtime.RuntimeStatus):
            self._apply_status(status)
            self._append_log(
                f"Finished — {status.ok_count}/{len(status.items)} checks OK."
            )
        else:
            self._apply_status(runtime.probe_status())
            self._set_status("PyBox runtime uninstalled.")
            self._append_log("Uninstall finished.")

    def _on_failed(self, message: str) -> None:
        self._append_log(f"ERROR: {message}")
        self._alert(f"PyBox runtime action failed:\n{message}")
        self._apply_status(runtime.probe_status())
        self._set_status("PyBox runtime action failed. See the log.")

    def _on_thread_finished(self) -> None:
        self._thread = None
        self._worker = None
        self._set_busy(False)
