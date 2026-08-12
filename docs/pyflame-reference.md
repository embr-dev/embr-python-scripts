# PyFlame 参照メモ（Embr 自前ユーティリティ設計用）

Embr は **PyFlame を依存・同梱しない**。  
ただし「よく使う機能をすぐ呼べる」共通層を自作するため、[PyFlame](https://github.com/logik-portal/pyflame) の **構成と機能一覧だけ**を参考にする。

## ライセンス注意（重要）

| 項目 | 内容 |
|------|------|
| PyFlame | **GPL-3.0** |
| Embr (このリポ) | **MIT** |

- PyFlame の **ソースコードをコピー・改変して Embr に入れない**（クリーンルームで設計する）
- ローカル参照用クローンは `vendor/pyflame/`（**gitignore 対象・配布しない**）
- 参考にするのは API 表面・責務分割・フォルダ構成のアイデアまで

参照クローン:

```bash
git clone --depth 1 https://github.com/logik-portal/pyflame.git vendor/pyflame
```

---

## PyFlame が用意しているもの（概観）

実体はほぼ単一巨大モジュール:

```text
vendor/pyflame/lib/pyflame_lib.py   # ~880KB / クラス多数
```

スクリプト側は `from lib.pyflame_lib_<name> import *` で取り込み、ユーティリティは `pyflame.*`、UI は `PyFlameWindow` 等を直接 new する。

### A. ユーティリティ（`_PyFlame` → `pyflame`）

Embr でも優先して欲しい層。UI なしでも価値がある。

| カテゴリ | メソッド例 |
|----------|------------|
| ログ / 診断 | `print`, `print_title`, `print_list`, `print_dict`, `print_json`, `raise_type_error`, `raise_value_error` |
| 環境 | `get_flame_version`, `get_flame_python_packages_path`, `refresh_hooks` |
| UI 補助 | `cursor_busy`, `cursor_restore`, `pause`, `file_browser`, `open_in_finder`, `copy_to_clipboard` |
| 名前 | `generate_unique_name`, `generate_unique_node_names`, `iterate_name` |
| トークン / ショット | `resolve_tokens`, `resolve_shot_name`, `shot_name_from_clip`, `shot_name_from_batch_group` |
| Media Panel | `create_media_panel_folder(s)`, `create_media_panel_libraries`, `move_to_shot_folder`, `copy_to_shot_folder`, `find_by_tag`, `set_shot_tagging` |
| ファイルシステム | `create_file_system_folder(s)`, `create_temp_folder`, `cleanup_temp_folder`, `untar` |
| Export preset | `get_export_preset_names`, `get_export_preset_version`, `update_export_preset`, `convert_export_preset_name_to_path` |
| パッケージ | `python_package_local_install`, `verify_script_install` |
| 解像度スケール | `gui_resize`, `font_resize`, `window_resolution`（主に自前ウィジェット用） |

### B. 設定（`PyFlameConfig`）

スクリプトごとの JSON/設定の load / save / get_typed。Embr でも薄い `Config` を用意すると繰り返しが減る。

### C. Flame 風 Qt ウィジェット（PySide6）

`PyFlameButton`, `PyFlameEntry`, `PyFlameSlider`, `PyFlameWindow`, `PyFlameMessageWindow` など多数。  
見た目を Flame に寄せるためのスタイル・フォント（Montserrat）込み。

Embr では **最初から全部を再実装しない**。必要になった UI から段階的に足す。

### D. 推奨フォルダ構成（PyFlame 側）

```text
script_name/
├── script_name.py
├── lib/
│   └── pyflame_lib_script_name.py   # スクリプトごとにリネームコピー
└── assets/fonts/...
```

複数スクリプトが同じ共有フォルダに同居しても、ライブラリ名衝突を避けるための作法。

---

## Embr への落とし込み方針（案）

PyFlame の「全部入り巨大1ファイル」は避け、**小さく分割した MIT の共通層**にする。

```text
scripts/
  embr/                    # 共通ライブラリ（import 用）
    __init__.py
    version.py             # get_flame_version 等
    log.py                 # print / message area
    hooks.py               # refresh_hooks
    paths.py               # packages path, temp dirs
    names.py               # unique name helpers
    config.py              # 薄い設定 I/O
    ui/                    # 必要になったら追加（PySide6）
  my_tool/
    my_tool.py
```

### 優先実装順（提案）

1. **ログ + バージョン + hooks 再読込**（ほぼ全スクリプトで使う）
2. **パス / temp / unique name**
3. **config**
4. **Media Panel / token / shot**（ツールが増えてから）
5. **UI ウィジェット**（ダイアログが必要になったら）

### Embr で意識的に変えるとよい点

| PyFlame | Embr で良くする方向 |
|---------|---------------------|
| 1 ファイル巨大・`import *` | モジュール分割・明示 import |
| GPL・スクリプトごとに lib コピー | 共有 `embr` パッケージを1つ置く |
| UI と util が密結合 | util を UI 非依存に保つ |
| Flame 風見た目が主目的 | まず機能 util、UI は後追い |
| 2025.1+ 表記 | Embr は **2025.0+** |

---

## 参照元

- リポジトリ: https://github.com/logik-portal/pyflame
- サイト: https://logik-portal.com/pyflame/
- ローカル: `vendor/pyflame/`（clone 後）
