"""Script Manager window (PySide6)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
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
    channel_label,
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


class ScriptManagerWindow(QDialog):
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
        self._catalog_path = catalog_path
        self._source_root = source_root
        self._catalog: Catalog | None = None
        self._rows_by_id: dict[str, dict[str, str]] = {}
        if channel is not None:
            self._channel = normalize_channel(channel)
        else:
            self._channel = normalize_channel(local.get_channel(self._root))

        title_bar = embr_ui.prepare_embr_window(self, "Script Manager")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(title_bar)

        body = QVBoxLayout()
        body.setContentsMargins(12, 10, 12, 10)
        body.setSpacing(8)

        meta = QHBoxLayout()
        self._root_label = QLabel()
        self._root_label.setObjectName("embrRoot")
        meta.addWidget(self._root_label, 1)

        meta.addWidget(QLabel("Channel:"))
        self._channel_combo = QComboBox()
        self._channel_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        for name in CHANNEL_ORDER:
            self._channel_combo.addItem(channel_label(name), name)
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
        body.addWidget(self._table)

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
        buttons.addWidget(self._btn_install_update)
        buttons.addWidget(self._btn_repair)
        buttons.addWidget(self._btn_uninstall)
        body.addLayout(buttons)

        layout.addLayout(body)

        self._status = QLabel()
        self._status.setObjectName("embrStatus")
        self._status.setWordWrap(False)
        self._status.setMinimumWidth(0)
        self._status.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        self._status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._status)

        self.resize(780, 480)
        self._normal_size = self.size()

        self._btn_refresh.clicked.connect(self.refresh)
        self._btn_install_update.clicked.connect(self._run_install_or_update)
        self._btn_repair.clicked.connect(lambda: self._run_action("repair"))
        self._btn_uninstall.clicked.connect(lambda: self._run_action("uninstall"))
        self._table.itemSelectionChanged.connect(self._update_action_buttons)

        font_err = embr_ui.font_load_error()
        if font_err:
            self._set_status(font_err)

        self._persist_channel()
        self._update_root_label()
        self.refresh()

    def _set_status(self, text: str) -> None:
        """Set status text without letting long messages widen the window."""
        self._status.setText(text)
        # Re-assert ignored horizontal policy after text changes on some styles.
        self._status.setMinimumWidth(0)

    def _alert(self, text: str, *, critical: bool = True) -> None:
        """Show a modal alert without resizing this frameless window."""
        geo = self.geometry()
        box = QMessageBox(None)
        box.setIcon(
            QMessageBox.Icon.Critical if critical else QMessageBox.Icon.Information
        )
        box.setWindowTitle("Embr Script Manager")
        box.setText(text)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()
        if not self.isMaximized():
            self.setGeometry(geo)

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
        selected = self._selected_rows()
        can_install_update = any(
            r["status"]
            in (local.STATUS_NOT_INSTALLED, local.STATUS_UPDATE_AVAILABLE)
            for r in selected
        )
        can_repair = any(r["status"] == local.STATUS_CORRUPTED for r in selected)
        can_uninstall = any(
            r["status"] != local.STATUS_NOT_INSTALLED for r in selected
        )
        self._btn_refresh.setEnabled(True)
        self._btn_install_update.setEnabled(can_install_update)
        self._btn_repair.setEnabled(can_repair)
        self._btn_uninstall.setEnabled(can_uninstall)

    def refresh(self) -> None:
        try:
            self._catalog = self._load_catalog()
            rows = actions.build_status_rows(self._catalog, self._root)
        except CatalogError as exc:
            self._alert(str(exc))
            self._set_status(str(exc))
            self._update_action_buttons()
            return
        except Exception as exc:
            msg = f"Embr Script Manager: refresh failed - {exc}"
            self._alert(msg)
            self._set_status(msg)
            self._update_action_buttons()
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
        # Keep fixed Status/Local/Remote; Name stays Stretch (do not resizeToContents).
        self._table.setColumnWidth(_COL_STATUS, _COL_STATUS_W)
        self._table.setColumnWidth(_COL_LOCAL, _COL_VERSION_W)
        self._table.setColumnWidth(_COL_REMOTE, _COL_VERSION_W)
        src = (
            f"local:{self._catalog_path.name}"
            if self._catalog_path is not None
            else f"channel:{self._channel}"
        )
        self._set_status(
            f"{src} · {self._catalog.repo}@{self._catalog.ref} — "
            f"{len(rows)} package(s)"
        )
        self._update_action_buttons()

    def _selected_ids(self) -> list[str]:
        return [r["id"] for r in self._selected_rows()]

    def _run_install_or_update(self) -> None:
        if self._catalog is None:
            self.refresh()
        if self._catalog is None:
            return
        selected = self._selected_rows()
        if not selected:
            return
        try:
            for row in selected:
                pkg_id = row["id"]
                status = row["status"]
                if status == local.STATUS_NOT_INSTALLED:
                    actions.install_package(
                        self._catalog,
                        pkg_id,
                        self._root,
                        source_root=self._source_root,
                    )
                elif status == local.STATUS_UPDATE_AVAILABLE:
                    actions.update_package(
                        self._catalog,
                        pkg_id,
                        self._root,
                        source_root=self._source_root,
                    )
        except (actions.ActionError, CatalogError) as exc:
            self._alert(str(exc))
            self._set_status(str(exc))
            return
        except Exception as exc:
            msg = f"Embr Script Manager: install/update failed - {exc}"
            self._alert(msg)
            self._set_status(msg)
            return
        self._after_action("install/update")

    def _run_action(self, action: str) -> None:
        if self._catalog is None:
            self.refresh()
        if self._catalog is None:
            return
        ids = self._selected_ids()
        if not ids:
            return

        if action == "uninstall":
            geo = self.geometry()
            answer = QMessageBox.question(
                None,
                "Embr Script Manager",
                f"Uninstall {', '.join(ids)} from:\n{self._root} ?",
            )
            if not self.isMaximized():
                self.setGeometry(geo)
            if answer != QMessageBox.StandardButton.Yes:
                return

        try:
            for pkg_id in ids:
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
            self._alert(str(exc))
            self._set_status(str(exc))
            return
        except Exception as exc:
            msg = f"Embr Script Manager: {action} failed - {exc}"
            self._alert(msg)
            self._set_status(msg)
            return

        self._after_action(action)

    def _after_action(self, action: str) -> None:
        self.refresh()
        self._set_status(f"{action} completed")
        try:
            import embr_hooks as hooks

            hooks.refresh(invalidate=("embr", "embr_manager"))
        except Exception:
            self._set_status(
                f"{action} completed — run Rescan Python Hooks if menus did not update"
            )


def open_script_manager() -> None:
    """Entry used by the Flame hook."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    root = paths.install_root()
    # Dev convenience: use local catalog when running from the repo tree.
    catalog_path = None
    source_root = None
    candidate = paths.scripts_root().parent / "catalog" / "catalog.json"
    if candidate.is_file() and (paths.scripts_root() / "embr").is_dir():
        # Only treat as repo checkout when catalog sits next to scripts/.
        if paths.scripts_root().name == "scripts":
            catalog_path = candidate
            source_root = paths.scripts_root()

    if not bootstrap.is_bootstrapped(root) and not (root / "embr").is_dir():
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
                "Rescan Python Hooks (or restart Flame), then open Script Manager again.",
            )
        except Exception as exc:
            QMessageBox.critical(None, "Embr Setup", str(exc))
        return

    window = ScriptManagerWindow(
        root=root,
        catalog_path=catalog_path,
        source_root=source_root,
    )
    window.show()
    window.raise_()
    window.activateWindow()
    # Keep a reference so the window is not garbage-collected.
    app._embr_script_manager = window  # type: ignore[attr-defined]
