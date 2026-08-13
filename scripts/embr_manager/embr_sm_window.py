"""Embr Manager window (PySide6) — tabbed hub; Scripts tab is the former Script Manager."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import embr_paths as paths
import embr_ui as embr_ui
import embr_sm_actions as actions
import embr_sm_bootstrap as bootstrap
import embr_sm_local as local
from embr_sm_catalog import (
    CHANNEL_ORDER,
    Catalog,
    CatalogError,
    fetch_catalog_for_channel,
    load_catalog_from_path,
    normalize_channel,
)

# Column indices
_COL_NAME = 0
_COL_STATUS = 1
_COL_LOCAL = 2
_COL_REMOTE = 3

_COL_STATUS_W = 140
_COL_VERSION_W = 88

StatusFn = Callable[[str], None]


class ScriptsTab(QWidget):
    """Scripts package list — install / update / repair / uninstall."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        root: Path,
        catalog_path: Path | None = None,
        source_root: Path | None = None,
        channel: str | None = None,
        set_status: StatusFn | None = None,
    ) -> None:
        super().__init__(parent)
        self._root = root.resolve()
        self._catalog_path = catalog_path
        self._source_root = source_root
        self._catalog: Catalog | None = None
        self._rows_by_id: dict[str, dict[str, str]] = {}
        self._busy = False
        self._set_status_fn = set_status
        if channel is not None:
            self._channel = normalize_channel(channel)
        else:
            self._channel = normalize_channel(local.get_channel(self._root))

        body = QVBoxLayout(self)
        body.setContentsMargins(
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
        )
        body.setSpacing(embr_ui.EMBR_SPACE_2)

        meta = QHBoxLayout()
        self._root_label = QLabel()
        self._root_label.setObjectName("embrRoot")
        meta.addWidget(self._root_label, 1)

        meta.addWidget(QLabel("Channel:"))
        self._channel_combo = QComboBox()
        self._channel_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        for name in CHANNEL_ORDER:
            self._channel_combo.addItem(name, name)
        idx = self._channel_combo.findData(self._channel)
        if idx < 0:
            idx = self._channel_combo.findData(local.DEFAULT_CHANNEL)
        self._channel_combo.setCurrentIndex(max(0, idx))
        if self._catalog_path is not None:
            self._channel_combo.setEnabled(False)
            self._channel_combo.setToolTip(
                "Using a local catalog file; channel fetch is disabled."
            )
        else:
            self._channel_combo.currentIndexChanged.connect(self._on_channel_changed)
        meta.addWidget(self._channel_combo)
        body.addLayout(meta)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Name", "Status", "Local", "Remote"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self._table.setAlternatingRowColors(True)
        self._table.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        header = self._table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(_COL_NAME, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(_COL_STATUS, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(_COL_LOCAL, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(_COL_REMOTE, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(_COL_STATUS, _COL_STATUS_W)
        self._table.setColumnWidth(_COL_LOCAL, _COL_VERSION_W)
        self._table.setColumnWidth(_COL_REMOTE, _COL_VERSION_W)
        body.addWidget(self._table, 1)

        buttons = QHBoxLayout()
        self._btn_refresh = QPushButton("Refresh")
        self._btn_install_update = QPushButton("Install / Update")
        self._btn_install_update.setObjectName("embrAccent")
        self._btn_repair = QPushButton("Repair")
        self._btn_uninstall = QPushButton("Uninstall")
        for btn in (
            self._btn_refresh,
            self._btn_install_update,
            self._btn_repair,
            self._btn_uninstall,
        ):
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        buttons.addWidget(self._btn_refresh)
        buttons.addStretch(1)
        buttons.addWidget(self._btn_uninstall)
        buttons.addWidget(self._btn_repair)
        buttons.addWidget(self._btn_install_update)
        body.addLayout(buttons)

        self._btn_refresh.clicked.connect(self.refresh)
        self._btn_install_update.clicked.connect(self._run_install_or_update)
        self._btn_repair.clicked.connect(lambda: self._run_action("repair"))
        self._btn_uninstall.clicked.connect(lambda: self._run_action("uninstall"))
        self._table.itemSelectionChanged.connect(self._on_selection_changed)

        self._persist_channel()
        self._update_root_label()

    def activate(self) -> None:
        """Called when the Scripts tab is shown."""
        font_err = embr_ui.font_load_error()
        if font_err:
            self._set_status(font_err)
        self.refresh()

    def _host_window(self) -> QWidget | None:
        win = self.window()
        return win if win is not None and win is not self else None

    def _channel_phrase(self) -> str:
        if self._catalog_path is not None:
            return f"local catalog ({self._catalog_path.name})"
        return f"channel “{self._channel}”"

    def _idle_status(self) -> str:
        total = self._table.rowCount()
        selected = self._selected_rows()
        n = len(selected)
        base = f"{total} package{'s' if total != 1 else ''} on {self._channel_phrase()}"

        if n == 0:
            return f"Ready — {base}. Select a package to continue."

        names = ", ".join(r["name"] for r in selected[:3])
        if n > 3:
            names += f", +{n - 3} more"

        statuses = {r["status"] for r in selected}
        if local.STATUS_NOT_INSTALLED in statuses and local.STATUS_UPDATE_AVAILABLE in statuses:
            hint = "Install / Update is available."
        elif local.STATUS_NOT_INSTALLED in statuses:
            hint = "Ready to install."
        elif local.STATUS_UPDATE_AVAILABLE in statuses:
            hint = "Update available."
        elif local.STATUS_CORRUPTED in statuses:
            hint = "Repair recommended."
        elif all(r["id"] in actions.PROTECTED_FROM_UNINSTALL for r in selected):
            hint = "Core packages can’t be uninstalled here."
        elif local.STATUS_UP_TO_DATE in statuses:
            hint = "Up to date."
        else:
            hint = "Choose an action below."

        return f"{n} selected ({names}) — {hint}"

    def _set_status(self, text: str) -> None:
        if self._set_status_fn is not None:
            self._set_status_fn(text)

    def _process_ui(self) -> None:
        host = self._host_window()
        if host is None or not host.isVisible():
            return
        from PySide6.QtCore import QEventLoop

        app = QApplication.instance()
        if app is not None:
            app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

    def _set_busy(self, busy: bool, message: str | None = None) -> None:
        self._busy = busy
        self._table.setEnabled(not busy)
        if self._catalog_path is None:
            self._channel_combo.setEnabled(not busy)

        if busy:
            effect = QGraphicsOpacityEffect(self._table)
            effect.setOpacity(0.45)
            self._table.setGraphicsEffect(effect)
            for btn in (
                self._btn_refresh,
                self._btn_install_update,
                self._btn_repair,
                self._btn_uninstall,
            ):
                btn.setEnabled(False)
            if message:
                self._set_status(message)
        else:
            self._table.setGraphicsEffect(None)
            self._update_action_buttons()

        self._process_ui()

    def _on_selection_changed(self) -> None:
        if self._busy:
            return
        self._update_action_buttons()
        self._set_status(self._idle_status())

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

    def _persist_channel(self) -> None:
        local.set_channel(self._root, self._channel)

    def _on_channel_changed(self, _index: int) -> None:
        data = self._channel_combo.currentData()
        if data is None:
            return
        self._channel = normalize_channel(str(data))
        self._persist_channel()
        self.refresh()

    def _update_root_label(self) -> None:
        self._root_label.setText(f"Install root: {paths.describe_install_root(self._root)}")

    def _load_catalog(self) -> Catalog:
        if self._catalog_path is not None:
            return load_catalog_from_path(str(self._catalog_path))
        return fetch_catalog_for_channel(self._channel)

    def _selected_rows(self) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for idx in self._table.selectionModel().selectedRows():
            item = self._table.item(idx.row(), _COL_NAME)
            if item is None:
                continue
            pkg_id = item.data(Qt.ItemDataRole.UserRole)
            if not pkg_id:
                continue
            row = self._rows_by_id.get(str(pkg_id))
            if row:
                rows.append(row)
        return rows

    def _update_action_buttons(self) -> None:
        if self._busy:
            return
        selected = self._selected_rows()
        can_install_update = any(
            r["status"]
            in (local.STATUS_NOT_INSTALLED, local.STATUS_UPDATE_AVAILABLE)
            for r in selected
        )
        can_repair = any(r["status"] == local.STATUS_CORRUPTED for r in selected)
        can_uninstall = any(
            r["status"] != local.STATUS_NOT_INSTALLED
            and r["id"] not in actions.PROTECTED_FROM_UNINSTALL
            for r in selected
        )
        self._btn_refresh.setEnabled(True)
        self._btn_install_update.setEnabled(can_install_update)
        self._btn_repair.setEnabled(can_repair)
        self._btn_uninstall.setEnabled(can_uninstall)
        if selected and all(r["id"] in actions.PROTECTED_FROM_UNINSTALL for r in selected):
            self._btn_uninstall.setToolTip(
                "Embr Core and Embr Manager cannot be uninstalled from the UI."
            )
        else:
            self._btn_uninstall.setToolTip("")

    def refresh(self) -> None:
        self._set_busy(True, f"Checking {self._channel_phrase()}…")
        try:
            self._catalog = self._load_catalog()
            rows = actions.build_status_rows(self._catalog, self._root)
        except CatalogError as exc:
            self._set_busy(False)
            self._alert(str(exc))
            self._set_status(
                f"Couldn’t load {self._channel_phrase()}. Try another channel or Refresh."
            )
            return
        except Exception as exc:
            self._set_busy(False)
            msg = f"Embr Manager: Scripts refresh failed - {exc}"
            self._alert(msg)
            self._set_status("Refresh failed. Check the network and try again.")
            return

        self._rows_by_id = {row["id"]: row for row in rows}
        self._table.setRowCount(0)
        for row in rows:
            r = self._table.rowCount()
            self._table.insertRow(r)
            values = [row["name"], row["status"], row["local"], row["remote"]]
            for c, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if c == _COL_NAME:
                    item.setData(Qt.ItemDataRole.UserRole, row["id"])
                self._table.setItem(r, c, item)
        self._table.setColumnWidth(_COL_STATUS, _COL_STATUS_W)
        self._table.setColumnWidth(_COL_LOCAL, _COL_VERSION_W)
        self._table.setColumnWidth(_COL_REMOTE, _COL_VERSION_W)
        self._set_busy(False)
        total = len(rows)
        self._set_status(
            f"Catalog updated — {total} package{'s' if total != 1 else ''} "
            f"on {self._channel_phrase()}."
        )
        self._update_action_buttons()
        host = self._host_window()
        if host is not None:
            host.raise_()
            host.activateWindow()

    def _selected_ids(self) -> list[str]:
        return [r["id"] for r in self._selected_rows()]

    def _partition_install_work(
        self, work: list[dict[str, str]]
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        by_id = {row["id"]: row for row in work}
        core: list[dict[str, str]] = []
        for pkg_id in bootstrap.CORE_PACKAGE_ORDER:
            row = by_id.get(pkg_id)
            if row is not None:
                core.append(row)
        core_ids = {row["id"] for row in core}
        others = [row for row in work if row["id"] not in core_ids]
        return core, others

    def _install_or_update_row(self, row: dict[str, str]) -> None:
        assert self._catalog is not None
        if row["status"] == local.STATUS_NOT_INSTALLED:
            actions.install_package(
                self._catalog,
                row["id"],
                self._root,
                source_root=self._source_root,
            )
        else:
            actions.update_package(
                self._catalog,
                row["id"],
                self._root,
                source_root=self._source_root,
            )

    def _rescan_python_hooks(self) -> bool:
        self._set_busy(True, "Rescanning Python Hooks…")
        try:
            import embr_hooks as hooks

            hooks.refresh()
            return True
        except Exception:
            return False

    def _run_install_or_update(self) -> None:
        if self._catalog is None:
            self.refresh()
        if self._catalog is None:
            return
        selected = self._selected_rows()
        if not selected:
            return

        work = [
            r
            for r in selected
            if r["status"]
            in (local.STATUS_NOT_INSTALLED, local.STATUS_UPDATE_AVAILABLE)
        ]
        if not work:
            return

        core, others = self._partition_install_work(work)
        rescanned = False
        try:
            phases = (("core", core), ("other", others))
            for _phase_name, rows in phases:
                if not rows:
                    continue
                total = len(rows)
                for i, row in enumerate(rows, start=1):
                    verb = (
                        "Installing"
                        if row["status"] == local.STATUS_NOT_INSTALLED
                        else "Updating"
                    )
                    self._set_busy(
                        True,
                        f"{verb} {row['name']} ({i}/{total})…",
                    )
                    self._install_or_update_row(row)
                if self._rescan_python_hooks():
                    rescanned = True
        except (actions.ActionError, CatalogError) as exc:
            self._set_busy(False)
            self._alert(str(exc))
            self._set_status("Install / Update stopped. See the message for details.")
            return
        except Exception as exc:
            self._set_busy(False)
            msg = f"Embr Manager: install/update failed - {exc}"
            self._alert(msg)
            self._set_status("Install / Update failed. Try Repair or Refresh.")
            return
        self._after_action("Install / Update", already_rescanned=rescanned)

    def _run_action(self, action: str) -> None:
        if self._catalog is None:
            self.refresh()
        if self._catalog is None:
            return
        ids = self._selected_ids()
        if not ids:
            return

        if action == "uninstall":
            removable = [i for i in ids if i not in actions.PROTECTED_FROM_UNINSTALL]
            blocked = [i for i in ids if i in actions.PROTECTED_FROM_UNINSTALL]
            if not removable:
                self._alert(
                    "Embr Core and Embr Manager cannot be uninstalled from the UI."
                )
                return
            host = self._host_window()
            geo = host.geometry() if host is not None else None
            msg = f"Uninstall {', '.join(removable)} from:\n{self._root} ?"
            if blocked:
                msg += f"\n\nSkipped (protected): {', '.join(blocked)}"
            answer = QMessageBox.question(
                None,
                "Embr Manager",
                msg,
            )
            if host is not None and geo is not None and not host.isMaximized():
                host.setGeometry(geo)
            if answer != QMessageBox.StandardButton.Yes:
                return
            ids = removable

        label = "Repair" if action == "repair" else "Uninstall"
        try:
            total = len(ids)
            for i, pkg_id in enumerate(ids, start=1):
                name = (
                    self._rows_by_id.get(pkg_id, {}).get("name")
                    or pkg_id
                )
                self._set_busy(True, f"{label}ing {name} ({i}/{total})…")
                if action == "repair":
                    actions.repair_package(
                        self._catalog,
                        pkg_id,
                        self._root,
                        source_root=self._source_root,
                    )
                elif action == "uninstall":
                    actions.uninstall_package(self._catalog, pkg_id, self._root)
        except (actions.ActionError, CatalogError) as exc:
            self._set_busy(False)
            self._alert(str(exc))
            self._set_status(f"{label} stopped. See the message for details.")
            return
        except Exception as exc:
            self._set_busy(False)
            msg = f"Embr Manager: {action} failed - {exc}"
            self._alert(msg)
            self._set_status(f"{label} failed. Try Refresh and try again.")
            return

        self._after_action(label)

    def _after_action(self, action: str, *, already_rescanned: bool = False) -> None:
        self._set_busy(False)
        self.refresh()
        done = f"{action} finished."
        host = self._host_window()
        if already_rescanned:
            self._set_status(f"{done} {self._idle_status()}")
            if host is not None:
                host.raise_()
                host.activateWindow()
            return
        try:
            import embr_hooks as hooks

            hooks.refresh()
            self._set_status(f"{done} {self._idle_status()}")
        except Exception:
            self._set_status(
                f"{done} If menus look stale, run Rescan Python Hooks."
            )
        if host is not None:
            host.raise_()
            host.activateWindow()


class EmbrManagerWindow(QDialog):
    """Tabbed hub. Scripts is first; PyBox / Matchbox tabs come later."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        root: Path | None = None,
        catalog_path: Path | None = None,
        source_root: Path | None = None,
        channel: str | None = None,
    ) -> None:
        super().__init__(parent)
        self._root = (root or paths.install_root()).resolve()

        title_bar = embr_ui.prepare_embr_window(self, "Embr Manager")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(title_bar)

        self._tabs = QTabWidget()
        self._tabs.setObjectName("embrTabs")
        self._tabs.setDocumentMode(True)
        self._scripts = ScriptsTab(
            self,
            root=self._root,
            catalog_path=catalog_path,
            source_root=source_root,
            channel=channel,
            set_status=self._set_status,
        )
        self._tabs.addTab(self._scripts, "Scripts")
        layout.addWidget(self._tabs, 1)

        self._status = QLabel()
        self._status.setObjectName("embrStatus")
        self._status.setWordWrap(False)
        self._status.setMinimumWidth(0)
        self._status.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        self._status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._status)

        self.resize(780, 520)
        self._tabs.currentChanged.connect(self._on_tab_changed)
        self._scripts.activate()

    def _set_status(self, text: str) -> None:
        self._status.setText(text)
        self._status.setMinimumWidth(0)

    def _on_tab_changed(self, index: int) -> None:
        widget = self._tabs.widget(index)
        if widget is self._scripts:
            self._scripts.activate()


# Back-compat alias for older imports / tests.
ScriptManagerWindow = EmbrManagerWindow


def open_embr_manager() -> None:
    """Entry used by the Flame hook (one window per QApplication)."""
    root = paths.install_root()
    catalog_path = None
    source_root = None
    candidate = paths.scripts_root().parent / "catalog" / "catalog.json"
    if candidate.is_file() and (paths.scripts_root() / "embr").is_dir():
        if paths.scripts_root().name == "scripts":
            catalog_path = candidate
            source_root = paths.scripts_root()

    if not (root / "embr").is_dir():
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        chosen = bootstrap.prompt_bootstrap_choice_qt()
        if chosen is None:
            return
        try:
            channel = local.DEFAULT_CHANNEL
            cat = (
                load_catalog_from_path(str(catalog_path))
                if catalog_path
                else fetch_catalog_for_channel(channel)
            )
            bootstrap.bootstrap_into(
                chosen,
                catalog=cat,
                source_root=source_root,
                channel=channel,
            )
            QMessageBox.information(
                None,
                "Embr Setup",
                f"Embr installed to:\n{chosen}\n\n"
                f"Channel: {channel}\n\n"
                "Rescan Python Hooks (or restart Flame), then open Manager again.",
            )
        except Exception as exc:
            QMessageBox.critical(None, "Embr Setup", str(exc))
        return

    def _factory() -> EmbrManagerWindow:
        return EmbrManagerWindow(
            root=root,
            catalog_path=catalog_path,
            source_root=source_root,
        )

    embr_ui.show_singleton_window("_embr_manager", _factory)


def open_script_manager() -> None:
    """Back-compat entry point."""
    open_embr_manager()
