"""Embr Preferences window — menu order and visibility."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import embr_log as log
import embr_menus as menus
import embr_paths as paths
import embr_ui as embr_ui


class PreferencesWindow(QDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        root: Path | None = None,
        config_root: Path | None = None,
    ) -> None:
        super().__init__(parent)
        # ``root`` kept as deprecated alias for config_root (tests / old call sites).
        self._config_root = (config_root or root or paths.flame_user_embr_dir()).resolve()
        self._current_surface: str | None = None
        self._dirty = False

        title_bar = embr_ui.prepare_embr_window(self, "Preferences")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(title_bar)

        body = QVBoxLayout()
        body.setContentsMargins(12, 10, 12, 10)
        body.setSpacing(8)

        surface_row = QHBoxLayout()
        surface_row.addWidget(QLabel("Menu:"))
        self._surface_combo = QComboBox()
        self._surface_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        for surface in menus.surfaces_with_entries():
            label = menus.SURFACE_LABELS.get(surface, surface)
            self._surface_combo.addItem(label, surface)
        surface_row.addWidget(self._surface_combo, 1)
        body.addLayout(surface_row)

        hint = QLabel("Drag to reorder. Uncheck to hide from the Embr menu.")
        hint.setObjectName("embrMuted")
        body.addWidget(hint)

        self._list = QListWidget()
        self._list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._list.setAlternatingRowColors(True)
        self._list.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        body.addWidget(self._list, 1)

        buttons = QHBoxLayout()
        self._btn_reset = QPushButton("Reset to Defaults")
        self._btn_apply = QPushButton("Apply")
        self._btn_apply.setObjectName("embrAccent")
        self._btn_close = QPushButton("Close")
        for btn in (self._btn_reset, self._btn_apply, self._btn_close):
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        buttons.addWidget(self._btn_reset)
        buttons.addStretch(1)
        buttons.addWidget(self._btn_close)
        buttons.addWidget(self._btn_apply)
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

        self.resize(480, 420)

        self._surface_combo.currentIndexChanged.connect(self._on_surface_changed)
        self._list.model().rowsMoved.connect(self._mark_dirty)
        self._list.itemChanged.connect(self._mark_dirty)
        self._btn_reset.clicked.connect(self._reset_all)
        self._btn_apply.clicked.connect(self._apply)
        self._btn_close.clicked.connect(self.close)

        font_err = embr_ui.font_load_error()
        if font_err:
            self._set_status(font_err)

        if self._surface_combo.count() == 0:
            self._set_status("No menu entries in defaults.")
            self._btn_apply.setEnabled(False)
            self._btn_reset.setEnabled(False)
        else:
            self._load_surface(self._surface_combo.currentData())

    def _set_status(self, text: str) -> None:
        self._status.setText(text)

    def _mark_dirty(self, *_args) -> None:
        self._dirty = True
        self._set_status("Unsaved changes — click Apply to update Flame menus.")

    def _on_surface_changed(self, _index: int) -> None:
        if self._dirty:
            reply = QMessageBox.question(
                self,
                "Preferences",
                "Apply changes for the current menu before switching?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Cancel:
                self._surface_combo.blockSignals(True)
                idx = self._surface_combo.findData(self._current_surface)
                if idx >= 0:
                    self._surface_combo.setCurrentIndex(idx)
                self._surface_combo.blockSignals(False)
                return
            if reply == QMessageBox.StandardButton.Yes:
                if not self._apply(rescan=False):
                    self._surface_combo.blockSignals(True)
                    idx = self._surface_combo.findData(self._current_surface)
                    if idx >= 0:
                        self._surface_combo.setCurrentIndex(idx)
                    self._surface_combo.blockSignals(False)
                    return
        self._load_surface(self._surface_combo.currentData())

    def _load_surface(self, surface: str | None) -> None:
        self._list.blockSignals(True)
        self._list.clear()
        self._current_surface = surface
        self._dirty = False
        if not surface:
            self._list.blockSignals(False)
            return
        for entry in menus.effective_entries(surface, config_root=self._config_root):
            item = QListWidgetItem(entry["caption"])
            item.setData(Qt.ItemDataRole.UserRole, entry["id"])
            flags = (
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsDragEnabled
            )
            if entry.get("locked"):
                # Always-on tools (Script Manager / Preferences): show checked, not hideable.
                item.setFlags(flags)
                item.setCheckState(Qt.CheckState.Checked)
                item.setToolTip("Always visible — cannot be hidden.")
            else:
                item.setFlags(flags | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(
                    Qt.CheckState.Checked
                    if entry["visible"]
                    else Qt.CheckState.Unchecked
                )
            self._list.addItem(item)
        self._list.blockSignals(False)
        label = menus.SURFACE_LABELS.get(surface, surface)
        self._set_status(f"{label}: {self._list.count()} item(s).")

    def _collect_surface(self) -> tuple[list[str], list[str]]:
        order: list[str] = []
        hidden: list[str] = []
        locked = {
            e["id"]
            for e in menus.effective_entries(
                self._current_surface or "", config_root=self._config_root
            )
            if e.get("locked")
        }
        for i in range(self._list.count()):
            item = self._list.item(i)
            action_id = str(item.data(Qt.ItemDataRole.UserRole) or "")
            if not action_id:
                continue
            order.append(action_id)
            if action_id in locked:
                continue
            if item.checkState() != Qt.CheckState.Checked:
                hidden.append(action_id)
        return order, hidden

    def _apply(self, *, rescan: bool = True) -> bool:
        surface = self._current_surface
        if not surface:
            return False
        order, hidden = self._collect_surface()
        try:
            menus.set_surface_prefs(
                surface, order=order, hidden=hidden, config_root=self._config_root
            )
        except menus.MenuError as exc:
            log.error(str(exc), duration=10)
            QMessageBox.warning(self, "Preferences", str(exc))
            return False

        self._dirty = False
        if rescan:
            try:
                menus.refresh_hooks_after_prefs()
                self._set_status("Saved. Flame menus rescanned.")
            except Exception as exc:
                log.error(
                    f"Embr Preferences: saved prefs but rescan failed - {exc}",
                    duration=10,
                )
                self._set_status(
                    "Saved. Run Main Menu → Python → Rescan Python Hooks if menus look stale."
                )
        else:
            self._set_status("Saved.")
        return True

    def _reset_all(self) -> None:
        reply = QMessageBox.question(
            self,
            "Preferences",
            "Reset all Embr menu order and visibility to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            menus.reset_menu_prefs(config_root=self._config_root)
        except menus.MenuError as exc:
            log.error(str(exc), duration=10)
            QMessageBox.warning(self, "Preferences", str(exc))
            return
        self._dirty = False
        self._load_surface(self._current_surface)
        try:
            menus.refresh_hooks_after_prefs()
            self._set_status("Defaults restored. Flame menus rescanned.")
        except Exception as exc:
            log.error(
                f"Embr Preferences: reset prefs but rescan failed - {exc}",
                duration=10,
            )
            self._set_status(
                "Defaults restored. Run Rescan Python Hooks if menus look stale."
            )

    def closeEvent(self, event) -> None:  # noqa: N802
        if self._dirty:
            reply = QMessageBox.question(
                self,
                "Preferences",
                "Discard unsaved menu changes?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        super().closeEvent(event)


def open_preferences(*, config_root: Path | None = None, root: Path | None = None) -> PreferencesWindow:
    """Show the Preferences window (one per QApplication)."""
    cfg = config_root or root

    def _factory() -> PreferencesWindow:
        return PreferencesWindow(config_root=cfg)

    return embr_ui.show_singleton_window("_embr_preferences", _factory)
