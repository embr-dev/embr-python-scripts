# Embr Matte

Main Menu → **Embr → Matte**。Media Panel のクリップをジョブ化し、エクスポート／インポートするツール（Phase 0）。

| 項目 | 内容 |
|------|------|
| パッケージ | `scripts/embr_matte/`（カタログ id `embr_matte`） |
| ジョブ格納 | `$EMBR_ML_ROOT/jobs/<job_id>/`（既定は `~/Embr/ml/jobs/`） |
| ジョブ ID | 12 桁 hex（`uuid4`）。**フォルダ名＝ID** |
| プリセット | [`presets/Embr.xml`](../scripts/embr_matte/presets/Embr.xml)（`Embr_custom` 由来） |

## Phase 0 操作

1. ウィンドウを開く（空リスト + **Add**）
2. Media Panel でクリップを選び **Add** → `jobs/<id>/export/` に PNG 書き出し（この連番をそのまま RGB input として使う）
3. 一覧: サムネ・クリップ名・job id・**Import**
4. **Import** → Add 時点の親リールへ `import_clips` → 名前を `<clip>-ML-Matte` に変更 → 記録したソース解像度へ `reformat(Fit)`（取得できた場合）→ `cache_media("current")`

ジョブはウィンドウを閉じても `status.json` で残る。親オブジェクト参照はセッション内のみ；再起動後は親名で解決し、見つからなければ失敗する（別リールへ流さない）。

## Export プリセット

- `startFrame=1` / `framePadding=6` / 8-bit RGB PNG
- `namePattern` 空（フラット連番。コピー正規化なし）
- 現行 `Embr_custom`: height 1080 系のスケール設定を含む（プロジェクト検証用）

## インポート API メモ

- `flame.import_clips(path, destination)` 自体に名前／解像度引数は無い
- 名前: 戻り値の `PyClip.name = "…-ML-Matte"`
- 解像度: Add 時に保存した `source_width` / `source_height` で `reformat`（MediaHub options でも指定可能だが、本ツールは import 後 reformat を採用）

## 後続（未実装）

ランタイム導入 UI、SAM2 ガイド、MatAnyone2 実行キューなど。AI ランタイム全体は [ai-runtime.md](./ai-runtime.md)。
