# Getting Started（Flame Python API）

公式 Help の次を基に、Embr 開発の実行まわりをまとめたもの。

| 一次情報 |
|----------|
| `docs/API Documentation/Python Console and How to Execute Scripts/` |
| `docs/API Documentation/Write Your First Python API Script/` |

前提: [hooks.md](./hooks.md)（メニュー配布）／ [embr-util.md](../embr-util.md)

---

## 1. スクリプトの必須条件

どの実行経路でも、API を使うスクリプトは先頭で:

```python
import flame
```

Help 明記: **`import flame` がないと動かない**（特に `-s` 起動時スクリプト）。

Embr hooks でも同様。Console では **タブごとに一度** `import flame` すればよい（再宣言不要）。

---

## 2. Python Console

Flame メニューから開く。API を試す主ツール。

### ウィンドウ

| 部分 | 役割 |
|------|------|
| Terminal | `print` / `help()` / エラー（赤）の出力 |
| Editor | スクリプト編集。下部タブで複数ファイル。`+` で新規タブ |

### 主なボタン（Help 記載）

| 操作 | 内容 |
|------|------|
| Play | 現在タブ全体、または **選択範囲のみ** を実行 |
| Save / Load | スクリプトの保存・読込（新タブ） |
| Eraser（Terminal） | 出力クリア |
| Eraser（Editor） | 現在タブのコードクリア |
| Sound Wave | 実行したコードを Terminal に出すか（青で ON） |
| Line numbers | 行番号表示トグル |

### Console からの実行

1. **By Script** — Play でタブ全体を実行  
2. **By Selection** — 選択行だけ Play  

デバッグは Terminal のトレースバックを見る。

---

## 3. 起動時にスクリプトを実行（`-s`）

コマンドラインから Flame を起動し、プロジェクト読込後にスクリプトを走らせる。

```bash
/opt/Autodesk/<version>/bin/startApplication -s /path/to/onStart.py
```

このマシン例:

```bash
/opt/Autodesk/.flamefamily_2025/bin/startApplication -s /path/to/onStart.py
```

Embr 開発で hooks も使う場合は、これまでどおり `DL_PYTHON_HOOK_PATH` を付けたうえで `-s` も併用可能:

```bash
export DL_PYTHON_HOOK_PATH="/Users/oue.isamu/Projects/embr-python-scripts/scripts"
/opt/Autodesk/.flamefamily_2025/bin/startApplication -s /path/to/onStart.py
```

**Embr の通常ツール配布は hooks（メニュー）が主。** `-s` は起動時ワンショットや検証用。

---

## 4. 最初の Batch スクリプト（公式チュートリアル要約）

流れ:

1. `import flame`
2. `flame.batch.create_batch_group(...)` で Batch グループ作成  
3. `flame.batch.go_to()` で Batch タブへ  
4. `flame.batch.create_node("...")` でノード作成（戻り値を変数に保持）  
5. `flame.batch.connect_nodes(src, "Socket", dst, "Socket")` で接続  
6. `flame.batch.organize()` で配置整理（新規ノードはデフォルトで重なる）

完成形（公式の完成スクリプト）:

```python
import flame

schematicReels = [
    "SchematicReel1",
    " SchematicReel2",
    "SchematicReel3",
    "SchematicReel4",
]
shelfReels = ["ShelfReel1", "ShelfReel2", "ShelfReel3"]

flame.batch.create_batch_group(
    "TheName",
    start_frame=1,
    duration=99,
    reels=schematicReels,
    shelf_reels=shelfReels,
)

flame.batch.go_to()

comp = flame.batch.create_node("Comp")
writeFile = flame.batch.create_node("Write File")

flame.batch.connect_nodes(comp, "Result", writeFile, "Front")
# Invalid socket name はソケット名の綴り／大小不一致で出る（Flame 上の表示と完全一致）

flame.batch.organize()
```

手動配置する場合はノードの `pos_x` / `pos_y` を設定する。

実行: Console の Play、または保存して `-s` で起動時実行。

---

## 5. Embr での実行パターン整理

| 方法 | 用途 |
|------|------|
| **Custom UI hooks**（Main Menu / Batch 等） | 本番ツールの主経路 |
| **Python Console** | 試行・デバッグ・短文実行 |
| **`startApplication -s`** | 起動時自動実行 |
| **`embr.hooks.refresh()`** | hooks／util 変更の再読込 |

オブジェクトへの到達パスは [defines.md](./defines.md)。短いレシピは [recipes.md](./recipes.md)。クラス一覧は [flame-module.md](./flame-module.md)。
