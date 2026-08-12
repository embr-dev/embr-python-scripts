# Render Passes with the Python API

公式 Help「Render Passes with the Python API」の整理。Flame Learning Channel の Python 動画でも紹介されている例。

| 項目 | 内容 |
|------|------|
| 一次情報 | `docs/API Documentation/Render Passes with the Python API/` |
| 親 | Python API Examples |
| 関連 | [importing-multi-channel-clip.md](./importing-multi-channel-clip.md) · [looping-by-node-type.md](./looping-by-node-type.md) |

---

## 概要

Batch で **マルチパス render** を自動化する例。複数 clip を import し、Comp ノード列で合成して Write File へつなぐ。

使う前に必ず変えるもの:

1. 各パスの **ファイルパス**（例は `[025-029].exr` 連番）
2. パス構成・ブレンドモード（メディアに合わせて調整）

---

## 流れ

1. パス種別ごとの Schematic Reel を持つ Batch グループを作成  
2. 各 EXR シーケンスを `import_clip`  
3. Comp ノードを作成し `flame_blend_mode` を設定（Add / Screen 等）  
4. Front / Back / Result でチェーン接続  
5. `organize()`  

---

## 公式サンプル（整形）

```python
import flame

schematicReels = [
    "direct_passes",
    "indirect_passes",
    "reflection",
    "Utility_Passes",
]
shelfReels = ["Extra_Data"]

flame.batch.create_batch_group(
    "Learning_RenderPasses",
    start_frame=1001,
    duration=5,
    reels=schematicReels,
    shelf_reels=shelfReels,
)

flame.batch.go_to()

clip1 = flame.batch.import_clip(
    "/var/tmp/flc_python/robot/direct_diffuse/robot_direct_diffuse.[025-029].exr",
    "direct_passes",
)
clip1.name = "Direct_Diffuse"
clip2 = flame.batch.import_clip(
    "/var/tmp/flc_python/robot/indirect_diffuse/robot_indirect_diffuse.[025-029].exr",
    "indirect_passes",
)
clip2.name = "Indirect_Diffuse"
clip3 = flame.batch.import_clip(
    "/var/tmp/flc_python/robot/direct_specular/robot_direct_specular.[025-029].exr",
    "direct_passes",
)
clip3.name = "Direct_Specular"
clip4 = flame.batch.import_clip(
    "/var/tmp/flc_python/robot/indirect_specular/robot_indirect_specular.[025-029].exr",
    "indirect_passes",
)
clip4.name = "Indirect_Specular"
clip5 = flame.batch.import_clip(
    "/var/tmp/flc_python/robot/reflection/robot_reflection.[025-029].exr",
    "reflection",
)
clip5.name = "Reflection"
clip6 = flame.batch.import_clip(
    "/var/tmp/flc_python/robot/P/robot_P.[025-029].exr",
    "Utility_Passes",
)
clip6.name = "Position_Map"
clip7 = flame.batch.import_clip(
    "/var/tmp/flc_python/robot/N/robot_N.[025-029].exr",
    "Utility_Passes",
)
clip7.name = "Normals_Map"
clip8 = flame.batch.import_clip(
    "/var/tmp/flc_python/robot/Z/robot_Z.[025-029].exr",
    "Utility_Passes",
)
clip8.name = "Z-Depth_Map"

comp1 = flame.batch.create_node("Comp")
comp1.name = "Diffuse"
comp1.flame_blend_mode = "Add"

comp2 = flame.batch.create_node("Comp")
comp2.name = "Direct_Specular"
comp2.flame_blend_mode = "Add"

comp3 = flame.batch.create_node("Comp")
comp3.name = "Indirect_Specular"
comp3.flame_blend_mode = "Add"

comp4 = flame.batch.create_node("Comp")
comp4.name = "Reflection"
comp4.flame_blend_mode = "Screen"

writeFile = flame.batch.create_node("Write File")
writeFile.name = "MyComp"

flame.batch.connect_nodes(clip1, "BGR", comp1, "Front")
flame.batch.connect_nodes(clip2, "BGR", comp1, "Back")
flame.batch.connect_nodes(comp1, "Result", comp2, "Back")
flame.batch.connect_nodes(clip3, "BGR", comp2, "Front")
flame.batch.connect_nodes(comp2, "Result", comp3, "Back")
flame.batch.connect_nodes(clip4, "BGR", comp3, "Front")
flame.batch.connect_nodes(comp3, "Result", comp4, "Back")
flame.batch.connect_nodes(clip5, "BGR", comp4, "Front")
flame.batch.connect_nodes(comp4, "Result", writeFile, "Front")

flame.batch.organize()
```

### Embr 向けメモ

- Utility パス（P / N / Z）は import・命名まで行い、この例では Comp チェーンには未接続。
- 全 Comp の blend を一括変更するなら [looping-by-node-type.md](./looping-by-node-type.md) と組み合わせるとよい。
- `flame_blend_mode` の取り得る値は Comp ノード Attributes / UI 表記に合わせる。
