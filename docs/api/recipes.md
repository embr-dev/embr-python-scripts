# Flame API Recipes（短いレシピ集）

公式「Flame API Code Samples」＋「Python API Examples」を基にしたレシピ。  
`<PyClip>` 等は [defines.md](./defines.md) のショートハンド。

| 一次情報 |
|----------|
| `docs/API Documentation/Flame API Code Samples/` |
| `docs/API Documentation/Python API Examples/` |

例外の捕り方（Examples）:

```python
from flame import batch

try:
    batch.import_clip("bad_path", "bad_reel_name")
except Exception as e:
    print(str(e))
```

---

## Clip

```python
# Import into a library
flame.import_clips("/usr/tmp/clip.mov", py_library)

# Reformat
py_clip.reformat(width=1920, height=1080, ratio=1.778)

# Render Timeline FX via Burn (proxy)
py_clip.render(
    render_mode="All",
    render_option="Burn",
    render_quality="Proxy Resolution",
)

# Render Batch FX on clip
py_clip.render(effect_type="Batch FX")

print(py_clip.is_rendered())
```

## Views / Desktop

```python
py_desktop.set_desktop_reels()
py_desktop.set_desktop_reels(py_batch)

py_workspace.set_freeform()
py_workspace.set_freeform(py_library)
```

## Timeline selection / markers

```python
# Select all segments on bottom video track
for seg in py_version.tracks[0].segments:
    seg.selected = True

# Unrendered segments
for seg in py_version.tracks[0].segments:
    if seg.is_rendered() is False:
        seg.selected = True

# Markers on clip
for marker in py_clip.markers:
    print(marker.name)

py_clip.create_marker(10)

marker = py_clip.markers[0]
marker.location = 20
marker.comment = "<user>_<date>"
```

## PyTime

```python
tc = flame.PyTime("10:00:01:05", "23.976 fps")
frm = flame.PyTime(10)  # relative frame
frm_abs = flame.PyTime(864000, "23.976 fps")

print(py_clip.current_time.frame)
print(py_clip.current_time.relative_frame)
print(py_clip.current_time.timecode)
```

## Marks / duration

```python
py_clip.in_mark = 20
tc = flame.PyTime("10:00:00:20", "23.976 fps")
py_clip.in_mark = tc
print(py_clip.in_mark.get_value().frame)

py_clip.out_mark = 30
print(py_clip.duration.frame)

py_clip.current_time = "10:00:00:20"
```

## Segment / Timeline FX

```python
py_segment.shot_name = "sh010"
py_segment.comment = "sh010"
print(py_segment.file_path)

py_segment.create_effect("Blur")
py_segment.create_effect("Blur", "Image")  # after existing Image TL FX
print(py_segment.effect_types)
print(py_segment.effects)

for effect in py_segment.effects:
    if effect.type == "Image":
        effect.bypass = True

py_timeline_fx.bypass = True
py_segment.effects[0].save_setup("/usr/tmp/my_timelinefx_setup")
```

## Tracks

```python
seq = py_sequence
track = seq.versions[0].tracks[0]
seq.primary_track = track
print(seq.primary_track.get_value().name)

seq.secondary_track = track
version = seq.versions[0]
version.expanded = False
version.locked = True
version.hidden = True

track.stereo_linked = False
```

## Media Panel / Batch on Desktop

```python
batch = py_desktop.batch_groups[0]
batch.create_reel("MyReel")
batch.create_shelf_reel("MyShelfReel")
batch.iterate()
batch.iterate(5)

py_desktop.destination = py_library
batch.save()
batch.save_current_iteration()

py_folder.batch_groups[0].open_as_batch_group()
py_library.batch_iterations[0].open_as_batch_group()

flame.execute_shortcut("Overwrite Edit")

flame.media_panel.move(clips, reel)
flame.media_panel.copy(clips, reel)
flame.media_panel.selected_entries = py_reel.clips
print(flame.media_panel.selected_entries)

flame.media_panel.visible = False
flame.media_panel.full_width = True
flame.media_panel.dual = True
```

## parent（hooks の selection から）

```python
def action_1(selection):
    import flame
    for marker in selection:
        print(marker.parent.name)
        parent = marker.parent
        marker.location = parent.record_in + (parent.record_duration.frame / 2)
```

## Action Compass

```python
compass = action.create_node("Compass")
compass.colour = (50, 50, 50)
compass.name = "MyCompass"
compass.width = 250
compass.height = 250

action.encompass_nodes(["NodeName1", node3, "NodeName2"])
```

## Batch nodes

```python
flame.batch.create_node("Matchbox", "Blur.mx")
flame.batch.create_node("Pybox", "sendmail.py")

mx = flame.batch.get_node("Matchbox100")
print(mx.shader_name)

ofx = flame.batch.create_node("OpenFX")
ofx.change_plugin("S_Distort")

mux = flame.batch.current_node.get_value()
mux.bypass = True
mux.before_range = "Repeat First"
mux.after_range = "Repeat Last"

frame = flame.batch.current_frame
mux.range_active = True
mux.range_start = frame
mux.range_end = frame
```

## Users / Tabs

```python
user = flame.users.current_user.name
print(flame.users.current_user.nickname)

print(flame.get_current_tab())
flame.set_current_tab("Timeline")
```

---

関連トピック（保存済み・未整理の個別ページ）:

- Importing Multi-Channel Clip
- Render Passes with the Python API
- Looping by Node Type

クラス詳細索引: [flame-module.md](./flame-module.md)
