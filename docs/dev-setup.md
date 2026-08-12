# 開発セットアップ — `DL_PYTHON_HOOK_PATH`

開発中は、Flame インストール先や `/opt/Autodesk/shared/python` を汚さず、このリポジトリの `scripts/` を読ませる。  
公式に用意されているのが環境変数 **`DL_PYTHON_HOOK_PATH`**。

---

## 出典（ソース）

### 1. Autodesk 公式ドキュメント（Hooks Reference）

Flame Family の **Python Hooks Reference** に、既定パス以外を走査させる方法として記載されている。

- Help: [Python Hooks Reference](https://help.autodesk.com/view/FLAME/2026/ENU/?guid=Flame_API_Python_Hooks_Reference_html)  
  （2025 版も同内容: [FLAME/2025](https://help.autodesk.com/view/FLAME/2025/ENU/?guid=Flame_API_Python_Hooks_Reference_html)）

公式 Help の該当セクション要旨（Autodesk Community 上の引用・サポート回答でも同文）:

> It is possible to make Flame scan a directory other than `/opt/Autodesk/<app>_<version>/python` for `.py` files by setting the `DL_PYTHON_HOOK_PATH` environment variable to the desired path.

あわせて記載される既定の走査先:

| スコープ | パス |
|----------|------|
| ユーザー (macOS) | `/Users/<user>/Library/Preferences/Autodesk/flame/python` |
| ユーザー (Linux) | `/home/<user>/flame/python` |
| プロジェクト | `/opt/Autodesk/project/<project>/python` |
| アプリ版 | `/opt/Autodesk/<app>_<version>/python` |
| 共有 | `/opt/Autodesk/shared/python` |

参考スレ（公式文の引用あり）:  
[Flare 2026.1 (macOS) – Python script search paths](https://forums.autodesk.com/t5/flame-forum/flare-2026-1-macos-need-confirmation-of-python-script-search/td-p/13865341)

### 2. Autodesk 製品同梱の実コード（Shotgun / Flow Production Tracking）

Flame に同梱される Toolkit 統合が、フック登録に同じ変数を使っている。

このマシン上の例:

```text
/opt/Autodesk/presets/2025/shotgun/README.md
/opt/Autodesk/presets/2025/shotgun/bundle_cache/app_store/tk-flame/v1.19.0/engine.py
```

`engine.py` より:

```python
flame_hooks_folder = os.path.join(self.disk_location, self.FLAME_HOOKS_FOLDER)
sgtk.util.append_path_to_env_var("DL_PYTHON_HOOK_PATH", flame_hooks_folder)
```

`presets/2025/shotgun/README.md` の例:

```bash
export DL_PYTHON_HOOK_PATH='/tmp/tk-plugin-flame/flame_hooks'
```

→ Autodesk 自身の統合でも使っている **公式の仕組み**。

### 3. Autodesk スタッフによる補足（コミュニティ）

Centralized Components（`sysconfig.cfg`）の共有 python は **1 パスのみ**だが、追加の走査先として `DL_PYTHON_HOOK_PATH` を使える、と Autodesk 側が明言している。

- [Centralized components & multiple paths in 2025 (Logik Forums)](https://forum.logik.tv/t/centralized-components-multiple-paths-in-2025/10528)

---

## 試し方（このリポジトリ）

### 1. スモークテスト用スクリプト

次を配置済み:

```text
scripts/embr_smoke_test/embr_smoke_test.py
```

Flame の **Main Menu** に `Embr / Smoke Test` が出れば、フックパスが効いている。

### 2. 環境変数を付けて Flame を起動

リポジトリルートで:

```bash
./tools/run_flame_dev.sh
```

中身は次と同等:

```bash
export DL_PYTHON_HOOK_PATH="/Users/oue.isamu/Projects/embr-python-scripts/scripts"
/opt/Autodesk/.flamefamily_2025/bin/startApplication
```

または手動:

```bash
export DL_PYTHON_HOOK_PATH="$PWD/scripts"
/opt/Autodesk/.flamefamily_2025/bin/startApplication
```

### 3. 確認手順

1. 上記で Flame を起動（**環境変数付きのターミナルから**起動すること。Dock アイコン起動では変数が付かない）
2. プロジェクトを開く
3. Flame Main Menu（画面右下付近の Flame メニュー）に **Embr → Smoke Test** があるか確認
4. 実行すると Flame のメッセージ欄 / ターミナルに `Embr smoke test OK` が出る
5. スクリプトを編集したら **Main Menu → Python → Rescan Python Hooks**

### うまく出ないとき

- アイコン起動していないか（`DL_PYTHON_HOOK_PATH` 未設定）
- パスが `scripts` ディレクトリを指しているか（リポジトリルートではない）
- ターミナルに `[PYTHON HOOK]` エラーが出ていないか
- 既存の共有スクリプトとメニュー名が衝突していないか

---

## 開発時の推奨

| 方法 | 用途 |
|------|------|
| **`DL_PYTHON_HOOK_PATH`（推奨・まずこれ）** | 公式・一時的・マシンを汚さない |
| symlink | 常時ロードしたいとき（任意） |
| `/opt/Autodesk/shared/python` | 配布・スタジオ共有の本番置き場 |

本リポジトリの当面の開発フローは **`DL_PYTHON_HOOK_PATH` → `scripts/`**。
