"""Embr Rename window (PySide6)."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import embr_log as log
import embr_rn_prefs as rn_prefs
import embr_rn_selection as rn_sel
import embr_rn_tokens as tokens
import embr_ui as embr_ui


def _section_label(text: str) -> QLabel:
    lab = QLabel(text)
    lab.setObjectName("embrSection")
    return lab


def _hairline() -> QWidget:
    """1px rule — plain widget (QFrame HLine often paints ~2px)."""
    line = QWidget()
    line.setObjectName("embrHairline")
    line.setFixedHeight(1)
    line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    return line


class _ReplaceRow(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(embr_ui.EMBR_SPACE_2)
        self.find_edit = QLineEdit()
        self.find_edit.setPlaceholderText("Find")
        self.replace_edit = QLineEdit()
        self.replace_edit.setPlaceholderText("Replace")
        self.btn_remove = QPushButton("Remove")
        self.btn_remove.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.find_edit, 1)
        layout.addWidget(self.replace_edit, 1)
        layout.addWidget(self.btn_remove)


class RenameWindow(QDialog):
    def __init__(
        self,
        selection: tuple[Any, ...],
        *,
        surface: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._surface = surface
        self._selection = tuple(selection)
        self._renameable = tokens.renameable_items(self._selection)

        title_bar = embr_ui.prepare_embr_window(self, "Rename")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(title_bar)

        body = QVBoxLayout()
        body.setContentsMargins(
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
        )
        body.setSpacing(embr_ui.EMBR_SPACE_2)

        # --- Preview (result first) ---
        body.addWidget(_section_label("Preview"))
        self._preview = QLineEdit()
        self._preview.setObjectName("embrPreview")
        self._preview.setReadOnly(True)
        self._preview.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._preview.setPlaceholderText("—")
        body.addWidget(self._preview)

        body.addWidget(_hairline())

        # --- Pattern + tokens ---
        body.addWidget(_section_label("Pattern"))
        self._pattern = QLineEdit()
        self._pattern.setPlaceholderText("<name>_<date@YYMMDD>")
        body.addWidget(self._pattern)

        token_row = QHBoxLayout()
        token_row.setSpacing(embr_ui.EMBR_SPACE_2)
        token_row.setContentsMargins(0, 0, 0, 0)
        self._btn_tok_name = QPushButton("name")
        self._btn_tok_date = QPushButton("date")
        for btn in (self._btn_tok_name, self._btn_tok_date):
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            token_row.addWidget(btn)
        token_row.addStretch(1)
        body.addLayout(token_row)

        body.addWidget(_hairline())

        # --- Replace ---
        replace_header = QHBoxLayout()
        replace_header.setSpacing(embr_ui.EMBR_SPACE_2)
        replace_header.setContentsMargins(0, 0, 0, 0)
        replace_header.addWidget(_section_label("Replace"), 1)
        self._btn_add_replace = QPushButton("Add")
        self._btn_add_replace.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        replace_header.addWidget(self._btn_add_replace)
        body.addLayout(replace_header)

        self._replace_host = QVBoxLayout()
        self._replace_host.setSpacing(embr_ui.EMBR_SPACE_2)
        self._replace_host.setContentsMargins(
            embr_ui.EMBR_SPACE_2,
            embr_ui.EMBR_SPACE_2,
            embr_ui.EMBR_SPACE_2,
            embr_ui.EMBR_SPACE_2,
        )
        replace_wrap = QWidget()
        replace_wrap.setObjectName("embrReplaceHost")
        replace_wrap.setLayout(self._replace_host)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(replace_wrap)
        # Fit three replace rows without scrolling (row 32 + spacing/margins + border).
        _row_h = embr_ui.EMBR_CONTROL_MIN_HEIGHT + 2
        _sp = embr_ui.EMBR_SPACE_2
        _m = embr_ui.EMBR_SPACE_2
        _rows = 3
        replace_h = _rows * _row_h + (_rows - 1) * _sp + 2 * _m + 2
        scroll.setMinimumHeight(replace_h)
        scroll.setMaximumHeight(max(replace_h, 200))
        body.addWidget(scroll, 1)

        # --- Actions ---
        buttons = QHBoxLayout()
        buttons.setSpacing(embr_ui.EMBR_SPACE_2)
        buttons.addStretch(1)
        self._btn_cancel = QPushButton("Cancel")
        self._btn_rename = QPushButton("Rename")
        self._btn_rename.setObjectName("embrAccent")
        for btn in (self._btn_cancel, self._btn_rename):
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        buttons.addWidget(self._btn_cancel)
        buttons.addWidget(self._btn_rename)
        body.addLayout(buttons)

        layout.addLayout(body, 1)

        self._status = QLabel()
        self._status.setObjectName("embrStatus")
        self._status.setWordWrap(False)
        self._status.setMinimumWidth(0)
        self._status.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        self._status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._status)

        self.resize(520, 480)

        saved = rn_prefs.load_rename_prefs()
        self._pattern.setText(saved["pattern"])
        pairs = saved["replacements"] or [("", "")]
        for find, replace in pairs:
            self._add_replace_row(find, replace)

        self._pattern.textChanged.connect(self._update_preview)
        self._btn_tok_name.clicked.connect(lambda: self._insert_token("<name>"))
        self._btn_tok_date.clicked.connect(lambda: self._insert_token("<date@YYMMDD>"))
        self._btn_add_replace.clicked.connect(lambda: self._add_replace_row("", ""))
        self._btn_cancel.clicked.connect(self.close)
        self._btn_rename.clicked.connect(self._apply_rename)

        self._update_preview()
        if not self._renameable:
            self._btn_rename.setEnabled(False)

    def _insert_token(self, token: str) -> None:
        self._pattern.insert(token)
        self._pattern.setFocus()

    def _add_replace_row(self, find: str = "", replace: str = "") -> None:
        row = _ReplaceRow()
        row.find_edit.setText(find)
        row.replace_edit.setText(replace)
        row.find_edit.textChanged.connect(self._update_preview)
        row.replace_edit.textChanged.connect(self._update_preview)
        row.btn_remove.clicked.connect(lambda: self._remove_replace_row(row))
        self._replace_host.addWidget(row)
        self._update_preview()

    def _remove_replace_row(self, row: _ReplaceRow) -> None:
        if self._replace_host.count() <= 1:
            row.find_edit.clear()
            row.replace_edit.clear()
            self._update_preview()
            return
        self._replace_host.removeWidget(row)
        row.deleteLater()
        self._update_preview()

    def _collect_pairs(self) -> list[tuple[str, str]]:
        pairs: list[tuple[str, str]] = []
        for i in range(self._replace_host.count()):
            item = self._replace_host.itemAt(i)
            widget = item.widget() if item else None
            if isinstance(widget, _ReplaceRow):
                pairs.append((widget.find_edit.text(), widget.replace_edit.text()))
        return pairs

    def _status_selection_text(self, *, original: str | None = None) -> str:
        summary = rn_sel.selection_summary(self._selection)
        if not self._renameable:
            return f"{summary}  ·  No renameable objects"
        extra = len(self._renameable) - 1
        parts = [summary]
        if original:
            parts.append(f"from “{original}”")
        if extra > 0:
            parts.append(f"+{extra} more")
        return "  ·  ".join(parts)

    def _update_preview(self) -> None:
        if not self._renameable:
            self._preview.clear()
            self._preview.setPlaceholderText("—")
            self._status.setText(self._status_selection_text())
            return
        first = self._renameable[0]
        original = tokens.object_name(first)
        pattern = self._pattern.text() or tokens.DEFAULT_PATTERN
        new_name = tokens.compute_new_name(original, pattern, self._collect_pairs())
        if new_name:
            self._preview.setText(new_name)
            self._preview.setPlaceholderText("")
        else:
            self._preview.clear()
            self._preview.setPlaceholderText("(empty — will skip)")
        self._status.setText(self._status_selection_text(original=original or None))

    def _apply_rename(self) -> None:
        pattern = self._pattern.text() or tokens.DEFAULT_PATTERN
        pairs = self._collect_pairs()
        try:
            rn_prefs.save_rename_prefs(pattern=pattern, replacements=pairs)
        except Exception as exc:
            log.error(f"Embr Rename: could not save prefs - {exc}", duration=8)

        ok = 0
        skipped = 0
        failed = 0
        for obj in self._renameable:
            original = tokens.object_name(obj)
            new_name = tokens.compute_new_name(original, pattern, pairs)
            if not new_name:
                skipped += 1
                continue
            if new_name == original:
                skipped += 1
                continue
            try:
                name_attr = getattr(obj, "name", None)
                setter = getattr(name_attr, "set_value", None)
                if callable(setter):
                    setter(new_name)
                else:
                    obj.name = new_name  # type: ignore[attr-defined]
                ok += 1
            except Exception as exc:
                failed += 1
                log.error(
                    f"Embr Rename: failed on {type(obj).__name__!r} "
                    f"{original!r} -> {new_name!r} - {exc}",
                    duration=8,
                )

        msg = f"Renamed {ok}."
        if skipped:
            msg += f" Skipped {skipped}."
        if failed:
            msg += f" Failed {failed}."
        log.info(f"Embr Rename: {msg}", duration=5)
        self._status.setText(msg)
        if ok and not failed:
            self.accept()


def open_rename(selection: tuple[Any, ...], *, surface: str) -> RenameWindow:
    """Show Rename for a cached isVisible selection (singleton per app)."""
    snapshot = tuple(selection)

    def _factory() -> RenameWindow:
        return RenameWindow(snapshot, surface=surface)

    # One window; recreate factory captures current snapshot when creating new.
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    existing = getattr(app, "_embr_rename", None)
    if existing is not None:
        try:
            # Replace contents by closing and recreating with new selection.
            existing.close()
        except RuntimeError:
            pass
        try:
            setattr(app, "_embr_rename", None)
        except Exception:
            pass
    return embr_ui.show_singleton_window("_embr_rename", _factory)
