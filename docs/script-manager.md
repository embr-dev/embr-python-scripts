# Script Manager

GitHub 上のカタログを正とし、ローカルの Embr インストールと照合して **Install / Update / Uninstall / Repair** するツール。

| 項目 | 内容 |
|------|------|
| メニュー | Main Menu → **Embr → Script Manager** |
| パッケージ | `scripts/embr_manager/` |
| カタログ | [`catalog/catalog.json`](../catalog/catalog.json) |
| 生成 | `python3 tools/gen_catalog.py`（`ref` は現在の git branch） |

---

## インストールルート

**すべてのパッケージは `…/python/Embr/` 配下に入る**（hooks 直下を `embr_*` で埋めない）。

| 例 | パス |
|----|------|
| User (macOS) | `~/Library/Preferences/Autodesk/flame/python/Embr/` |
| User (Linux) | `~/flame/python/Embr/` |
| Shared | `/opt/Autodesk/shared/python/Embr/` |

```text
…/python/Embr/
  .embr/state.json      # channel + installed digests
  embr/                 # Core
  embr_manager/
  embr_<tool>/
```

リポジトリ側は従来どおり `scripts/embr`, `scripts/embr_*`（配布時だけ `Embr/` にネスト）。

ブートストラップ時に **User** か **Shared** を選ぶ。以降のルート変更はサポートしない。

Shared に書けない場合は権限昇格せず、英語で理由と対処（User へ切替 or 管理者）を出す。

---

## チャンネル（stable / latest / dev）

| チャンネル | git ref | 用途 |
|------------|---------|------|
| `stable` | `stable` | 配布・一般利用 |
| `latest` | `main` | main 先端 |
| `dev` | `dev` | 検証・プレリリース（既定） |

選択は `…/Embr/.embr/state.json` の `channel` に保存。UI の Channel で切替 → Refresh。

初回シード（マシンに Embr が無いとき）:

```bash
git clone -b dev https://github.com/embr-dev/embr-python-scripts.git
cd embr-python-scripts
"$(./tools/find_flame_python.sh)" tools/bootstrap_from_channel.py --channel dev
# Shared:  … --channel dev --shared
```

`find_flame_python.sh` は `/opt/Autodesk/python/2025.2.7` のような **マイナー付き** パスから最新の `bin/python3` を選ぶ（`…/python/2025` は無いことが多い）。

その後は **通常起動**（`DL_PYTHON_HOOK_PATH` なし）→ Rescan → Embr → Script Manager。

---

## ブートストラップ

1. `bootstrap_from_channel.py`、または初回ダイアログで User / Shared  
2. カタログから `embr` + `embr_manager` を `…/python/Embr/` へ配置  
3. **Rescan Python Hooks**  
4. Main Menu → Embr → Script Manager  

## 開発時（DL_PYTHON_HOOK_PATH）

`./tools/run_flame_dev.sh` で問題ない。ただし Flame は hooks 配下の `.py` を **basename で** ロードする。

そのため:

- ヘルパーは一意名（`embr_paths.py` / `embr_sm_window.py`）
- パッケージ相対 import（`from . import …`）は使わない
- Script Manager は起動時に `scripts/embr` と `scripts/embr_manager` を `sys.path` へ載せる

これは DL_PYTHON_HOOK_PATH 自体の不具合ではなく、Flame の hooks ローダ仕様に合わせた書き方。

---

## カタログ運用

公開するパッケージは `scripts/embr` または `scripts/embr_<tool>/` に置き、リリース前に:

```bash
python3 tools/gen_catalog.py
# 明示: EMBR_CATALOG_REF=dev python3 tools/gen_catalog.py
```

`catalog/catalog.json` をコミットする。チャンネルごとの URL 例:

- dev: `https://raw.githubusercontent.com/embr-dev/embr-python-scripts/dev/catalog/catalog.json`
- latest (`main`): `https://raw.githubusercontent.com/embr-dev/embr-python-scripts/main/catalog/catalog.json`
- stable: `https://raw.githubusercontent.com/embr-dev/embr-python-scripts/stable/catalog/catalog.json`

---

## ブランド資産（Embr 全体）

| 資産 | 扱い |
|------|------|
| アクセント | Ember（`BRAND.md`） |
| 背景 | 無彩色ダーク（Flame 標準 UI 寄り）。茶色の Ash 塗りはツールウィンドウでは使わない |
| タイトルバー | `embr.ui.prepare_embr_window`（左: icon+Embr / 中央: ウィンドウ名 / 右: min·max·close） |
| ロゴ | `scripts/embr/assets/logo/`（正本は Embr リポ `brand/`） |
| フォント | **Figtree**（SIL OFL）を `scripts/embr/assets/fonts/Figtree/` に同梱。Satoshi は使わない |

Flame ツールの UI は **`embr.ui` 経由のみ**。

---

## 動作確認チェックリスト

### Flame 外（自動）

```bash
PYTHONPATH=scripts "$(./tools/find_flame_python.sh)" tools/test_script_manager.py
```

### Flame 内（手動・配布相当）

- [ ] `bootstrap_from_channel.py --channel dev` → `…/python/Embr/`
- [ ] `DL_PYTHON_HOOK_PATH` **なし**で起動 → Script Manager
- [ ] Channel 切替（dev / latest / stable）
- [ ] Install / Update / Repair / Uninstall
- [ ] Shared python（書ける場合 / 書けない場合のエラー文）
- [ ] macOS と Rocky Linux

---

## モジュール

| ファイル | 役割 |
|----------|------|
| `embr_manager.py` | フック入口のみ |
| `embr_sm_catalog.py` | 取得・検証・チャンネル |
| `embr_sm_local.py` | digest / state（channel） |
| `embr_sm_actions.py` | 4 操作 |
| `embr_sm_bootstrap.py` | User / Shared → `Embr/` 初回配置 |
| `embr_sm_window.py` | PySide6 ウィンドウ |

Flame は `.py` を **ファイル名（basename）** でモジュール化するため、ヘルパーは `embr_sm_*.py` の一意名にする（`ui.py` や `__init__.py` は使わない）。
