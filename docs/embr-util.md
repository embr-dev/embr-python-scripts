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

実ファイルは Flame の basename 衝突を避けるため `embr_*.py`。`from embr import paths` などは `__init__.py` がエイリアスする。

## 使い方

```python
from embr import log, version, names, paths, hooks, ui

version.require_min("2025.0")
log.info("hello")
unique = names.unique_name("Clip", ["Clip", "Clip1"])  # -> "Clip2"
print(paths.flame_user_python(), paths.flame_shared_python())

# PySide6 window (frameless Embr chrome):
# title_bar = ui.prepare_embr_window(window, "Window Name")
# layout.addWidget(title_bar)
# # or theme only: ui.apply_embr_theme(window)

# 開発中に embr を直したあと:
hooks.refresh()  # embr を sys.modules から外してから Rescan
```

## ブランド資産

| 資産 | 場所 |
|------|------|
| アクセント色 | Ember（`EMBR_EMBER` 等、`BRAND.md`） |
| ウィンドウ背景 | 無彩色ダーク（`EMBR_BG` / `EMBR_SURFACE`）— Flame 標準 UI に寄せる |
| タイトルバー | `ui.prepare_embr_window` / `ui.create_title_bar`（icon+Embr \| タイトル \| min/max/close） |
| ロゴ | `scripts/embr/assets/logo/` |
| Figtree (OFL) | `scripts/embr/assets/fonts/Figtree/` |

Satoshi はランタイムで使わない。UI は必ず `embr.ui` 経由。

## 動作確認

```bash
PYTHONPATH=scripts /opt/Autodesk/python/2025/bin/python3 tools/test_script_manager.py
```

規約: [conventions.md](./conventions.md) · Script Manager: [script-manager.md](./script-manager.md)
