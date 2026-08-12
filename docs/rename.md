# Embr Rename

Timeline / Media Panel / Batch のコンテキストメニュー → **Embr → Rename**。

トークン付きパターンと複数 Find/Replace で、選択オブジェクトの `.name` を変更する。プレビューは先頭の rename 対象のみ。

## selection

**常に `isVisible` 時の selection を使う。** `execute` の引数は無視する（フォーカス移動で空／別選択になることがあるため）。詳細は [api/hooks.md](./api/hooks.md)。

## トークン（v1）

| トークン | 意味 |
|----------|------|
| `<name>` | 元の名前 |
| `<date@YYMMDD>` | 今日の日付（`@` 以降は `YY`/`YYYY`/`MM`/`DD` 等） |

## パッケージ

`scripts/embr_rename/` — カタログ id `embr_rename`。
