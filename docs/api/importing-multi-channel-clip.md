# Importing Multi-Channel Clip

公式 Help「Importing Multi-Channel Clip」の整理。Flame Learning Channel の Python 動画でも紹介されている例。

| 項目 | 内容 |
|------|------|
| 一次情報 | `docs/API Documentation/Importing Multi-Channel Clip/` |
| 親 | Python API Examples |
| 関連 | [recipes.md](./recipes.md) · [getting-started.md](./getting-started.md) |

---

## 概要

Batch で **マルチチャンネル clip** を扱うときのクイックスタート例。

使う前に必ず変えるもの:

1. **import するメディアのパス**（例の `/var/tmp/flc_python/...` は学習用）
2. **チャンネル接続時のソケット名**（clip 側チャンネル名はメディア依存）

---

## 流れ

1. `create_batch_group` で Batch グループ作成  
2. `go_to()` で Batch タブへ  
3. `import_clip` でマルチチャンネル媒体を Schematic Reel へ  
4. Action を作り `add_media()` でメディア層を追加  
5. clip の各チャンネル出力 → Action Media の Front へ接続  
6. Action の Comp 出力 → Write File  
7. `organize()` で配置整理  

---

## 公式サンプル（整形）

```python
import flame

schematicReels = ["Multi-Channel_Clip"]
shelfReels = ["Extra_Data"]

flame.batch.create_batch_group(
    "Learning_Multi-Channel",
    start_frame=1001,
    duration=5,
    reels=schematicReels,
    shelf_reels=shelfReels,
)

flame.batch.go_to()

clip1 = flame.batch.import_clip(
    "/var/tmp/flc_python/robot/robot_CGI.clip",
    "Multi-Channel_Clip",
)
clip1.name = "CGI_Render"

action1 = flame.batch.create_node("Action")
action1.name = "Comping_CGI"

direct_diffuse = action1.add_media()
direct_diffuse.name = "Direct_Diffuse"
indirect_diffuse = action1.add_media()
indirect_diffuse.name = "Indirect_Diffuse"
direct_specular = action1.add_media()
direct_specular.name = "Direct_Specular"
indirect_specular = action1.add_media()
indirect_specular.name = "Indirect_Specular"
reflection = action1.add_media()
reflection.name = "Reflection"

writeFile = flame.batch.create_node("Write File")
writeFile.name = "MyComp"

flame.batch.connect_nodes(clip1, "robot_direct_diffuse", direct_diffuse, "Front")
flame.batch.connect_nodes(clip1, "robot_indirect_diffuse", indirect_diffuse, "Front")
flame.batch.connect_nodes(clip1, "robot_direct_specular", direct_specular, "Front")
flame.batch.connect_nodes(clip1, "robot_indirect_specular", indirect_specular, "Front")
flame.batch.connect_nodes(clip1, "robot_reflection", reflection, "Front")
flame.batch.connect_nodes(action1, "output1 [ Comp ]", writeFile, "Front")

flame.batch.organize()
```

### Embr 向けメモ

- ソケット名は **Flame UI に表示される文字列と完全一致**（大小区別）。不一致は `Invalid socket name`。
- MediaHub の multi-channel モード設定は `flame.mediahub.files.options.multi_channel_mode`（[whats-new.md](./whats-new.md) / Attributes 参照）。
- 新規ノードはデフォルトで重なるため、最後に `organize()` が定石。
