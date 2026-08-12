# Flame Python API ドキュメント（Embr）

公式 Help（保存済み HTML）とローカル同梱ソースを基にした Embr 向けまとめ。

## 構成

| 文書 | 役割 |
|------|------|
| [hooks.md](./hooks.md) | Python Hooks（配置・Custom UI・同梱 hook 一覧） |
| [getting-started.md](./getting-started.md) | Console / `-s` 起動 / 最初の Batch スクリプト |
| [defines.md](./defines.md) | オブジェクトへの到達パス |
| [recipes.md](./recipes.md) | 短いレシピ集 |
| [importing-multi-channel-clip.md](./importing-multi-channel-clip.md) | マルチチャンネル clip の Batch 例 |
| [render-passes.md](./render-passes.md) | マルチパス render の Batch 例 |
| [looping-by-node-type.md](./looping-by-node-type.md) | `batch.nodes` で種別ループ |
| [pybox.md](./pybox.md) | Pybox handler（外部アプリ連携） |
| [whats-new.md](./whats-new.md) | 過去リリースの Python API 変更年表 |
| [flame-module.md](./flame-module.md) | **メソッド／モジュール関数・Data の索引**（整形済み） |
| [attributes/](./attributes/) | **属性（Attributes）原文寄り集約** |

## 読み分け

- **何ができる？（メソッド）** → [flame-module.md](./flame-module.md)
- **プロパティの型・意味・値域** → [attributes/](./attributes/)
- **hooks でメニューに出す** → [hooks.md](./hooks.md)
- **Batch 自動化の定石例** → recipes / multi-channel / render-passes / looping
- **外部レンダラ連携** → [pybox.md](./pybox.md)
- **いつ API が増えたか** → [whats-new.md](./whats-new.md)（2025 は [prerequisites](../prerequisites.md)）

## 公式トピック ↔ このディレクトリ

| 公式 Help | Embr doc |
|-----------|----------|
| Python Hooks Reference / Tips | [hooks.md](./hooks.md) |
| Console / Write Your First Script | [getting-started.md](./getting-started.md) |
| Defines for the flame Module | [defines.md](./defines.md) |
| Flame API Code Samples | [recipes.md](./recipes.md) |
| Importing Multi-Channel Clip | [importing-multi-channel-clip.md](./importing-multi-channel-clip.md) |
| Render Passes with the Python API | [render-passes.md](./render-passes.md) |
| Looping by Node Type | [looping-by-node-type.md](./looping-by-node-type.md) |
| Pybox | [pybox.md](./pybox.md) |
| What's New in Previous Releases | [whats-new.md](./whats-new.md) |
| Autodesk Flame Family Python Module | [flame-module.md](./flame-module.md) |
| Attributes | [attributes/](./attributes/) |

## 一次情報

- 保存 HTML: [`../API Documentation/`](../API%20Documentation/)
- ローカル hooks: `/opt/Autodesk/.flamefamily_2025/python/`
- 再生成スクリプト（参考）: `tools/gen_api_docs.py`

## ライセンス注記

Autodesk Help は CC BY-NC-SA 3.0 等の表記あり。Embr ドキュメントは学習・開発用の要約／突合であり、公式の代替ではない。
