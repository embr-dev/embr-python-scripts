"""Embr Manager — PyBox tab (AI / PyBox runtime under ``~/Embr``)."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
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

    def __init__(self, action: str, channel: str) -> None:
        super().__init__()
        self._action = action
        self._channel = channel

    def run(self) -> None:
        def log(message: str) -> None:
            self.log_line.emit(message)

        try:
            if self._action == "install":
                status = runtime.install_or_update_runtime(
                    channel=self._channel, log=log
                )
            elif self._action == "repair":
                status = runtime.repair_runtime(channel=self._channel, log=log)
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
        self._channel = runtime.get_channel()
        self._last_status: runtime.RuntimeStatus | None = None

        body = QVBoxLayout(self)
        body.setContentsMargins(
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
        )
        body.setSpacing(embr_ui.EMBR_SPACE_2)

        meta = QHBoxLayout()
        self._home_label = QLabel()
        self._home_label.setObjectName("embrRoot")
        self._home_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        meta.addWidget(self._home_label, 1)

        meta.addWidget(QLabel("Channel:"))
        self._channel_combo = QComboBox()
        self._channel_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        for name in runtime.CHANNEL_ORDER:
            self._channel_combo.addItem(name, name)
        idx = self._channel_combo.findData(self._channel)
        if idx < 0:
            idx = self._channel_combo.findData(runtime.DEFAULT_CHANNEL)
        self._channel_combo.setCurrentIndex(max(0, idx))
        self._channel_combo.currentIndexChanged.connect(self._on_channel_changed)
        meta.addWidget(self._channel_combo)
        body.addLayout(meta)

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

    def _on_channel_changed(self, _index: int) -> None:
        if self._busy:
            return
        data = self._channel_combo.currentData()
        if data is None:
            return
        self._channel = runtime.set_channel(channel=str(data))
        self.refresh()

    def refresh(self) -> None:
        if self._busy:
            return
        self._set_status(f"Checking handlers on channel “{self._channel}”…")
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QEventLoop

        app = QApplication.instance()
        if app is not None:
            app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
        self._apply_status(
            runtime.probe_status(channel=self._channel, check_remote=True)
        )

    def _apply_status(self, status: runtime.RuntimeStatus) -> None:
        self._last_status = status
        self._home_label.setText(f"Runtime: {status.home}")
        self._rebuild_checks(status)
        self._set_status(self._idle_status(status))

    def _idle_status(self, status: runtime.RuntimeStatus | None = None) -> str:
        status = status or self._last_status or runtime.probe_status(
            channel=self._channel, check_remote=False
        )
        n = len(status.items)
        ok = status.ok_count
        ch = status.channel
        if status.sync_error and not status.remote_sha:
            return (
                f"Channel “{ch}” — {status.sync_error}. "
                "Pick another channel or fix network, then Refresh."
            )
        if status.update_available and status.local_sha and status.remote_sha:
            return (
                f"Update available on channel “{ch}” "
                f"({status.local_sha[:7]} → {status.remote_sha[:7]}). "
                "Use Install / Update."
            )
        if status.all_ok:
            return f"PyBox runtime ready — channel “{ch}”, {ok}/{n} checks OK."
        if ok == 0:
            return (
                f"PyBox runtime not installed — channel “{ch}”. "
                "Use Install / Update."
            )
        return (
            f"PyBox runtime incomplete — channel “{ch}”, {ok}/{n} checks OK. "
            "Use Install / Update or Repair."
        )

    def _rebuild_checks(self, status: runtime.RuntimeStatus) -> None:
        while self._checks.count():
            item = self._checks.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._check_labels.clear()

        for check in status.items:
            row = QHBoxLayout()
            mark_text = check.mark or ("OK" if check.ok else "—")
            mark = QLabel(mark_text)
            mark.setFixedWidth(36)
            if mark_text == "UPD":
                mark.setStyleSheet(
                    f"color: {embr_ui.EMBR_EMBER}; font-weight: 700;"
                )
            elif check.ok or mark_text == "OK":
                mark.setStyleSheet(
                    f"color: {embr_ui.EMBR_EMBER}; font-weight: 600;"
                )
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
        self._channel_combo.setEnabled(not busy)
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
            "install": f"Installing / updating PyBox runtime ({self._channel})…",
            "repair": f"Repairing PyBox runtime ({self._channel})…",
            "uninstall": "Uninstalling PyBox runtime…",
        }
        self._log.clear()
        self._set_busy(True, labels.get(action, "Working…"))
        self._append_log(f"— {action} / channel {self._channel} —")

        thread = QThread(self)
        worker = _RuntimeWorker(action, self._channel)
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
            self._apply_status(
                runtime.probe_status(channel=self._channel, check_remote=False)
            )
            self._set_status("PyBox runtime uninstalled.")
            self._append_log("Uninstall finished.")

    def _on_failed(self, message: str) -> None:
        self._append_log(f"ERROR: {message}")
        self._alert(f"PyBox runtime action failed:\n{message}")
        self._apply_status(
            runtime.probe_status(channel=self._channel, check_remote=True)
        )
        self._set_status("PyBox runtime action failed. See the log.")

    def _on_thread_finished(self) -> None:
        self._thread = None
        self._worker = None
        self._set_busy(False)
