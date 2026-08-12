"""Script Manager window (PySide6)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QStatusBar,
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
        self._table.horizontalHeader().setStretchLastSection(True)
        body.addWidget(self._table)

        buttons = QHBoxLayout()
        self._btn_refresh = QPushButton("Refresh")
        self._btn_install = QPushButton("Install")
        self._btn_install.setObjectName("embrAccent")
        self._btn_update = QPushButton("Update")
        self._btn_repair = QPushButton("Repair")
        self._btn_uninstall = QPushButton("Uninstall")
        for btn in (
            self._btn_refresh,
            self._btn_install,
            self._btn_update,
            self._btn_repair,
            self._btn_uninstall,
        ):
            buttons.addWidget(btn)
        buttons.addStretch(1)
        body.addLayout(buttons)

        self._status = QStatusBar()
        body.addWidget(self._status)

        layout.addLayout(body)

        self.resize(780, 480)

        self._btn_refresh.clicked.connect(self.refresh)
        self._btn_install.clicked.connect(lambda: self._run_action("install"))
        self._btn_update.clicked.connect(lambda: self._run_action("update"))
        self._btn_repair.clicked.connect(lambda: self._run_action("repair"))
        self._btn_uninstall.clicked.connect(lambda: self._run_action("uninstall"))

        font_err = embr_ui.font_load_error()
        if font_err:
            self._status.showMessage(font_err)

        self._persist_channel()
        self._update_root_label()
        self.refresh()

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
        label = paths.describe_install_root(self._root)
        self._root_label.setText(f"Install root: {label}  ({self._root})")

    def _load_catalog(self) -> Catalog:
        if self._catalog_path is not None:
            return load_catalog_from_path(str(self._catalog_path))
        return fetch_catalog_for_channel(self._channel)

    def refresh(self) -> None:
        try:
            self._catalog = self._load_catalog()
            rows = actions.build_status_rows(self._catalog, self._root)
        except CatalogError as exc:
            QMessageBox.critical(self, "Embr Script Manager", str(exc))
            self._status.showMessage(str(exc))
            return
        except Exception as exc:
            msg = f"Embr Script Manager: refresh failed - {exc}"
            QMessageBox.critical(self, "Embr Script Manager", msg)
            self._status.showMessage(msg)
            return

        self._table.setRowCount(0)
        for row in rows:
            r = self._table.rowCount()
            self._table.insertRow(r)
            values = [row["name"], row["status"], row["local"], row["remote"]]
            for c, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if c == 0:
                    item.setData(Qt.ItemDataRole.UserRole, row["id"])
                self._table.setItem(r, c, item)
        self._table.resizeColumnsToContents()
        src = (
            f"local:{self._catalog_path.name}"
            if self._catalog_path is not None
            else f"channel:{self._channel}"
        )
        self._status.showMessage(
            f"{src} · {self._catalog.repo}@{self._catalog.ref} — "
            f"{len(rows)} package(s)"
        )

    def _selected_ids(self) -> list[str]:
        ids: list[str] = []
        for idx in self._table.selectionModel().selectedRows():
            item = self._table.item(idx.row(), 0)
            if item is None:
                continue
            pkg_id = item.data(Qt.ItemDataRole.UserRole)
            if pkg_id:
                ids.append(str(pkg_id))
        return ids

    def _run_action(self, action: str) -> None:
        if self._catalog is None:
            self.refresh()
        if self._catalog is None:
            return
        ids = self._selected_ids()
        if not ids:
            QMessageBox.information(
                self,
                "Embr Script Manager",
                "Select one or more packages first.",
            )
            return

        if action == "uninstall":
            answer = QMessageBox.question(
                self,
                "Embr Script Manager",
                f"Uninstall {', '.join(ids)} from:\n{self._root} ?",
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        try:
            for pkg_id in ids:
                if action == "install":
                    actions.install_package(
                        self._catalog,
                        pkg_id,
                        self._root,
                        source_root=self._source_root,
                    )
                elif action == "update":
                    actions.update_package(
                        self._catalog,
                        pkg_id,
                        self._root,
                        source_root=self._source_root,
                    )
                elif action == "repair":
                    actions.repair_package(
                        self._catalog,
                        pkg_id,
                        self._root,
                        source_root=self._source_root,
                    )
                elif action == "uninstall":
                    actions.uninstall_package(self._catalog, pkg_id, self._root)
        except (actions.ActionError, CatalogError) as exc:
            QMessageBox.critical(self, "Embr Script Manager", str(exc))
            self._status.showMessage(str(exc))
            return
        except Exception as exc:
            msg = f"Embr Script Manager: {action} failed - {exc}"
            QMessageBox.critical(self, "Embr Script Manager", msg)
            self._status.showMessage(msg)
            return

        self.refresh()
        self._status.showMessage(f"{action} completed")
        try:
            import embr_hooks as hooks

            hooks.refresh(invalidate=("embr", "embr_manager"))
        except Exception:
            self._status.showMessage(
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

    installed = bootstrap.is_bootstrapped(root)
    vendor_candidates = [p for _, p in bootstrap.candidate_roots()]
    on_vendor_tree = root in {p.resolve() for p in vendor_candidates} or (
        root.name == paths.VENDOR_DIR_NAME
    )

    if not installed and not on_vendor_tree:
        # Running from a transient hook path without Embr on disk target yet.
        pass

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
