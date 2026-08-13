"""Embr Matte window — Phase 0: Add / list / Import / cache."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import embr_mt_export as mt_export
import embr_mt_import as mt_import
import embr_mt_jobs as jobs
import embr_mt_selection as mt_sel
import embr_ui as embr_ui

_ICON_IMPORT = embr_ui.ICON_DOWNLOAD
_ICON_DELETE = embr_ui.ICON_DELETE
_THUMB_W = 96
_THUMB_H = 54


def _icon_button(glyph: str, tooltip: str) -> QPushButton:
    btn = QPushButton()
    btn.setObjectName("embrIconBtn")
    btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn.setToolTip(tooltip)
    btn.setFixedSize(36, 36)
    pix = embr_ui.material_icon_pixmap(glyph, 20, color=embr_ui.EMBR_TEXT)
    if not pix.isNull():
        btn.setIcon(pix)
        btn.setIconSize(pix.size())
    return btn


class _JobRow(QWidget):
    def __init__(
        self,
        job: jobs.MatteJob,
        *,
        on_import,
        on_delete,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.job = job
        row = QHBoxLayout(self)
        row.setContentsMargins(
            embr_ui.EMBR_SPACE_2,
            embr_ui.EMBR_SPACE_2,
            embr_ui.EMBR_SPACE_2,
            embr_ui.EMBR_SPACE_2,
        )
        row.setSpacing(embr_ui.EMBR_SPACE_2)

        self._thumb = QLabel()
        self._thumb.setFixedSize(_THUMB_W, _THUMB_H)
        self._thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumb.setObjectName("embrMuted")
        self._thumb.setStyleSheet(
            f"background: {embr_ui.EMBR_SURFACE_RAISED}; "
            f"border: 1px solid {embr_ui.EMBR_BORDER}; "
            f"border-radius: {embr_ui.EMBR_RADIUS}px;"
        )
        self._load_thumb()
        row.addWidget(self._thumb)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self._name = QLabel(job.clip_name or job.id)
        self._name.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._meta = QLabel(self._meta_text(job))
        self._meta.setObjectName("embrMuted")
        self._meta.setWordWrap(True)
        text_col.addWidget(self._name)
        text_col.addWidget(self._meta)
        text_col.addStretch(1)
        row.addLayout(text_col, 1)

        self._btn_import = _icon_button(
            _ICON_IMPORT, "Import to saved parent reel"
        )
        if self._btn_import.icon().isNull():
            self._btn_import.setText("In")
        self._btn_import.clicked.connect(lambda: on_import(self.job))
        row.addWidget(self._btn_import, 0, Qt.AlignmentFlag.AlignVCenter)

        self._btn_delete = _icon_button(_ICON_DELETE, "Delete job")
        if self._btn_delete.icon().isNull():
            self._btn_delete.setText("Del")
        self._btn_delete.clicked.connect(lambda: on_delete(self.job))
        row.addWidget(self._btn_delete, 0, Qt.AlignmentFlag.AlignVCenter)

    @staticmethod
    def _meta_text(job: jobs.MatteJob) -> str:
        bits = [f"id {job.id}"]
        if job.parent_name:
            bits.append(f"{job.parent_type} “{job.parent_name}”")
        if job.source_width > 0 and job.source_height > 0:
            bits.append(f"{job.source_width}x{job.source_height}")
        if job.source_frame_rate:
            bits.append(job.source_frame_rate)
        if job.source_bit_depth:
            bits.append(f"{job.source_bit_depth}-bit")
        bits.append(job.status)
        return " · ".join(bits)

    def _load_thumb(self) -> None:
        path = Path(self.job.thumbnail) if self.job.thumbnail else None
        if path is None or not path.is_file():
            path = jobs.first_image(Path(self.job.input_dir or ""))
        if path is None or not path.is_file():
            self._thumb.setText("—")
            return
        pix = QPixmap(str(path))
        if pix.isNull():
            self._thumb.setText("—")
            return
        self._thumb.setPixmap(
            pix.scaled(
                _THUMB_W,
                _THUMB_H,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )


class MatteWindow(QWidget):
    """Phase 0 Matte hub: Add exports, list jobs, Import + cache."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session_parents: dict[str, object] = {}
        title_bar = embr_ui.prepare_embr_window(self, "Embr Matte")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(title_bar)

        body = QVBoxLayout()
        body.setContentsMargins(
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
            embr_ui.EMBR_SPACE_3,
        )
        body.setSpacing(embr_ui.EMBR_SPACE_2)

        hint = QLabel(
            "Select clip(s) in the Media Panel, then Add. "
            "Import returns frames to the parent reel saved at Add time."
        )
        hint.setObjectName("embrMuted")
        hint.setWordWrap(True)
        body.addWidget(hint)

        self._empty = QLabel("No jobs yet.")
        self._empty.setObjectName("embrMuted")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._list_host = QWidget()
        self._list_layout = QVBoxLayout(self._list_host)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(embr_ui.EMBR_SPACE_1)
        self._list_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(self._list_host)
        scroll.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        body.addWidget(scroll, 1)
        body.addWidget(self._empty)

        actions = QHBoxLayout()
        self._btn_refresh = QPushButton("Refresh")
        self._btn_add = QPushButton("Add")
        self._btn_add.setObjectName("embrAccent")
        for btn in (self._btn_refresh, self._btn_add):
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        actions.addWidget(self._btn_refresh)
        actions.addStretch(1)
        actions.addWidget(self._btn_add)
        body.addLayout(actions)

        self._status = QLabel()
        self._status.setObjectName("embrStatus")
        self._status.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        root.addLayout(body, 1)
        root.addWidget(self._status)

        self._btn_refresh.clicked.connect(self.reload_jobs)
        self._btn_add.clicked.connect(self.add_selection)

        self.resize(640, 480)
        self.reload_jobs()
        self._set_status("Ready — select Media Panel clips and press Add.")

    def _set_status(self, text: str) -> None:
        self._status.setText(text)

    def _alert(self, text: str, *, critical: bool = True) -> None:
        box = QMessageBox(None)
        box.setIcon(
            QMessageBox.Icon.Critical if critical else QMessageBox.Icon.Information
        )
        box.setWindowTitle("Embr Matte")
        box.setText(text)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()

    def reload_jobs(self) -> None:
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        loaded = jobs.list_jobs()
        self._empty.setVisible(not loaded)
        for job in loaded:
            if job.id in self._session_parents:
                job.parent_ref = self._session_parents[job.id]
            self._list_layout.addWidget(
                _JobRow(
                    job,
                    on_import=self.import_job,
                    on_delete=self.delete_job,
                )
            )
        self._list_layout.addStretch(1)
        self._set_status(
            f"{len(loaded)} job{'s' if len(loaded) != 1 else ''}."
            if loaded
            else "No jobs yet."
        )

    def add_selection(self) -> None:
        clips = mt_sel.iter_selected_clips()
        if not clips:
            self._alert(
                "No clips selected in the Media Panel.\n"
                "Select one or more clips, then press Add."
            )
            return

        added = 0
        for clip in clips:
            try:
                self._add_one(clip)
                added += 1
            except Exception as exc:
                self._alert(f"Add failed for {mt_sel.clip_label(clip)}:\n{exc}")
                break

        self.reload_jobs()
        if added:
            self._set_status(f"Added {added} job{'s' if added != 1 else ''}.")

    def _add_one(self, clip) -> jobs.MatteJob:
        name = mt_sel.clip_label(clip)
        parent = mt_sel.resolve_parent(clip)
        parent_name, parent_type = mt_sel.parent_label(parent)
        if parent is None:
            raise RuntimeError(
                f"Clip “{name}” has no parent reel/folder to import back to."
            )

        job_id = jobs.new_job_id()
        job_dir = jobs.create_job_dirs(job_id)
        export_dir = job_dir / "export"
        fmt = mt_sel.clip_format(clip)
        if fmt.width <= 0 or fmt.height <= 0:
            raise RuntimeError(
                f"Could not read resolution from “{name}”. "
                "Open the clip once in Flame and try Add again."
            )

        self._set_status(f"Exporting “{name}”…")
        mt_export.export_clip_to_job(clip, export_dir)
        thumb = jobs.first_image(export_dir)
        if thumb is None or not thumb.is_file():
            raise mt_export.MatteExportError(
                f"Export produced no image frames under {export_dir}"
            )

        job = jobs.MatteJob(
            id=job_id,
            clip_name=name,
            job_dir=str(job_dir),
            parent_name=parent_name,
            parent_type=parent_type,
            status="ready",
            thumbnail=str(thumb),
            export_dir=str(export_dir),
            # Phase 0: exported PNG sequence is the RGB input (no copy).
            input_dir=str(export_dir),
            source_width=fmt.width,
            source_height=fmt.height,
            source_ratio=fmt.ratio,
            source_bit_depth=fmt.bit_depth,
            source_scan_mode=fmt.scan_mode,
            source_frame_rate=fmt.frame_rate,
            created_at=datetime.now().isoformat(timespec="seconds"),
            parent_ref=parent,
        )
        self._session_parents[job_id] = parent
        jobs.save_job(job)
        return job

    def import_job(self, job: jobs.MatteJob) -> None:
        try:
            self._set_status(f"Importing “{job.clip_name}”…")
            if job.parent_ref is None and job.id in self._session_parents:
                job.parent_ref = self._session_parents[job.id]
            imported = mt_import.import_job_to_parent(job)
            mt_import.cache_imported(imported)
            job.status = "imported"
            job.message = f"Imported {len(imported)} clip(s)"
            jobs.save_job(job)
            self.reload_jobs()
            self._set_status(
                f"Imported “{job.clip_name}” → {job.parent_name} "
                f"({len(imported)} clip(s)), cache requested."
            )
        except Exception as exc:
            self._alert(f"Import failed:\n{exc}")
            self._set_status("Import failed.")

    def delete_job(self, job: jobs.MatteJob) -> None:
        box = QMessageBox(None)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Embr Matte")
        box.setText(
            f"Delete job “{job.clip_name or job.id}”?\n"
            f"This removes the folder:\n{job.job_dir}"
        )
        box.setStandardButtons(
            QMessageBox.StandardButton.Cancel
            | QMessageBox.StandardButton.Yes
        )
        box.setDefaultButton(QMessageBox.StandardButton.Cancel)
        if box.exec() != QMessageBox.StandardButton.Yes:
            return
        try:
            jobs.delete_job(job)
            self._session_parents.pop(job.id, None)
            self.reload_jobs()
            self._set_status(f"Deleted job {job.id}.")
        except Exception as exc:
            self._alert(f"Delete failed:\n{exc}")
            self._set_status("Delete failed.")


def open_matte() -> None:
    def _factory() -> MatteWindow:
        return MatteWindow()

    embr_ui.show_singleton_window("_embr_matte", _factory)
