# Embr util (`scripts/embr`)

Flame 2025.0+ 向けの共通ユーティリティ。MIT。PyFlame は使わない。

フック入口（`get_*_custom_ui_actions` など）は **このパッケージに定義しない**。

## モジュール

| Module | 役割 |
|--------|------|
| `embr.version` | → `embr_version.py` |
| `embr.log` | → `embr_log.py` |
| `embr.hooks` | → `embr_hooks.py` |
| `embr.paths` | → `embr_paths.py` |
| `embr.names` | → `embr_names.py` |
| `embr.ui` | → `embr_ui.py` |
| `embr.menus` | → `embr_menus.py`（defaults / prefs / Flame action dict） |

実ファイルは Flame の basename 衝突を避けるため `embr_*.py`。`from embr import paths` などは `__init__.py` がエイリアスする。

## 使い方

```python
from embr import log, version, names, paths, hooks, ui, menus

version.require_min("2025.0")
log.info("hello")
unique = names.unique_name("Clip", ["Clip", "Clip1"])  # -> "Clip2"
print(paths.flame_user_python(), paths.flame_shared_python())

# PySide6 window (frameless Embr chrome):
# title_bar = ui.prepare_embr_window(window, "Window Name")
# layout.addWidget(title_bar)
# # or theme only: ui.apply_embr_theme(window)

# Menu (order / visibility from defaults + user prefs):
# return menus.group("timeline", [menus.action("timeline", "rename_segments", ...)])

# 開発中に embr を直したあと:
hooks.refresh()  # embr を sys.modules から外してから Rescan
```

### メニュー（`embr.menus`）

| API | 役割 |
|-----|------|
| `menus.action(surface, id, execute=…)` | Flame アクション dict（ユーザー非表示なら `None`） |
| `menus.group(surface, […])` | `Embr` サブメニューで包む |
| `menus.effective_entries(surface)` | Preferences 用の合成一覧 |
| `menus.set_surface_prefs` / `reset_menu_prefs` | prefs 書き込み |

デフォルト表: `scripts/embr/menus/defaults.json`。ユーザー設定: [preferences.md](./preferences.md)。

## ブランド資産

| 資産 | 場所 |
|------|------|
| アクセント色 | Ember（`EMBR_EMBER` 等、`BRAND.md`） |
| ウィンドウ背景 | 無彩色ダーク（`EMBR_BG` / `EMBR_SURFACE`）— Flame 標準 UI に寄せる |
| タイトルバー | `ui.prepare_embr_window` / `ui.create_title_bar`（icon+Embr \| タイトル \| min/max/close） |
| シングルトン窓 | `ui.show_singleton_window("_embr_…", factory)` — QApplication に保持（hooks 再読込でも多重起動しない） |
| ロゴ | `scripts/embr/assets/logo/` |
| Figtree (OFL) | `scripts/embr/assets/fonts/Figtree/` |
| Material Icons (Apache-2.0) | `scripts/embr/assets/fonts/MaterialIcons/` — `ui.material_font` / タイトルバーボタン |

Satoshi はランタイムで使わない。UI は必ず `embr.ui` 経由。

### Material Icons の入れ方（方針）

PySide6 では次のどちらか（推奨はフォント同梱）:

1. **フォント + QRawFont（推奨）**  
   - [Google Material Icons](https://github.com/google/material-design-icons) の `MaterialIcons-Regular.ttf` を  
     `scripts/embr/assets/fonts/MaterialIcons/` に同梱（ライセンスファイルも）。  
   - **Qt の `QLabel`/`QPushButton` にコードポイントを直接載せると文字化けしやすい**ため、  
     `ui.material_icon_pixmap(codepoint, size)` で `QRawFont` 描画 → `QIcon` にする。  
   - タイトルバーの min/max/close はこの方式。

2. **SVG**  
   - 使うアイコンだけ SVG を `assets/icons/` に置き、既存の `logo_pixmap` と同様に `QSvgRenderer` で `QPixmap` / `QIcon` 化。  
   - アイコン数が少ないとき向き。

**やらないこと:** 実行時にネットからフォントを取る、システム依存のアイコン名だけに頼る。

実装タイミング: タイトルバーやボタンにアイコンが必要になったらフォント同梱 + `embr.ui` ヘルパーを追加する。

## 動作確認

```bash
PYTHONPATH=scripts /opt/Autodesk/python/2025/bin/python3 tools/test_script_manager.py
```

規約: [conventions.md](./conventions.md) · Script Manager: [script-manager.md](./script-manager.md)
