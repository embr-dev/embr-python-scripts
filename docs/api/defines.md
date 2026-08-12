# Defines for the flame Module（オブジェクトへの到達）

公式 Help「Defines for the flame Module」の内容を、Embr 用に表形式で整理したもの。  
`<PyClip>` のような表記は「その型のオブジェクト」を指すショートハンド（Code Samples でも同じ）。

| 一次情報 |
|----------|
| `docs/API Documentation/Defines for the flame Module/` |

**注:** Help の例は `flame.project.current_project` 表記。2020.1 以降は `flame.projects` 推奨（`flame.project` も互換のため残る）。Embr では **`flame.projects`** を使う。

---

## 到達パス一覧

| 型 | 到達例 |
|----|--------|
| **PyProject** | `flame.projects.current_project` |
| **PyWorkspace** | `flame.projects.current_project.current_workspace` |
| | `PyProject.current_workspace` |
| **PyDesktop** | `...current_workspace.desktop` |
| | `PyWorkspace.desktop` |
| **PyBatch** | `...desktop.batch_groups[#]` |
| | `flame.batch`（**現在の** Batch） |
| **PyNode** | `...batch_groups[#].nodes[#]` |
| | `...batch_groups[#].current_node` |
| | `...batch_groups[#].get_node("name")` |
| | `...batch_groups[#].create_node("type")` |
| **PyReelGroup** | `...libraries[#].reel_groups[#]` |
| | `...desktop.reel_groups[#]` |
| **PyReel** | `...libraries[#].reel_groups[#].reels[#]` |
| | `...desktop.reel_groups[#].reels[#]` |
| **PyLibrary** | `...current_workspace.libraries[#]` |
| **PyFolder** | `...libraries[#].folders[#]`（ネスト可） |
| **PyBatchIteration** | `...batch_groups[#].batch_iterations[#]` |
| **PyClip** | `...libraries[#].clips[#]` |
| | `...desktop.reel_groups[#].reels[#].clips[#]` |
| **PySequence** | `...libraries[#].sequences[#]` |
| | `...reels[#].sequences[#]` |
| **PyVersion** | `PySequence.versions[#]` |
| **PyTimelineFX** | `...tracks[#].segments[#].effects[#]` |
| **PyTrack** | `PySequence.versions[#].tracks[#]` |
| **PyMarker** | `...segments[#].markers[#]` または `...sequences[#].markers[#]` |
| **PyAudioTrack** | `PySequence.audio_tracks[#]` |
| **PySegment** | `...tracks[#].segments[#]` |

`[#]` はリスト添字。

---

## Embr でのよく使う入口

```python
import flame

project = flame.projects.current_project
workspace = project.current_workspace
desktop = workspace.desktop
batch = flame.batch  # current batch group
```

詳細メンバは [flame-module.md](./flame-module.md)。Attributes ページ群は後続で原文寄りに整理する。
