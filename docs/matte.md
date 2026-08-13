# Embr Matte

Main Menu → **Embr → Matte**。Media Panel のクリップをジョブ化し、エクスポート／インポートするツール（Phase 0）。

| 項目 | 内容 |
|------|------|
| パッケージ | `scripts/embr_matte/`（カタログ id `embr_matte`） |
| ジョブ格納 | `$EMBR_ML_ROOT/jobs/<job_id>/`（既定は `~/Embr/ml/jobs/`） |
| プリセット | [`presets/Embr.xml`](../scripts/embr_matte/presets/Embr.xml) |

## Phase 0 操作

1. ウィンドウを開く（空リスト + **Add**）
2. Media Panel でクリップを選び **Add** → `export/` に PNG 書き出し → `input/` に正規化
3. 一覧: サムネ・クリップ名・**Import**
4. **Import** → Add 時点で記録した親リールへ `import_clips` → `cache_media("current")`

ジョブはウィンドウを閉じても `status.json` で残る。親オブジェクト参照はセッション内のみ；再起動後は親名で解決し、見つからなければ失敗する（別リールへ流さない）。

## Export プリセット（StartFrame）

`Embr.xml` は **`startFrame=1`**・`framePadding=6`・8-bit RGB PNG。`000001` 始まりを Flame / MatAnyone 系と揃えるため、0 始まりにはしない。

現行プリセットは `ResScalingValue=50`（50%）。Phase 0 の往復確認用；本番解像度は後続フェーズで見直す。

## 後続（未実装）

ランタイム導入 UI、SAM2 ガイド、MatAnyone2 実行キューなど。AI ランタイム全体は [ai-runtime.md](./ai-runtime.md)。
