# Looping by Node Type

公式 Help「Looping by Node Type」の整理。

| 項目 | 内容 |
|------|------|
| 一次情報 | `docs/API Documentation/Looping by Node Type/` |
| 親 | Python API Examples |
| 関連 | [recipes.md](./recipes.md) · [flame-module.md](./flame-module.md)（`PyBatch`） |

---

## 概要

`flame.batch.nodes` で Batch schematic 内の全ノードを取得し、`for` で回して条件に合うノードだけ変更する定石。

---

## 例 1 — Action Media の位置を動かす

`type == "Action Media"` かつ `pos_y < 99` のノードを上方向へずらす。

```python
import flame

for i in flame.batch.nodes:
    if i.type == "Action Media" and i.pos_y < 99:
        i.pos_y -= 100
```

---

## 例 2 — 全 Comp の blend mode を Add に

Flame Learning Channel の Python 動画でも紹介。

```python
import flame

for n in flame.batch.nodes:
    if n.type == "Comp":
        n.flame_blend_mode = "Add"
```

---

## Embr 向けメモ

- `flame.batch` は **現在の** Batch グループ。対象グループを開いた状態で実行する。
- `n.type` の文字列は UI / API のノード種別表記と一致させる（例: `"Comp"`, `"Action Media"`, `"Write File"`）。
- hooks の `selection` と組み合わせる場合は、選択オブジェクトの型チェック（`isinstance`）も併用すると安全。
- 例外を握りつぶしたい場合の最小形は [recipes.md](./recipes.md) の Catching Exceptions を参照。
