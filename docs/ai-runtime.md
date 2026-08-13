# Embr AI / PyBox ランタイム（`~/Embr`）

Flame hooks（`…/python/Embr/`）とは別に、**AI / PyBox 用ランタイム**を `$EMBR_HOME`（既定 `~/Embr`）に閉じる。

| 項目 | 内容 |
|------|------|
| UI | Embr Manager → **PyBox** タブ |
| CLI | `python3 tools/install_embr_runtime.py` |
| 実装 | `scripts/embr/embr_runtime.py` |
| handlers | [embr-pybox-handlers](https://github.com/embr-dev/embr-pybox-handlers)（`dev`） |

詳細な契約・レイアウトは handlers 側の `docs/handoff-embr-runtime-install.md` / `docs/embr-home.md` を正とする。

---

## 何が別物か

| | Scripts（既存） | PyBox ランタイム |
|--|-----------------|------------------|
| 場所 | `…/python/Embr/` | `$EMBR_HOME`（`~/Embr`） |
| 中身 | hooks / Embr パッケージ | `bin/uv`, handlers clone, venv, weights |
| 管理 | Manager → Scripts | Manager → PyBox / CLI |
| 削除 | Scripts の Uninstall | `rm -rf ~/Embr`（＋任意で `~/embr-ml`） |

---

## レイアウト（要約）

```text
~/Embr/                          # $EMBR_HOME
  bin/uv
  ml/                            # $EMBR_ML_ROOT
  repos/embr-pybox-handlers/
  tools/
  venvs/
```

環境変数: `EMBR_HOME` / `EMBR_ML_ROOT` / `EMBR_UV`。**グローバル PATH には足さない**（子プロセスだけ `PATH` 先頭に `bin` を付ける）。

---

## Install が行うこと

1. `$EMBR_HOME` の `bin/ ml/ tools/ repos/ venvs/` を作成  
2. Astral uv を **`$EMBR_HOME/bin`** に配置（`UV_INSTALL_DIR`）  
3. `embr-pybox-handlers` を `repos/` に clone（または update）  
4. `worker/embr_ml/bootstrap.py` を実行（venv・モデル確保）

bootstrap の起動は **Python 3.10+ 必須**。Linux では Flame 起動でも `sys.executable` が古い `/usr/bin/python3`（3.6）になることがあるため、Install は次の順で選ぶ:

1. `$EMBR_HOME/bin/uv run --python 3.10`（推奨）
2. `/opt/Autodesk/python/*/bin/python3`
3. `sys.executable`（3.10+ のときだけ）

Repair は uv / repo を確保し、壊れた `worker/.venv` があれば消してから bootstrap。  
Uninstall は `$EMBR_HOME` 全体と任意で `~/embr-ml` シンボリックリンク。**hooks は触らない**。

---

## CLI

```bash
# 状態
python3 tools/install_embr_runtime.py --status

# Install / Update（ネット・時間がかかります）
python3 tools/install_embr_runtime.py

# Repair
python3 tools/install_embr_runtime.py --repair

# Uninstall
python3 tools/install_embr_runtime.py --uninstall --yes
```

`--home /path` で `EMBR_HOME` を上書き可能。

---

## Flame での使い方（Install 後）

1. Embr → **Manager** → **PyBox** で状態を確認  
2. PyBox で Handler に `…/repos/embr-pybox-handlers/handlers/embr_matte.py` などを指定  
3. Repo Root は handlers clone の絶対パス  

MatAnyone2 は S-Lab **non-commercial** 系。Install UI にも注記あり。社内ポリシーを確認すること。

---

## 既知のフォロー（handlers 側）

現行 bootstrap は `~/.local/bin/uv` を好みやすい。scripts 側 Install は先に `$EMBR_HOME/bin/uv` を置き、bootstrap 起動時に `EMBR_HOME` / `EMBR_UV` / `PATH` / `UV_INSTALL_DIR` を渡す。handlers 側の `find_uv` / `install_uv` 改修後はさらに安全になる。
