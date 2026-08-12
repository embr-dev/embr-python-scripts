# Python Hooks（Flame 2025）

Embr 開発向けに、公式 **Python Hooks Reference** / **Python Hooks Tips** と、ローカル同梱の `*_hook.py` を突合してまとめたもの。

| 項目 | 内容 |
|------|------|
| 対象 | Autodesk Flame Family **2025**（Embr は 2025.0+） |
| 一次情報（保存済み） | `docs/API Documentation/Python Hooks Reference/` |
| | `docs/API Documentation/Python Hooks Tips/` |
| 一次情報（インストール） | `/opt/Autodesk/.flamefamily_2025/python/*_hook.py` |
| | `/opt/Autodesk/.flamefamily_2025/python_utilities/examples/` |
| 公式 Help 表記の例 | `/opt/Autodesk/<PRODUCT>_<VERSION>/python/` |
| | Help 上の `python_examples` ≈ 実機の `python_utilities/examples` |

**重要:** Help の Reference は概要中心。各フックの引数・辞書キーの詳細は **同梱 `.py` 内コメントが正式仕様**。

---

## 1. 仕組みの要点

- Hooks はショット管理連携、アーカイブ監視、Batch 命名などへの差し込み点。
- **すべての hooks はデフォルトでブロッキング**（完了するまで Flame が待つ）。非同期にしたい場合は Tips の Threading パターンを使う。
- Flame は複数の `.py` を読み、**サポートされているメソッドを探す**。実装をファイル分割してよい。
- 同じカスタムアクション名が複数ファイルにあっても、**同じサブメニュー名でグループ化**される。同名アクションが同一サブメニューに重複すると、名前に番号が付く。
- ファイル名はパス横断で **一意** にする（Python は同名モジュールを複数場所から同時に扱えない）。

---

## 2. 配置場所（どこに置くか）

### 公式に記載されている場所

| スコープ | パス |
|----------|------|
| アプリ版 | `/opt/Autodesk/<PRODUCT>_<VERSION>/python/` |
| 共有（全版） | `/opt/Autodesk/shared/python/` |
| ユーザー (Linux) | `/home/<user>/flame/python` |
| ユーザー (macOS) | `/Users/<user>/Library/Preferences/Autodesk/flame/python` |
| プロジェクト | `/opt/Autodesk/project/<project>/python` |
| 追加 | 環境変数 `DL_PYTHON_HOOK_PATH` |

プロジェクト配下の python は、将来プロジェクトを新バージョンへ変換する際にコピーされる、と Help に記載あり。

### このマシン（2025）の実例

| 種類 | パス |
|------|------|
| Family / 同梱 hooks | `/opt/Autodesk/.flamefamily_2025/python/` |
| 例 | `/opt/Autodesk/.flamefamily_2025/python_utilities/examples/` |
| 共有 | `/opt/Autodesk/shared/python/` |
| ユーザー | `~/Library/Preferences/Autodesk/flame/python` |

### Embr の開発配置

`DL_PYTHON_HOOK_PATH` → リポジトリの `scripts/`（手順は [dev-setup.md](../dev-setup.md)）。

---

## 3. 環境変数

### `DL_PYTHON_HOOK_PATH`

- 既定以外のディレクトリを hooks 走査対象にする。
- **PATH と同様**に扱え、**複数パスを `:` 区切り**できる。
- 左から順に読み、**未定義の hooks を後続パスから補完**する。

```bash
export DL_PYTHON_HOOK_PATH=/share_1/dev/python_hooks/test:/share_1/dev/python_hooks/production
```

上例では `test` を先に読み、足りない hooks を `production` から読む。

### `DL_DEBUG_PYTHON_HOOKS`

```bash
export DL_DEBUG_PYTHON_HOOKS=1
```

有効にするとシェルへ詳細出力:

- どのファイルからどの hook が載ったか
- 発火した hook に渡されたデータ

---

## 4. 再読込（開発時）

| 方法 | 内容 |
|------|------|
| ホットキー | 既定 **Ctrl+Shift+P+H**（Hotkey Editor 名: **Scan for python hooks**） |
| メニュー | Main Menu → Python → Rescan Python Hooks |
| API | `flame.execute_shortcut("Rescan Python Hooks")`（Embr: `embr.hooks.refresh()`） |

注意: Rescan は hook ファイルの再走査に加え、既ロードモジュールを **`importlib.reload`** する（ログ: `Reloading '…'`）。  
Embr の `hooks.refresh()` は **既定で Rescan のみ**（`sys.modules` を消さない）。basename の `embr_*.py` を消してから Rescan すると `ImportError: module … not in sys.modules` が連発する。

---

## 5. Custom UI Actions（Embr で最頻出）

メニュー／コンテキストに項目を足す hooks。同梱: `custom_actions_hook.py`。

### 入口関数

| 関数 | 出る場所 | 選択オブジェクトの注意 |
|------|----------|------------------------|
| `get_media_panel_custom_ui_actions` | Media Panel | Flame オブジェクトのタプル |
| `get_main_menu_custom_ui_actions` | Flame Main Menu | 同上 |
| `get_mediahub_files_custom_ui_actions` | MediaHub Files | 選択のパスは `.path` |
| `get_mediahub_projects_custom_ui_actions` | MediaHub Projects | 選択の UID は `.uid` |
| `get_mediahub_archives_custom_ui_actions` | MediaHub Archives | **選択は返らない**（操作トリガのみ。内容変更は不可） |
| `get_timeline_custom_ui_actions` | Timeline コンテキスト | Flame オブジェクトのタプル |
| `get_batch_custom_ui_actions` | Batch コンテキスト | 同上 |
| `get_action_custom_ui_actions` | Batch 内 Action ノード | 同上 |

### 戻り値の形

**グループ辞書のリスト**（またはタプル）。

グループ:

| キー | 必須 | 意味 |
|------|------|------|
| `name` | ほぼ必須 | サブメニュー／グループ名 |
| `actions` | ほぼ必須 | アクション辞書の列 |
| `hierarchy` | 任意 (2023.2+) | 親サブメニュー名のリスト |
| `order` | 任意 (2023.2+) | 表示順 |
| `separator` | 任意 (2023.2+) | 例: `"below"` |

アクション:

| キー | 必須 | 意味 |
|------|------|------|
| `name` | 必須 | 項目名（`caption` 未指定時の表示にも使う） |
| `caption` | 任意 | 表示ラベル |
| `execute` | 任意* | `callable(selection)`。`selection` は選択 Flame オブジェクトのタプル |
| `isEnabled` | 任意 | `bool` または `callable(selection)`。省略時 True |
| `isVisible` | 任意 | `bool` または `callable(selection)`。省略時 True |
| `minimumVersion` | 任意 | 表示する最低バージョン（含む） |
| `maximumVersion` | 任意 | 表示する最高バージョン（含む） |
| `order` | 任意 (2023.2+) | 項目順 |
| `separator` | 任意 (2023.2+) | 区切り |

\*メニュー項目として動かすなら実質必須。

### 最小例（Main Menu）

```python
import flame


def _run(selection):
    flame.messages.show_in_console("hello", "info", 3)


def get_main_menu_custom_ui_actions():
    return [
        {
            "name": "Embr",
            "actions": [
                {
                    "name": "Hello",
                    "execute": _run,
                    "minimumVersion": "2025.0.0.0",
                }
            ],
        }
    ]
```

### Media Panel のスコープ例（公式 Reference より）

```python
def get_media_panel_custom_ui_actions():
    def scope_reelgroup(selection):
        import flame
        for item in selection:
            if isinstance(item, flame.PyReelGroup):
                return True
        return False

    def create_reel(selection):
        import flame
        for item in selection:
            reel = item.create_reel("New Reel")
            reel.colour = reel.parent.colour

    return [
        {
            "name": "Python: Reel Group",
            "actions": [
                {
                    "name": "Create Reel",
                    "isVisible": scope_reelgroup,
                    "execute": create_reel,
                }
            ],
        }
    ]
```

### selection のタイミング（Embr Rename 方針）

`isVisible` / `isEnabled` / `execute` はいずれも `selection` を受け取るが、**クリック時の `execute` 引数は右クリック時と異なる／空になることがある**（フォーカス移動や PySide ダイアログなど）。

Embr Rename は次で固定する:

1. `isVisible(selection)` で面ごとに `tuple(selection)` をキャッシュする
2. `execute` の引数は使わず、キャッシュだけを Rename 対象にする
3. ダイアログ表示後にライブ選択を取り直さない

---

### 階層メニュー（2023.2+）

`hierarchy` / `order` / `separator` を使う。公式例: `python_utilities/examples/custom_menu_structure.py`。  
Embr は 2025.0+ なので、新規メニューはこれらのキーを使ってよい。

### バージョン制限

公式例: `version_scoping_hooks.py`。

- アクション辞書の `minimumVersion` / `maximumVersion`（**hook スコープ**: 非対応版では隠す）
- 関数への `minimum_version` / `maximum_version` 付与（**function スコープ**: 非対応版では **ロード自体しない**）

形式例: `2025`, `2025.0`, `2025.0.1`, `2025.0.0.0`  
省略した桁はワイルドカード的（例: `2025.0` ならその下の patch は通る）。

function スコープの方が強い（狭い function 制限を、広い hook 制限で上書きできない）。

Embr 推奨: アクションに `"minimumVersion": "2025.0.0.0"` を付ける。

---

## 6. 同梱 hook ファイル一覧（ローカル 2025）

仕様の詳細コメントは各ファイル先頭〜各 `def` 上にある。

### `hook.py` — アプリ／タイムライン命名など

| 関数 | 概要 |
|------|------|
| `app_initialized(project_name)` | アプリ初期化後・プロジェクト変更時。Tips ではプロジェクト名共有に推奨 |
| `app_exited(info)` | 終了時。`info` に homeDirectory / version など |
| `user_changed(info)` | ユーザー切替 |
| `render_ended(...)` | シーケンスレンダー終了 |
| `playback_ended(...)` | 再生終了 |
| `preview_window_config_changed(...)` | プレビューデバイス変更 |
| `timeline_default_shot_name` | ショット名デフォルト |
| `timeline_default_marker_name` / `_comment` | マーカー |
| `timeline_default_segment_marker_name` / `_comment` | セグメントマーカー |
| `timeline_default_gap_bfx_name` | Gap BFX 名 |
| `default_reference_name` | リファレンス名 |

### `project_hook.py`

| 関数 | 概要 |
|------|------|
| `project_changed` | プロジェクト変更 |
| `project_changed_dict` | 辞書付きプロジェクト変更 |
| `project_saved` | 保存時 |

### `batch_hook.py`

| 関数 | 概要 |
|------|------|
| `batch_setup_loaded` / `batch_setup_saved` | setup 読込／保存 |
| `batch_setup_iterated_pre` / `_post` | イテレーション前後 |
| `batch_render_begin` / `_end` | レンダー |
| `batch_burn_begin` / `_end` | Burn |
| `batch_export_begin` / `_end` | Batch からの export |
| `batch_default_iteration_name` | イテレーション名 |
| `batch_default_render_node_name` | Render ノード名 |
| `batch_default_write_file_node_name` | Write File ノード名 |
| `batch_default_group_path` / `batch_default_iteration_path` | パス |

### `export_hook.py` — 書き出し（呼び出し順が重要）

| 順 | 関数 | 備考 |
|----|------|------|
| 1 | `pre_custom_export` | 任意。`get_custom_export_profiles` 由来のカスタム時 |
| 2 | `pre_export` | 常に。通常は Export 窓表示時。カスタム時は 1 の後 |
| 3 | `pre_export_sequence` | 常に。シーケンス書き込み前 |
| 4 | `pre_export_asset` | 常に。FG は全 asset を一括、BG は Backburner 投入ごと |
| 5 | `post_export_asset` | 常に。Backburner 側実行もあり（`use_backburner_post_export_asset`） |
| 6 | `post_export_sequence` | 常に |
| 7 | `post_export` | 常に |
| 8 | `post_custom_export` | 任意。カスタム時、7 の後 |

その他:

| 関数 | 概要 |
|------|------|
| `use_backburner_post_export_asset` | post asset を Backburner でやるか |
| `export_overwrite_file` | 上書き判断 |
| `get_custom_export_profiles` | カスタム export プロファイル／メニュー |

各関数の `info` 辞書キーは `export_hook.py` コメントが正。カスタム export では `destinationPath` / `presetPath` / `abort` などを書き換え可能。

### `archive_hook.py`

| 関数 | 概要 |
|------|------|
| `archive_restored` | リストア完了 |
| `archive_completed` | アーカイブ完了 |
| `archive_segment_completed` | セグメント完了 |
| `archive_selection_updated` | 選択更新 |

### `tokens_hook.py`

| 関数 | 概要 |
|------|------|
| `get_custom_token_list(context)` | トークンウィジェット用。`context == "Browsing"` など。戻りは `{"name","displayName"}` のタプル。Browsing の name は `{token}` 形式 |

### `custom_actions_hook.py`

セクション 5 参照。

---

## 7. Tips からの開発 Tips

### プロジェクト名の共有

`app_initialized(project_name)` でグローバルに保持し、他 hooks から読む。

```python
global_project_name = ""


def app_initialized(project_name):
    global global_project_name
    global_project_name = project_name  # Tips 原文の == は誤記。代入は =
```

### Threading（非ブロッキング）

重い処理は `threading.Thread` で逃がし、`atexit` で `join` するパターンが Tips に記載。`render_ended` などが例。UI／`flame` API を別スレッドから触るのは注意（基本はメインスレッド想定）。

### Locked Shared Libraries と export

Shared Library がロックされていても export hooks のコンテキストメニューは使える。ただしロック中に、プリセットが再インポートする設定で、ソースがライブラリ内にあると **再インポートは静かに失敗**する。

### Wiretap Python API

- 推奨: `from adsk import libwiretapPythonClientAPI`
- 実体: `/opt/Autodesk/python/<VERSION>/lib/python<PY>/site-packages/adsk/`
- 旧: `/opt/Autodesk/<PRODUCT>_<VERSION>/python/` への symlink（後方互換）。`import libwiretapPythonClientAPI` は更新推奨

### サードパーティ pip

Flame 同梱 Python: `/opt/Autodesk/python/<VERSION>/`  
pip: `/opt/Autodesk/python/<VERSION>/bin/pip`  
システム Python を汚さないこと。

---

## 8. 命名の歴史（読むとき用）

2020 で PEP8 化。旧名は当面サポートと Help 記載あり。Embr は新名のみ使う。

| 旧 | 新 |
|----|-----|
| `getCustomUIAction()` | `get_media_panel_custom_ui_actions()` など |
| `customUIAction()` | **非推奨**（上記へ移行） |
| custom actions は `hook.py` 内 | → `custom_actions_hook.py` |

---

## 9. Embr での実務チェックリスト

1. 入口は必要な `get_*_custom_ui_actions` だけ定義する（util パッケージにフック名を書かない）
2. `minimumVersion`: `"2025.0.0.0"`
3. 開発は `DL_PYTHON_HOOK_PATH=.../scripts` + `./tools/run_flame_dev.sh`
4. 変更反映は Rescan（必要なら `embr.hooks.refresh()`）
5. ログは `embr.log`（ASCII 推奨。Flame コンソールの文字化け回避）
6. 詳細引数が必要になったら **同梱 `*_hook.py` を開く**（この doc より詳しい）

---

## 10. 参照

- 保存 HTML: `docs/API Documentation/Python Hooks Reference/`
- 保存 HTML: `docs/API Documentation/Python Hooks Tips/`
- オンライン: [Python Hooks Reference](https://help.autodesk.com/view/FLAME/2025/ENU/?guid=Flame_API_Python_Hooks_Reference_html)
- ローカル: `/opt/Autodesk/.flamefamily_2025/python/`
- 例: `/opt/Autodesk/.flamefamily_2025/python_utilities/examples/`
- Embr: [dev-setup.md](../dev-setup.md), [embr-util.md](../embr-util.md)
