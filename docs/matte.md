# Embr Matte

Main Menu → **Embr → Matte**。Media Panel のクリップをジョブ化し、エクスポート／インポートするツール。

| 項目 | 内容 |
|------|------|
| パッケージ | `scripts/embr_matte/`（カタログ id `embr_matte`） |
| ジョブ格納 | `$EMBR_ML_ROOT/jobs/<job_id>/`（既定は `~/Embr/ml/jobs/`） |
| ジョブ ID | 12 桁 hex（`uuid4`）。**フォルダ名＝ID** |
| プリセット | [`presets/Embr.xml`](../scripts/embr_matte/presets/Embr.xml)（`Embr_custom` 由来） |
| ランタイム | `$EMBR_HOME`（Manager PyBox と同じ `embr_runtime`） |

## Phase 0 — クリップ往復

1. ウィンドウを開く（空リスト + **Add**）
2. Media Panel でクリップを選び **Add** → `jobs/<id>/export/` に PNG 書き出し（この連番をそのまま RGB input として使う）
3. 一覧: サムネ・クリップ名・job id・**Import (download)**・**Delete**
4. **Import** → Add 時点の親リールへ `import_clips` → 名前を `<clip>-ML-Matte` に変更 → 記録したソース解像度 / FPS / ビット深度へ `reformat(Fill)` → `cache_media("current")`
5. **Delete** → 確認後に `$EMBR_ML_ROOT/jobs/<id>/` を削除

ジョブはウィンドウを閉じても `status.json` で残る。親オブジェクト参照はセッション内のみ；再起動後は親名で解決し、見つからなければ失敗する（別リールへ流さない）。

## Phase 1 — Runtime gate

窓上部は **1行**（`Ready · mps · dev` + Check / Install）。パスはツールチップ。Install ログは実行中のみ表示し、成功後は閉じる。Install のオレンジ強調は未準備時のみ（通常の accent は Add）。

## Export プリセット

- `startFrame=1` / `framePadding=6` / 8-bit RGB PNG
- `namePattern` 空（フラット連番。コピー正規化なし）
- 現行 `Embr_custom`: height 1080 系のスケール設定を含む（プロジェクト検証用）

## インポート API メモ

- `flame.import_clips(path, destination)` 自体に名前／解像度引数は無い
- 名前: 戻り値の `PyClip.name = "…-ML-Matte"`
- フォーマット: Add 時に `width` / `height` / `ratio` / `bit_depth` / `scan_mode` / `frame_rate` を `status.json` へ保存し、Import 後に `reformat`（`resize_mode=Fill`）。旧ジョブで解像度が 0 の場合は再 Add が必要

## 後続（未実装）

MatAnyone2 実行キュー、SAM2 ガイド UI。AI ランタイム全体は [ai-runtime.md](./ai-runtime.md)。
