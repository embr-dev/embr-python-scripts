# スクリプト規約（Embr）

Flame **2025.0+** 向け。前提は [prerequisites.md](./prerequisites.md)、配置は [dev-setup.md](./dev-setup.md)。

tools / hooks を増やすときの共通ルール。迷ったらこの文書に戻る。

---

## 0. 言語と方針

| 対象 | 言語 |
|------|------|
| **`docs/`（このリポジトリのドキュメント）** | **日本語**（メンテ用。読むのは主に開発者） |
| **スクリプト内**（メニュー表示名・ログ・エラーメッセージ・コメント・docstring・識別子） | **英語** |

ユーザー層は日本人に限定しない。そのため **製品として Flame に出る文字列は英語**。ドキュメントは日本語でよい。

### 開発方針

| 方針 | 内容 |
|------|------|
| シンプル | 動く範囲で **最も単純な** 実装を選ぶ。過剰な抽象化・フレームワーク化は避ける |
| 確実さ | 検証してから出す。失敗しうる経路（版・パス・OS・選択型）は **必要なテストを細かく** 行う |
| プラットフォーム | **macOS** と **Rocky Linux** の両方で動くこと |
| エラーの明確さ | 失敗時は **何が・なぜ（分かる範囲で）・次に何を確認するか** を英語メッセージで出す。黙殺禁止 |

---

## 1. ディレクトリ構成

```text
scripts/
  embr/                 # 共通 util のみ（フック入口を置かない）
  embr_<tool>/          # 1 ツール = 1 ディレクトリ
    embr_<tool>.py      # フック入口（必須）
    …                   # ツール専用の補助モジュール（任意）
tools/                  # リポジトリ用シェル・生成スクリプト（Flame は読まない）
docs/                   # ドキュメント（日本語）
```

| 置き場 | 役割 | フック関数 |
|--------|------|------------|
| `scripts/embr/` | 共有ライブラリ | **禁止** |
| `scripts/embr_<tool>/` | 配布・メニューに出すツール | **ここだけ** |
| `tools/` | `run_flame_dev.sh` など | なし |

- 開発時のルートは `DL_PYTHON_HOOK_PATH` → `scripts/`（[dev-setup.md](./dev-setup.md)）。
- 一時確認用スクリプトを置く場合も、本番と同じ `embr_<name>/` 命名に揃える。確認後は削除してよい。

---

## 2. 命名

| 対象 | 規則 | 例 |
|------|------|-----|
| ツールディレクトリ | `embr_` + snake_case | `embr_batch_organize` |
| フック入口ファイル | ディレクトリ名と同じ `.py` | `embr_batch_organize/embr_batch_organize.py` |
| メニュー第1階層 | **`Embr`** | Main Menu → Embr → … |
| アクション表示名 | 短い英語 Title Case | `Organize Comp` |
| util モジュール | 短い snake_case | `embr.log`, `embr.paths` |

- プレフィックス `embr_` で公式・他社スクリプトと衝突しにくくする。
- `scripts/embr/` 内の util も basename が一意であること（`embr_paths.py` 等。`paths.py` / `ui.py` は使わない）

---

## 3. フック入口

1. **必要な** `get_*_custom_ui_actions` だけ定義する。
2. `execute` は `_` 始まりの関数、または同パッケージの明示的な公開関数。
3. `minimumVersion` は `"2025.0.0.0"` 以上。
4. 選択は型を確認してから触る。想定外は英語でログして return（ホストを落とさない）。

最小形:

```python
from __future__ import annotations

from embr import log, version


def _run(_selection) -> None:
    version.require_min("2025.0")
    log.info("Embr: hello")


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

詳細は [api/hooks.md](./api/hooks.md)。

---

## 4. `embr` util の使い方

```python
from embr import log, version, names, paths, hooks, ui
```

| ルール | 内容 |
|--------|------|
| import | 明示 import（`from embr import *` 禁止） |
| バージョン | 入口で `version.require_min("2025.0")` を推奨 |
| ログ | ユーザー向けは `embr.log`（文言は英語） |
| コンソール文字 | Flame コンソール向けは **ASCII 寄り**（非 ASCII は文字化け実績あり） |
| util 変更後 | `hooks.refresh()`（必要なら `invalidate=("embr",)`） |
| UI | 色・フォント・ロゴは **`embr.ui` 経由のみ**（直書き禁止） |
| PyFlame | **使わない・コピーしない**（[pyflame-reference.md](./pyflame-reference.md)） |

API: [embr-util.md](./embr-util.md)。

---

## 5. エラーと診断

問い合わせ・自分での切り分けができること。

| する | しない |
|------|--------|
| プレフィックス `Embr <Tool>: …` | 裸の `Error` / 空の catch |
| **何が**失敗したか（操作 + 対象） | 要約なしの traceback だけ |
| **なぜ**分かるか書く（パス欠落・型違い・版不足など） | 握りつぶして成功扱いにする |
| **次に確認すること**を短く | ユーザー経路での `except Exception: pass` |

例:

```text
Embr Organize Comp: cannot connect nodes - socket "Front" not found on node "comp01".
Check the schematic selection and socket names in the UI.
```

- 想定外例外: `log.error` で短い理由（英語）+ 端末には traceback。
- マジック戻り値より、明確な例外（例: util の `VersionError`）を優先。

---

## 6. シンプルさ

- 1 ツール = 1 仕事。万能ツールより小さなツールを複数。
- 第2の利用者が出るまでプラグイン基盤は作らない。
- 深い継承・遠回しな間接より、関数と薄いモジュール。
- 5〜10 行の重複は2回まで許容。3回目で共通化を検討。

---

## 7. クロスプラットフォーム（macOS + Rocky Linux）

| 項目 | 規則 |
|------|------|
| パス | `pathlib`。Flame / scripts 関連は `embr.paths` 経由 |
| ホーム / temp | `/Users/...` や `/home/...` だけのハードコード禁止 |
| シェル | `#!/usr/bin/env bash`。GNU 専用オプションはガードするか使わない |
| 改行 | リポジトリは LF |
| OS 分岐 | ヘルパーに閉じ、その経路は **両 OS でテスト** |

サポート OS は [prerequisites.md](./prerequisites.md) に合わせる。

---

## 8. テスト / 信頼性

| 層 | 期待 |
|----|------|
| 共有 util（`embr`） | 依存する挙動ごとに Flame 内チェック |
| 各ツール | 正常系・空/不正選択・エラー文の分かりやすさ |
| OS | ファイルシステムやシェルに触れるツールは macOS **と** Rocky |
| 回帰 | util 変更後、依存ツールを再確認 |

「自分の Mac だけで動いた」だけでパス/FS/シェル系をマージしない。

---

## 9. UI（PySide6）

- **PySide6 のみ**（PySide2 禁止）。
- 足りるなら Flame 組み込み（`flame.messages.show_in_dialog` / `flame.PyBrowser` など）。
- 独自 Qt は必要なときだけ。表示文言は英語。
- **ブランド**: Ash + Ember 色、**Figtree**（同梱 OFL）、ロゴは `embr.ui`。Satoshi は使わない。
- 公開ツールは `catalog/catalog.json` に登録（`python3 tools/gen_catalog.py`）。詳細は [script-manager.md](./script-manager.md)。

---

## 10. コードスタイル（当面）

| 項目 | 方針 |
|------|------|
| Python | 3.11。入口は `from __future__ import annotations` 推奨 |
| 型ヒント | 公開・やや複雑な API に付ける |
| 依存 | 標準ライブラリ + Flame 同梱 + `scripts/embr`。pip 依存は原則なし |
| ライセンス | MIT。ファイル先頭コメントは任意 |

リンタ固定（ruff 等）はツールが増えてからでよい。

---

## 11. ドキュメント

| 変更内容 | 更新先 |
|----------|--------|
| 前提・サポート | `docs/prerequisites.md` |
| util API | `docs/embr-util.md`（+ 必要なら英語 docstring） |
| 新ツール | `scripts/README.md` に1行 |
| Flame API の解釈 | `docs/api/` |

- **docs は日本語。**
- スクリプト内の docstring / ユーザー向け文言は **英語。**

---

## 12. 破壊的操作・確認（方針）

| 項目 | 方針 |
|------|------|
| 変更範囲 | デフォルトは **選択範囲のみ**。プロジェクト全体は明示が必要 |
| 確認ダイアログ | 削除・上書き・大量変更のときだけ |
| コミットメッセージ | **英語**（公開リポ・貢献者と揃える） |
| i18n | 当面なし（スクリプト表示は英語のみ） |

---

## 13. やってはいけないこと

- `scripts/embr/` に `get_*_custom_ui_actions` を置く
- PyFlame ソースのコピー／取り込み
- システム Python での `import flame` を正規の実行手順にする
- Dock 起動だけに頼る（env が付かない → `./tools/run_flame_dev.sh`）
- 秘密情報のコミット
- メニュー／エラーを日本語のみにする（スクリプト内は英語）

---

## 関連

- [prerequisites.md](./prerequisites.md)
- [dev-setup.md](./dev-setup.md)
- [embr-util.md](./embr-util.md)
- [api/hooks.md](./api/hooks.md)
- [script-manager.md](./script-manager.md)
- [scripts/README.md](../scripts/README.md)
