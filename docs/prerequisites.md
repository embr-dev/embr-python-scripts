# Flame 2025+ Python スクリプト開発 — 前提条件

Embr Python scripts の開発前提をまとめた文書です。  
対象は **Autodesk Flame Family 2025.0 以降**（2025.0+）。

調査時点の参照環境例: ローカル `Flame 2025`（同梱 Python `/opt/Autodesk/python/2025`）。

---

## 決定事項（このリポジトリ）

| 項目 | 値 |
|------|-----|
| 最低サポート | **Flame 2025.0+** |
| 実行 Python | Flame 同梱 **Python 3.11**（例: 3.11.5） |
| UI バインディング | **PySide6**（PySide2 非対応） |
| API | 組み込み `flame` モジュール（Flame プロセス内のみ） |
| 対応 OS | Rocky Linux / macOS |
| PyFlame | **使用しない**（GPL。機能面は参考にしつつ Embr 自前の共通層を作る） |
| 開発時のフック配置 | **`DL_PYTHON_HOOK_PATH` → `scripts/`**（公式機能。手順は [dev-setup.md](./dev-setup.md)） |

関連ドキュメント:

- [dev-setup.md](./dev-setup.md) — `DL_PYTHON_HOOK_PATH` の出典と試し方
- [pyflame-reference.md](./pyflame-reference.md) — PyFlame 参照メモ（Embr util 設計用）
- [api/hooks.md](./api/hooks.md) — Python Hooks（公式 + 同梱突合）
- [api/getting-started.md](./api/getting-started.md) — Console / 実行 / 最初のスクリプト
- [api/](./api/) — flame モジュール索引・Recipes など
- [embr-util.md](./embr-util.md) — `scripts/embr` 共通 util
- [conventions.md](./conventions.md) — スクリプト／パッケージ規約

---

## 1. 実行モデル

- スクリプトは **Flame 起動中の組み込み Python** で動く。
- 外部のシステム Python（例: macOS の `/usr/bin/python3`）から `import flame` してアプリを操作することは **できない**。
- エディタでの編集は外部でよいが、**実行・検証は Flame 内**（または起動時フック経由）が必須。
- 型チェックやリンター用に、開発マシンへ別途 Python 3.11 を入れるのは問題ない（実行環境とは分離する）。

### Flame 同梱 Python の場所（例）

```text
/opt/Autodesk/python/<version>/bin/python3
/opt/Autodesk/python/<version>/lib/python3.11/site-packages
```

ローカル実測例（2025）:

- Python **3.11.5**
- PySide6 **6.5.2**

---

## 2. スクリプト配置（Hooks）

Flame は起動時に複数ディレクトリの `.py` を走査する。

| スコープ | パス |
|----------|------|
| ユーザー | Linux: `/home/<user>/flame/python`  
| | macOS: `/Users/<user>/Library/Preferences/Autodesk/flame/python` |
| プロジェクト | `/opt/Autodesk/project/<project>/python` |
| アプリ版 | `/opt/Autodesk/<app>_<version>/python` |
| 共有（全ユーザー・複数版） | `/opt/Autodesk/shared/python` |
| 追加パス | 環境変数 `DL_PYTHON_HOOK_PATH` |

### 開発時の配置（決定）

インストール本体や共有フォルダを汚さず、リポジトリの `scripts/` を読ませる。

1. **`DL_PYTHON_HOOK_PATH`** を `scripts/` に向ける ← **採用**（公式。詳細は [dev-setup.md](./dev-setup.md)）
2. symlink は必要になったときだけ（下記「symlink とは」）

反映方法: Flame 内 **Main Menu → Python → Rescan Python Hooks**（多くの場合、再起動不要）。  
起動は `./tools/run_flame_dev.sh`（環境変数付き）を使う。

### Centralized Components（2025+）

スタジオ全体で共有パスを `sysconfig.cfg` から一元管理できる。  
共有 python の指定は **1 パスのみ**。複数置きたい場合は user / project 層や `DL_PYTHON_HOOK_PATH` で足す。

---

## 3. フック API の基本

同梱リファレンス（インストール先の例）:

- `/opt/Autodesk/.flamefamily_2025/python/custom_actions_hook.py`
- `/opt/Autodesk/.flamefamily_2025/python_utilities/examples/`

代表的なカスタム UI フック:

- `get_media_panel_custom_ui_actions`
- `get_main_menu_custom_ui_actions`
- `get_batch_custom_ui_actions`
- `get_timeline_custom_ui_actions`
- `get_action_custom_ui_actions`
- MediaHub / archive 系など

メニュー定義の主なキー: `name`, `actions`, `execute`, `isVisible`, `isEnabled`, `hierarchy`, `minimumVersion`, `maximumVersion` など。

最小例（Batch コンテキストメニュー）:

```python
import flame


def create_node(selection):
    flame.batch.create_node("Colour Correct")


def get_batch_custom_ui_actions():
    return [
        {
            "hierarchy": [],
            "actions": [
                {
                    "name": "Add Color Correct Node",
                    "execute": create_node,
                }
            ],
        }
    ]
```

---

## 4. 2025 での互換性の断絶（必須）

Flame **2025.0** から:

- **PySide2 → PySide6**（`from PySide2 import ...` は動作しない）
- UI 周りの API 差分あり（例）:
  - `QDesktopWidget` → `QGuiApplication.primaryScreen()`
  - `setMargin` → `setContentsMargins`
  - `QAction` の所属モジュール変更

本リポジトリは **2025.0+ のみ** を対象とし、**PySide6 固定**とする（2024 以前との両立はしない）。

公式: [What's New in 2025 — Python / PySide6](https://help.autodesk.com/cloudhelp/2026/ENU/Flame-WhatsNew/files/Previous-Releases/What-s-New-in-Flame-Family-2025/What-s-New-in-2025/wn-2025-python-api.html)

---

## 5. Flame 2025.0 と 2025.1 の違い

### スクリプト開発の土台としての差

| 観点 | 2025.0 | 2025.1 |
|------|--------|--------|
| Python 3.11 | ○ | ○ |
| PySide6 | ○（ここで切り替え） | ○ |
| `flame` Python API の基本 | ○ | ○（一部関数追加） |
| Centralized Components | ○（導入） | 強化（sysconfig の扱い・設定項目追加など） |

**結論:** Python / PySide / フック配置という「開発の前提」では、大きな断絶は **2025.0（PySide6 移行）**。  
2025.1 は機能追加・設定まわりの改善が中心で、**最低サポートを 2025.0+ にして問題ない**。

### 2025.1 で増えたもの（参考・スクリプト必須ではない）

- Centralized configuration の強化（例: sysconfig のシステムパス指定、Colour Coding / Channel Rules / Custom Resolutions の集約など）
- Python API の追加例: Batch Group の `clear_colour()`、Desktop クリアなど
- 製品機能（Timewarp ML、ML Inference など）— スクリプト前提とは別レイヤ

### PyFlame との関係

コミュニティライブラリ **PyFlame** の現行版は互換表記が **Flame 2025.1+**。  
これは **PyFlame 側のサポート下限**であり、Flame 本体のスクリプト機能が 2025.1 必須という意味ではない。  
Embr が PyFlame を必須依存にしない限り、対象は **2025.0+** のままでよい。

---

## 6. PyFlame を使うと何が便利か

[PyFlame](https://logik-portal.com/pyflame/)（Logik Portal / コミュニティ）は、Flame 向けの **UI ウィジェット + ユーティリティ集**。

### 便利になる点

1. **Flame 風 UI をすぐ作れる**  
   ボタン、スライダー、リスト、ウィンドウなどが Flame の見た目に寄せてある。素の PySide6 だけで同等にするのは手間が大きい。

2. **よく使う操作が関数化されている**  
   例: バージョン取得、フック再読込、ファイルブラウザ、トークン解決、Media Panel のフォルダ作成、メッセージ表示、busy カーソルなど。

3. **設定ファイルの読み書きヘルパー**  
   スクリプトごとの config 保存が楽になる。

4. **コミュニティスクリプトとの見た目・作法が揃いやすい**  
   Logik 系ツールと同じ UI 言語になり、ユーザーに馴染みやすい。

### 注意点・コスト

- 依存が増える（ライブラリ本体 + フォント資産、所定のフォルダ構成）
- ライセンスは **GPL-3.0**（Embr 本体が MIT の場合、同梱・再配布の方針を要確認）
- 現行 PyFlame は **2025.1+** 表記 — 採用するなら最低サポートを上げるか、PyFlame 利用スクリプトだけ 2025.1+ と明示する必要がある
- Autodesk 公式ではない（コミュニティ製・自己責任）

### Embr での扱い（決定）

- **PyFlame は使用・同梱しない**（GPL-3.0 と MIT の衝突を避ける）
- 同等の「よく使う機能をすぐ呼べる」層は **Embr 自前**で作る
- 設計の参考として PyFlame の API 表面・責務分割を見る → [pyflame-reference.md](./pyflame-reference.md)
- ローカル参照クローン: `vendor/pyflame/`（gitignore、配布しない）

---

## 7. symlink（シンボリックリンク）とは

**symlink** は、実体ファイル／フォルダへの「近道（エイリアス）」を作る仕組み。  
コピーではなく、別パスから同じ場所を参照する。

### なぜ開発で使うか

Flame は決まったディレクトリ（例: ユーザーの `.../flame/python`）しか見ない。  
リポジトリの `scripts/` をそこにコピーし続けるのは面倒なので、次のようにする:

```text
Flame が見るパス ──(symlink)──▶ リポジトリの scripts/
```

これで Git で編集したものが、そのまま Flame から読まれる。

### 例（macOS）

```bash
# ユーザー python ディレクトリへ、リポジトリの scripts をリンク
ln -s /Users/oue.isamu/Projects/embr-python-scripts/scripts \
  "$HOME/Library/Preferences/Autodesk/flame/python/embr-python-scripts"
```

確認:

```bash
ls -l "$HOME/Library/Preferences/Autodesk/flame/python"
```

`embr-python-scripts -> /Users/.../scripts` のように矢印が出ていれば symlink。

### コピーとの違い

| | コピー | symlink |
|--|--------|---------|
| 実体 | 2 つ存在する | 1 つ（リンク先のみ） |
| 編集の反映 | コピーし直す必要あり | 即反映 |
| 削除リスク | コピー側だけ消せる | リンク先を消すと参照切れ |

`DL_PYTHON_HOOK_PATH` でリポジトリを直接指定できる場合は、symlink なしでも同等のことができる。

---

## 8. 依存パッケージ

追加の pip パッケージが必要な場合:

- Flame の `site-packages` に入れる、またはスクリプト同梱にする
- **システムの pip / 別 venv を Flame 実行に混ぜない**

同梱 Python の pip 例:

```text
/opt/Autodesk/python/<version>/bin/pip3
```

---

## 9. 参照リンク

- [Python Hooks Reference (Flame 2026 Help)](https://help.autodesk.com/view/FLAME/2026/ENU/?guid=Flame_API_Python_Hooks_Reference_html)
- [What's New 2025 — Python / PySide6](https://help.autodesk.com/cloudhelp/2026/ENU/Flame-WhatsNew/files/Previous-Releases/What-s-New-in-Flame-Family-2025/What-s-New-in-2025/wn-2025-python-api.html)
- [Flame Family 2025 system requirements](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/flame-2025-sysreqs.html)
- [PyFlame (Logik Portal)](https://logik-portal.com/pyflame/)
- ローカル: `custom_actions_hook.py` / `python_utilities/examples/`

---

## 10. 次の実装ステップ

- [x] 対象バージョン **2025.0+**
- [x] PyFlame 不使用／参照のみ
- [x] 開発配置 **`DL_PYTHON_HOOK_PATH`**
- [x] `scripts/embr/` 共通ユーティリティ（log / version / hooks / paths / names）
- [x] `scripts/embr_util_test/` 削除
- [x] スクリプトのパッケージ構成規約（[conventions.md](./conventions.md)）
- [x] Script Manager（[script-manager.md](./script-manager.md)）
- [ ] （必要なら）追加の本番ツール / config
