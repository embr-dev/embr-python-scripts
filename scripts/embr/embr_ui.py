"""Embr UI theme helpers (brand colors, Figtree, logo, title bar).

Accent colors follow Embr BRAND.md (Ember). Window chrome backgrounds are
neutral dark grays so they sit closer to Flame's stock UI.
Runtime UI font is bundled Figtree (SIL OFL). Do not detect or load Satoshi.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Accent — Embr BRAND.md
EMBR_EMBER = "#E07020"
EMBR_EMBER_DEEP = "#C45C12"
EMBR_EMBER_BRIGHT = "#FF8A2B"

# Neutral chrome (Flame-adjacent; avoid brown ash fill in tool windows)
EMBR_BG = "#1C1D1F"
EMBR_SURFACE = "#28292C"
EMBR_SURFACE_RAISED = "#323338"
EMBR_BORDER = "#4C4E52"
EMBR_TEXT = "#E8E8E8"
EMBR_MUTED = "#9B9DA1"

# Frameless window chrome
EMBR_WINDOW_RADIUS = 6
EMBR_TITLE_ICON_SIZE = 24
EMBR_TITLE_BRAND_PT = 15
EMBR_TITLE_BRAND_GAP = 0

# Back-compat aliases used by older call sites / docs
EMBR_ASH = EMBR_BG
EMBR_ASH_COOL = EMBR_MUTED

_FONT_LOADED = False
_FONT_FAMILY = "Figtree"
_FONT_LOAD_ERROR: str | None = None

_MATERIAL_LOADED = False
_MATERIAL_FAMILY = "Material Icons"
_MATERIAL_LOAD_ERROR: str | None = None

# Material Icons PUA codepoints (ligatures are unreliable in Qt widgets).
ICON_MINIMIZE = "\ue931"  # minimize
ICON_MAXIMIZE = "\ue3c6"  # crop_square
ICON_RESTORE = "\ue3e0"  # filter_none
ICON_CLOSE = "\ue5cd"  # close

_ICON_TOOLTIPS = {
    ICON_MINIMIZE: "Minimize",
    ICON_MAXIMIZE: "Maximize",
    ICON_RESTORE: "Restore",
    ICON_CLOSE: "Close",
}


def assets_dir() -> Path:
    """Return ``scripts/embr/assets``."""
    return Path(__file__).resolve().parent / "assets"


def fonts_dir() -> Path:
    """Return the bundled Figtree directory."""
    return assets_dir() / "fonts" / "Figtree"


def material_icons_dir() -> Path:
    """Return the bundled Material Icons directory."""
    return assets_dir() / "fonts" / "MaterialIcons"


def logo_path(name: str = "embr-mark.svg") -> Path:
    """Return path to a bundled logo file under ``assets/logo/``."""
    return assets_dir() / "logo" / name


def _ensure_figtree_loaded() -> str:
    """Load bundled Figtree into Qt and return the family name."""
    global _FONT_LOADED, _FONT_FAMILY, _FONT_LOAD_ERROR
    if _FONT_LOADED:
        return _FONT_FAMILY

    try:
        from PySide6.QtGui import QFontDatabase
    except ImportError as exc:
        _FONT_LOAD_ERROR = f"Embr UI: PySide6 unavailable - {exc}"
        _FONT_LOADED = True
        _FONT_FAMILY = "Sans Serif"
        return _FONT_FAMILY

    families: list[str] = []
    font_dir = fonts_dir()
    for path in sorted(font_dir.glob("Figtree-*.ttf")):
        font_id = QFontDatabase.addApplicationFont(str(path))
        if font_id == -1:
            continue
        families.extend(QFontDatabase.applicationFontFamilies(font_id))

    if families:
        _FONT_FAMILY = families[0]
        _FONT_LOAD_ERROR = None
    else:
        _FONT_FAMILY = "Sans Serif"
        _FONT_LOAD_ERROR = (
            f"Embr UI: failed to load Figtree from {font_dir}. "
            "Using system UI font. Check that Figtree TTF files are installed."
        )
    _FONT_LOADED = True
    return _FONT_FAMILY


def font_load_error() -> str | None:
    """Return the last Figtree load error message, if any."""
    _ensure_figtree_loaded()
    return _FONT_LOAD_ERROR


def embr_font(point_size: int = 12, *, bold: bool = False) -> Any:
    """Return a ``QFont`` using bundled Figtree."""
    from PySide6.QtGui import QFont

    family = _ensure_figtree_loaded()
    font = QFont(family, point_size)
    if bold:
        font.setWeight(QFont.Weight.DemiBold)
    return font


def _ensure_material_icons_loaded() -> str:
    """Load bundled Material Icons and return the family name."""
    global _MATERIAL_LOADED, _MATERIAL_FAMILY, _MATERIAL_LOAD_ERROR
    if _MATERIAL_LOADED:
        return _MATERIAL_FAMILY

    try:
        from PySide6.QtGui import QFontDatabase
    except ImportError as exc:
        _MATERIAL_LOAD_ERROR = f"Embr UI: PySide6 unavailable - {exc}"
        _MATERIAL_LOADED = True
        _MATERIAL_FAMILY = "Sans Serif"
        return _MATERIAL_FAMILY

    path = material_icons_dir() / "MaterialIcons-Regular.ttf"
    font_id = QFontDatabase.addApplicationFont(str(path)) if path.is_file() else -1
    families: list[str] = []
    if font_id != -1:
        families.extend(QFontDatabase.applicationFontFamilies(font_id))

    if families:
        _MATERIAL_FAMILY = families[0]
        _MATERIAL_LOAD_ERROR = None
    else:
        _MATERIAL_FAMILY = "Sans Serif"
        _MATERIAL_LOAD_ERROR = (
            f"Embr UI: failed to load Material Icons from {path}. "
            "Window chrome falls back to text glyphs."
        )
    _MATERIAL_LOADED = True
    return _MATERIAL_FAMILY


def material_font(point_size: int = 18) -> Any:
    """Return a ``QFont`` for Material Icons codepoints."""
    from PySide6.QtGui import QFont

    font = QFont(_ensure_material_icons_loaded())
    font.setPixelSize(point_size)
    font.setStyleStrategy(
        QFont.StyleStrategy.PreferQuality | QFont.StyleStrategy.NoFontMerging
    )
    return font


def material_icon_text(codepoint: str) -> str:
    """Return a Material Icons glyph string (PUA codepoint)."""
    _ensure_material_icons_loaded()
    return codepoint


def logo_pixmap(name: str = "embr-mark.svg", width: int = 120) -> Any:
    """Load a logo as ``QPixmap`` (SVG via ``QSvgRenderer`` when needed)."""
    from PySide6.QtCore import QSize, Qt
    from PySide6.QtGui import QPainter, QPixmap
    from PySide6.QtSvg import QSvgRenderer

    path = logo_path(name)
    if not path.is_file():
        return QPixmap()

    if path.suffix.lower() == ".svg":
        renderer = QSvgRenderer(str(path))
        if not renderer.isValid():
            return QPixmap()
        size = renderer.defaultSize()
        if size.width() <= 0:
            size = QSize(width, width)
        aspect = size.height() / max(size.width(), 1)
        target = QSize(width, max(1, int(width * aspect)))
        pix = QPixmap(target)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        renderer.render(painter)
        painter.end()
        return pix

    pix = QPixmap(str(path))
    if pix.isNull():
        return pix
    return pix.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)


def stylesheet() -> str:
    """Return QSS using neutral chrome + Ember accents + Figtree."""
    family = _ensure_figtree_loaded()
    return f"""
    QWidget {{
        background-color: {EMBR_BG};
        color: {EMBR_TEXT};
        font-family: "{family}";
        font-size: 13px;
        outline: none;
    }}
    QMainWindow, QDialog {{
        background-color: {EMBR_BG};
        border: none;
        outline: none;
    }}
    QPushButton:focus, QComboBox:focus, QAbstractItemView:focus,
    QTableWidget:focus, QHeaderView:focus, QTableWidget::item:focus {{
        outline: none;
    }}
    QTableWidget::item:focus {{
        border: none;
    }}
    QLabel#embrStatus {{
        background-color: {EMBR_SURFACE};
        color: {EMBR_MUTED};
        border-top: 1px solid {EMBR_BORDER};
        padding: 6px 12px;
        font-size: 12px;
    }}
    QWidget#embrTitleBar {{
        background-color: {EMBR_SURFACE};
        border-bottom: 1px solid {EMBR_BORDER};
        border-top-left-radius: {EMBR_WINDOW_RADIUS}px;
        border-top-right-radius: {EMBR_WINDOW_RADIUS}px;
    }}
    QWidget#embrTitleBar QWidget,
    QWidget#embrTitleBar QLabel {{
        background-color: transparent;
    }}
    QLabel#embrBrand {{
        font-size: {EMBR_TITLE_BRAND_PT}px;
        font-weight: 600;
        color: {EMBR_TEXT};
    }}
    QLabel#embrWindowTitle {{
        font-size: 13px;
        font-weight: 500;
        color: {EMBR_TEXT};
    }}
    QLabel#embrRoot {{
        color: {EMBR_MUTED};
        font-size: 12px;
    }}
    QComboBox {{
        background-color: {EMBR_SURFACE_RAISED};
        color: {EMBR_TEXT};
        border: 1px solid {EMBR_BORDER};
        padding: 4px 8px;
        border-radius: 4px;
        min-width: 96px;
    }}
    QComboBox:hover {{
        background-color: #3C3E43;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {EMBR_SURFACE};
        color: {EMBR_TEXT};
        selection-background-color: {EMBR_EMBER_DEEP};
        border: 1px solid {EMBR_BORDER};
        outline: none;
    }}
    QPushButton#embrWinBtn, QPushButton#embrWinClose {{
        background-color: transparent;
        color: {EMBR_TEXT};
        border: none;
        padding: 0px;
        margin: 0px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
        border-radius: 0;
    }}
    QPushButton#embrWinBtn:hover {{
        background-color: {EMBR_SURFACE_RAISED};
    }}
    QPushButton#embrWinBtn:pressed {{
        background-color: #3C3E43;
    }}
    QPushButton#embrWinClose:hover {{
        background-color: #C42B2B;
        color: #FFFFFF;
    }}
    QPushButton#embrWinClose:pressed {{
        background-color: #A02020;
        color: #FFFFFF;
    }}
    QTableWidget {{
        background-color: {EMBR_SURFACE};
        alternate-background-color: {EMBR_SURFACE_RAISED};
        gridline-color: {EMBR_BORDER};
        selection-background-color: {EMBR_EMBER_DEEP};
        selection-color: {EMBR_TEXT};
        border: 1px solid {EMBR_BORDER};
        outline: none;
    }}
    QHeaderView::section {{
        background-color: {EMBR_SURFACE_RAISED};
        color: {EMBR_TEXT};
        padding: 6px;
        border: none;
        border-right: 1px solid {EMBR_BORDER};
        border-bottom: 1px solid {EMBR_BORDER};
    }}
    QPushButton {{
        background-color: {EMBR_SURFACE_RAISED};
        color: {EMBR_TEXT};
        border: 1px solid {EMBR_BORDER};
        padding: 8px 14px;
        border-radius: 4px;
    }}
    QPushButton:hover {{
        background-color: #3C3E43;
        border-color: #6A6C70;
    }}
    QPushButton:pressed {{
        background-color: #222326;
        border-color: {EMBR_EMBER};
        padding-top: 9px;
        padding-bottom: 7px;
    }}
    QPushButton#embrAccent {{
        background-color: {EMBR_EMBER};
        color: #1A1A1A;
        font-weight: 600;
        border: 1px solid {EMBR_EMBER_DEEP};
    }}
    QPushButton#embrAccent:hover {{
        background-color: {EMBR_EMBER_BRIGHT};
        border-color: {EMBR_EMBER};
    }}
    QPushButton#embrAccent:pressed {{
        background-color: {EMBR_EMBER_DEEP};
        border-color: #8A4008;
        color: #FFFFFF;
    }}
    QPushButton:disabled {{
        background-color: {EMBR_SURFACE};
        color: #5C5E62;
        border-color: #3A3C40;
    }}
    QPushButton#embrAccent:disabled {{
        background-color: #3A342E;
        color: #6E655C;
        border-color: #4A433C;
        font-weight: 600;
    }}
    """


def apply_no_focus_rect(widget: Any) -> None:
    """Suppress Qt's dotted focus rectangle on ``widget`` and descendants."""
    from PySide6.QtWidgets import QProxyStyle, QStyle

    class _NoFocusStyle(QProxyStyle):
        def drawPrimitive(self, element, option, painter, widget=None):  # noqa: N802
            if element == QStyle.PrimitiveElement.PE_FrameFocusRect:
                return
            super().drawPrimitive(element, option, painter, widget)

    style = _NoFocusStyle(widget.style())
    widget.setStyle(style)
    widget._embr_no_focus_style = style  # type: ignore[attr-defined]


def apply_embr_theme(widget: Any) -> None:
    """Apply Embr colors and Figtree to a Qt widget (typically a window)."""
    _ensure_material_icons_loaded()
    widget.setStyleSheet(stylesheet())
    widget.setFont(embr_font(12))
    apply_no_focus_rect(widget)


def _apply_rounded_mask(window: Any, radius: int = EMBR_WINDOW_RADIUS) -> None:
    """Clip a frameless window to a rounded rectangle (including children)."""
    from PySide6.QtCore import QEvent, QObject, QRectF
    from PySide6.QtGui import QPainterPath, QRegion

    def update_mask() -> None:
        if window.isMaximized() or window.isFullScreen():
            window.clearMask()
            return
        rect = QRectF(window.rect())
        if rect.width() <= 0 or rect.height() <= 0:
            return
        path = QPainterPath()
        path.addRoundedRect(rect, float(radius), float(radius))
        window.setMask(QRegion(path.toFillPolygon().toPolygon()))

    class _MaskFilter(QObject):
        def eventFilter(self, obj, event):  # noqa: N802
            if event.type() in (
                QEvent.Type.Resize,
                QEvent.Type.WindowStateChange,
                QEvent.Type.Show,
            ):
                update_mask()
            return False

    filt = _MaskFilter(window)
    window.installEventFilter(filt)
    window._embr_mask_filter = filt  # type: ignore[attr-defined]
    update_mask()


def create_title_bar(window: Any, title: str) -> Any:
    """Create a custom title bar: icon+Embr | title | min/max/close.

    The host ``window`` should be frameless (see ``prepare_embr_window``).
    """
    from PySide6.QtCore import QEvent, QObject, Qt
    from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget

    icon_px = EMBR_TITLE_ICON_SIZE
    bar_h = max(36, icon_px + 12)
    glyph_px = bar_h - 10
    bar = QWidget(window)
    bar.setObjectName("embrTitleBar")
    bar.setFixedHeight(bar_h)
    root = QHBoxLayout(bar)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    left = QWidget(bar)
    left_l = QHBoxLayout(left)
    left_l.setContentsMargins(8, 0, 8, 0)
    left_l.setSpacing(EMBR_TITLE_BRAND_GAP)
    icon = QLabel(left)
    pix = logo_pixmap("embr-icon.svg", width=icon_px)
    if not pix.isNull():
        icon.setPixmap(pix)
    icon.setFixedSize(icon_px, icon_px)
    left_l.addWidget(icon, 0, Qt.AlignmentFlag.AlignVCenter)
    brand = QLabel("Embr", left)
    brand.setObjectName("embrBrand")
    brand.setFont(embr_font(EMBR_TITLE_BRAND_PT, bold=True))
    left_l.addWidget(brand, 0, Qt.AlignmentFlag.AlignVCenter)
    left_l.addStretch(1)

    title_label = QLabel(title, bar)
    title_label.setObjectName("embrWindowTitle")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setFont(embr_font(13))

    right = QWidget(bar)
    right_l = QHBoxLayout(right)
    right_l.setContentsMargins(0, 0, 0, 0)
    right_l.setSpacing(0)
    right_l.addStretch(1)

    def _win_btn(glyph: str, object_name: str) -> QPushButton:
        btn = QPushButton(material_icon_text(glyph), right)
        btn.setObjectName(object_name)
        btn.setFont(material_font(glyph_px))
        btn.setCursor(Qt.CursorShape.ArrowCursor)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn.setFixedSize(bar_h, bar_h)
        btn.setToolTip(_ICON_TOOLTIPS.get(glyph, ""))
        return btn

    btn_min = _win_btn(ICON_MINIMIZE, "embrWinBtn")
    btn_max = _win_btn(ICON_MAXIMIZE, "embrWinBtn")
    btn_close = _win_btn(ICON_CLOSE, "embrWinClose")
    right_l.addWidget(btn_min)
    right_l.addWidget(btn_max)
    right_l.addWidget(btn_close)

    # Equal side columns keep the title optically centered.
    side_w = max(148, bar_h * 3)
    left.setFixedWidth(side_w)
    right.setFixedWidth(side_w)
    root.addWidget(left, 0)
    root.addWidget(title_label, 1)
    root.addWidget(right, 0)

    state: dict[str, Any] = {"drag_pos": None}
    chrome_btns = {btn_min, btn_max, btn_close}

    def _minimize() -> None:
        window.showMinimized()

    def _toggle_max() -> None:
        if window.isMaximized():
            window.showNormal()
            btn_max.setText(material_icon_text(ICON_MAXIMIZE))
            btn_max.setToolTip(_ICON_TOOLTIPS[ICON_MAXIMIZE])
        else:
            window.showMaximized()
            btn_max.setText(material_icon_text(ICON_RESTORE))
            btn_max.setToolTip(_ICON_TOOLTIPS[ICON_RESTORE])

    def _close() -> None:
        window.close()

    btn_min.clicked.connect(_minimize)
    btn_max.clicked.connect(_toggle_max)
    btn_close.clicked.connect(_close)

    class _DragFilter(QObject):
        def eventFilter(self, obj, event):  # noqa: N802
            if obj in chrome_btns:
                return False
            et = event.type()
            if et == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    state["drag_pos"] = (
                        event.globalPosition().toPoint()
                        - window.frameGeometry().topLeft()
                    )
            elif et == QEvent.Type.MouseMove:
                if state["drag_pos"] is None:
                    return False
                if event.buttons() & Qt.MouseButton.LeftButton:
                    if not window.isMaximized():
                        window.move(
                            event.globalPosition().toPoint() - state["drag_pos"]
                        )
            elif et == QEvent.Type.MouseButtonRelease:
                state["drag_pos"] = None
            elif et == QEvent.Type.MouseButtonDblClick:
                if event.button() == Qt.MouseButton.LeftButton:
                    _toggle_max()
                    return True
            return False

    drag_filter = _DragFilter(bar)
    for w in (bar, left, icon, brand, title_label, right):
        w.installEventFilter(drag_filter)
    bar._embr_drag_filter = drag_filter  # type: ignore[attr-defined]

    bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    bar._embr_title_label = title_label  # type: ignore[attr-defined]
    return bar


def prepare_embr_window(window: Any, title: str) -> Any:
    """Apply frameless chrome + theme; return the title bar widget to insert at top."""
    from PySide6.QtCore import Qt

    window.setWindowTitle(title)
    window.setWindowFlags(
        Qt.WindowType.Window
        | Qt.WindowType.FramelessWindowHint
        | Qt.WindowType.WindowSystemMenuHint
        | Qt.WindowType.WindowMinimizeButtonHint
        | Qt.WindowType.WindowMaximizeButtonHint
        | Qt.WindowType.WindowStaysOnTopHint
    )
    apply_embr_theme(window)
    _apply_rounded_mask(window, EMBR_WINDOW_RADIUS)
    return create_title_bar(window, title)


def set_title_bar_title(title_bar: Any, title: str) -> None:
    """Update the centered title text on a bar from ``create_title_bar``."""
    label = getattr(title_bar, "_embr_title_label", None)
    if label is not None:
        label.setText(title)
