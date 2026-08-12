# What's New in Previous Releases（Python API）

公式 Help「What's New in Previous Releases」の整理。**Python API のリリース別変更**が主題。

| 項目 | 内容 |
|------|------|
| 一次情報 | `docs/API Documentation/What's New in Previous Releases/` |
| 関連 | [prerequisites.md](../prerequisites.md) · [flame-module.md](./flame-module.md) · [attributes/](./attributes/) |

---

## Embr 向け読み方

- 本リポジトリは **Flame 2025.0+ / Python 3.11 / PySide6** 固定。
- **2025 の変更（PySide6 移行など）はこの Help ページに含まれない。** → [prerequisites.md](../prerequisites.md) と公式 [wn-2025-python-api](https://help.autodesk.com/cloudhelp/2026/ENU/Flame-WhatsNew/files/Previous-Releases/What-s-New-in-Flame-Family-2025/What-s-New-in-2025/wn-2025-python-api.html)。
- 属性の型・値域は [attributes/](./attributes/) を正とする。ここは「いつ何が増えたか」の年表＋ API 索引。
- 古いバージョン節は、移植・互換調査・サンプルの出自確認用。

## 2025（このページ外・要約）

| 項目 | 内容 |
|------|------|
| Python | **3.11** |
| UI | **PySide6**（PySide2 不可） |
| 詳細 | [prerequisites.md](../prerequisites.md) |

## 目次（このページ）

- [What's New in 2024.2](#whats-new-in-20242)
- [What's New in 2024.1](#whats-new-in-20241)
- [What's New in 2024](#whats-new-in-2024)
- [What's New in 2023.2](#whats-new-in-20232)
- [What's New in 2023.1](#whats-new-in-20231)
- [What's New in 2023](#whats-new-in-2023)
- [What's New in 2022](#whats-new-in-2022)
- [What's New in 2021.2](#whats-new-in-20212)
- [What's New in 2021.1](#whats-new-in-20211)
- [What's New in 2021](#whats-new-in-2021)
- [What's New in 2020.2](#whats-new-in-20202)
- [What's New in 2020.1](#whats-new-in-20201)
- [What's New in 2020](#whats-new-in-2020)
- [What's New in 2019.2](#whats-new-in-20192)
- [What's New in 2019.1](#whats-new-in-20191)
- [What's New in 2019](#whats-new-in-2019)

## What's New in 2024.2

### 要点

- **New PyObject: PyResolution** — A new PyObject named PyResolution can be used to get and set the resolution of a node.
- **Updated Commands: Batch** — Most settings in the Colour Source nodes are now available as attributes in the Python API.

### 追加・更新 API（索引）

| API | Type |
|-----|------|
| `flame.PyResolution()` | Constructor |
| `<PyNode>.resolution` | Attribute |
| `flame.PyExporter.include_subtitles` | Attribute |
| `flame.PyExporter.export_subtitles_as_files` | Attribute |
| `flame.PyExporter.export_all_subtitles` | Attribute |
| `<PyNode>.mode` | Attribute |
| `<PyNode>.colour` | Attribute |
| `<PyNode>.luminance` | Attribute |
| `<PyNode>.bars_softness` | Attribute |
| `<PyNode>.gradient_mode` | Attribute |
| `<PyNode>.gradient_direction_mode` | Attribute |
| `<PyNode>.gradient_circular_mode` | Attribute |
| `<PyNode>.bi_gradient_colour_one, <PyNode>.bi_gradient_colour_two` | Attribute |
| `<PyNode>.quad_gradient_colour_top_left, <PyNode>.quad_gradient_colour_top_right, <PyNode>.quad_gradient_colour_bottom_left, <PyNode>.quad_gradient_colour_bottom_right` | Attribute |
| `<PyNode>.resolution_mode` | Attribute |
| `<PyNode>.scaling_presets_value` | Attribute |
| `<PyNode>.adaptive_mode` | Attribute |
| `<PySequence>.import_subtitles_file()` | Function |
| `<PySequence>.subtitles` | Read-Only Property |
| `<PySequence>.subtitles_track` | Attribute |
| `<PySubtitleTrack>.parent` | Read-Only Property |
| `<PySequence>.create_subtitle()` | Function |
| `<PySubtitle>.name` | Attribute |
| `<PySubtitleTrack>.segments` | Read-Only Property |
| `<PySegment>.create_effect("Subtitle")` | Function |
| `flame.delete(PySubtitleTrack)` | Function |
| `<PySubtitleTrack>.export_as_srt_file()` | Function |

### 公式サブ節

- New PyObject: PyResolution
- Updated PyObject: PyExport
- Updated Commands: Batch
- Update Commands: Resize
- New Commands for Subtitles

## What's New in 2024.1

Now that you can burn a Metadata Overlay on media exported by a Batch Write File node, you can also enable and disable it using the Python API. For more details on Metadata Overlay in Batch, see the What's New in 2024.1.

### 追加・更新 API（索引）

| API | Type |
|-----|------|
| `<PyWriteFileNode>.metadata_overlay` | Attribute |
| `<PyWriteFileNode>.metadata_overlay_context` | Attribute |

## What's New in 2024

The Start Frame information is now available in Python Hooks as startFrame.

### 要点

- **Start Frame Workflow** — These new properties and functions allow control over the start frame.

### 追加・更新 API（索引）

| API | Type |
|-----|------|
| `<PyNode>.smart_replace` | Attribute |
| `<PyClip>.start_frame` | Read-Only Property |
| `<PyClip>.change_start_frame()` | Function |

### 公式サブ節

- Start Frame Workflow

## What's New in 2023.2

### 要点

- **Renamed Python Directories** — The new directory /opt/Autodesk/<version>/python_utilities replaces the old /opt/Autodesk/<version>/python_examples directory. It contains a scripts directory for useful custom actions, and an examples directory for examples of python API uses.
- **Custom Layout in the Context Menu** — You now have more control over the placement of custom actions in context menus.
- **Directory as arg** — You can now pass a directory as an argument to flame.import_clips().
- **Changes to flame.batch.create_group()** — You no longer have to set the duration argument for the flame.batch.create_group() function.

### 追加・更新 API（索引）

| API | Type |
|-----|------|
| `<PyWriteFileNode>.add_to_workspace` | Attribute |
| `<PyRenderNode>.out_mark` | Attribute |
| `<PyBatchIteration>.iteration_number` | Read-Only Property |
| `<PyWriteFileNode>.get_resolved_media_path()` | Function |
| `<PyNode>.set_channel_name()` | Function |
| `<PyNode>.channels` | Read-Only Property |

### 公式サブ節

- Renamed Python Directories
- Custom Layout in the Context Menu
- Directory as arg
- Changes to flame.batch.create_group()
- New Attributes and Functions

## What's New in 2023.1

You can now use the Python API to display Flame browser for users to select files. The PyBrowser object is used to set a file selection and settings as variables to be used by other functions like flame.import_clips(). The advantage of using a PyBrowser over a Qt dialog box is user interface consistency and access to features such as bookmarks.

### 要点

- **File Browser** — You can now use the Python API to open a Flame file browser for users to select files. The PyBrowser object itself is only used to set a file selection and settings as variables that can be used by other functions like flame.import_clips(). The advantage of using a PyBrowser over a Qt dialog box is user interface consistency and access to features such as the Flame bookmarks.

### 追加・更新 API（索引）

| API | Type |
|-----|------|
| `flame.messages.show_in_dialog()` | Function |
| `flame.messages.show_in_console()` | Function |
| `flame.messages.clear_console()` | Function |
| `flame.batch.import_clips()` | Function |
| `flame.browser.show()` | Function |
| `flame.browser.selection` | Read-Only Property |
| `flame.browser.resolution` | Read-Only Property |
| `flame.browser.width` | Read-Only Property |
| `flame.browser.height` | Read-Only Property |
| `flame.browser.bit_depth` | Read-Only Property |
| `flame.browser.frame_ratio` | Read-Only Property |
| `flame.browser.scan_mode` | Read-Only Property |
| `flame.browser.colour_space` | Read-Only Property |
| `flame.browser.resize_mode` | Read-Only Property |
| `flame.browser.resize_filter` | Read-Only Property |
| `flame.browser.sequence_mode` | Read-Only Property |
| `flame.mediahub.files.options.set_tagged_colour_space` | Attribute |
| `flame.mediahub.files.options.resize_mode` | Attribute |
| `flame.mediahub.files.options.resize_filter` | Attribute |
| `flame.mediahub.files.options.resolution` | Attribute |
| `flame.mediahub.files.options.width` | Attribute |
| `flame.mediahub.files.options.height` | Attribute |
| `flame.mediahub.files.options.frame_ratio` | Attribute |
| `flame.mediahub.files.options.pixel_ratio` | Attribute |
| `flame.mediahub.files.options.bit_depth` | Attribute |
| `flame.mediahub.files.options.scan_mode` | Attribute |
| `flame.mediahub.files.options.sequence_mode` | Attribute |
| `flame.import_clips()` | Function |
| `<PySegment>.get_colour_space` | Function |
| `<PyTransition>.set_dissolve_to_from_colour()` | Function |
| `<PyTransition>.set_fade_to_from_silence()` | Function |
| `<PyNode>.slope_blue` | Attribute |
| `<PyNode>.offset_blue` | Attribute |
| `<PyNode>.power_blue` | Attribute |
| `<PyNode>.saturation` | Attribute |
| `<PyNode>.style` | Attribute |
| `<PyNode>.invert` | Attribute |
| `<PyArchiveEntry>.clear_colour()` | Function |
| `<PyTrack>.cut()` | Function |
| `<PySegment>.clear_colour()` | Function |
| `PyClip.create_container()` | Function |
| `PySegment.container_clip()` | Read-Only Property |
| `PyClip.open_container()` | Function |
| `PyClip.close_container()` | Function |
| `<PySequence>.padding_end` | Attribute |
| `<PySegment>.create_unlinked_segment()` | Function |
| `<PySegment>.source_audio_track` | Read-Only Property |
| `<PyTrack>.insert_transition()` | Function |
| `<PyTransition>.set_transition()` | Function |
| `<PyTransition>.slide()` | Function |
| `<PyTransition>.name` | Attribute |
| `<PyTransition>.duration` | Attribute |
| `<PyTransition>.alignment` | Attribute |
| `<PyTransition>.selected` | Attribute |
| `<PyTransition>.type` | Attribute |
| `<PyTransition>.record_time` | Read-Only Property |
| `<PyTransition>.in_offset` | Read-Only Property |
| `<PyTransition>.parent` | Read-Only Property |
| `<PyClip>.selected_transitions` | Read-Only Property |
| `<PyTimeline>.current_transition` | Read-Only Property |

### 公式サブ節

- API New Attributes and Functions
- General
- Batch
- File Browser
- MediaHub
- Clip & Segment
- Transitions
- Look
- Media Panel
- Timeline
- Transitions

## What's New in 2023

Flame Family now installs and uses Python 3.9.7 instead of version 3.7.9 used in Flame Family 2022. The app_started python hook has been removed. Use the Python hook app_initialized instead.

### 要点

- **GMask Tracer & Image** — Python hook get_action_custom_ui_actions, used by the Action family nodes to add custom actions, is now available in Image and GMask Tracer.

### 追加・更新 API（索引）

| API | Type |
|-----|------|
| `flame.mediahub.files.options.multi_channel_mode` | Attribute |
| `flame.mediahub.files.options.cache_mode` | Attribute |
| `flame.mediahub.files.options.proxies_mode` | Attribute |
| `flame.mediahub.files.options.cache_and_proxies_all_versions` | Attribute |
| `<PyReelGroup>.save()` | Function |
| `<PyLibrary>.opened` | Read-Only Property |
| `<PySequence>.overwrite()` | Function |
| `<PySequence>.lift_selection_to_media_panel()` | Function |
| `flame.delete(<PySegment>)` | Function |
| `flame.timeline.type` | Attribute |
| `flame.timeline.clip` | Read-Only Property |
| `flame.timeline.current_effect` | Read-Only Property |
| `<PySegment>.set_gap_colour()` | Function |
| `<PySegment>.match()` | Function |
| `<PySegment>.smart_replace_media()` | Function |
| `<PySegment>.slip()` | Function |
| `<PyTimelineFX>.slide_keyframes()` | Function |
| `<PyAudioTrack>.copy_to_media_panel()` | Function |
| `<PySegment>` | Read-Only Property |
| `<PySegment>.matte_channels` | Read-Only Property |
| `<PySegment>.matte_channel` | Read-Only Property |
| `<PySegment>.matte_mode` | Read-Only Property |
| `<PySegment>.set_matte_channels()` | Function |
| `<PySegment>.dynamic_comment` | Attribute |

### 公式サブ節

- GMask Tracer & Image
- API New Attributes and Functions

## What's New in 2022

### 要点

- **Moving to Python 3.7** — Flame, Flare and Flame Assist now use Python 3.7. This means that you need to convert your Python 2 scripts to Python 3.
- **Python Console Update** — The Python console, Flame menu > Python > Python Console, now benefits from the following improvements:
- **Python API Updates** — Expanded PyActionNode ReachEvery functions, attributes, and properties available in the PyActionNode object are now available in GMask Tracer and Image.

### 追加・更新 API（索引）

| API | Type |
|-----|------|
| `<PyActionNode>.object_dual_mode` | Attribute |
| `<PyActionNode>.current_tab` | Attribute |
| `flame.duplicate(<PyObject>)` | Function |
| `<PyMediaPanel>.move()` | Function |
| `<PySegment>.create_connection()` | Function |
| `<PySegment>.remove_connection()` | Function |
| `<PySegment>.sync_connected_segments()` | Function |
| `<PySegment>.connected_segments()` | Function |
| `<PySegment>.duplicate_source()` | Function |
| `<PySegment>.shared_source_segments()` | Function |
| `<PyTimelineFx>.sync_connected_segments()` | Function |

### 公式サブ節

- Moving to Python 3.7
- Python Console Update
- Python API Updates
- New in Action
- New in Action/Image/Gmask Tracer
- New in Media Panel
- New in Timeline
- New TimelineFX

## What's New in 2021.2

New in the Python API for Flame Family 2021.2 Update: New functions for MediaHub: set or get MediaHub file or archive paths. New attributes for the following Batch nodes: Deinterlace Difference Matte Exposure Monochrome Write File

### 追加・更新 API（索引）

| API | Type |
|-----|------|
| `flame.mediahub.archives.set_path()` | Function |
| `<PyNode>.dominance` | Attribute |
| `<PyNode>.interpolation` | Attribute |
| `<PyNode>.tolerance_v` | Attribute |
| `<PyNode>.softness_v` | Attribute |
| `<PyNode>.gain_yu` | Attribute |
| `<PyNode>.lift_yuv` | Attribute |
| `<PyNode>.channel_v` | Attribute |
| `<PyNode>.space_rgb` | Attribute |
| `<PyNode>.input_data_type` | Attribute |
| `<PyNode>.exposure_blue` | Attribute |
| `<PyNode>.contrast_blue` | Attribute |
| `<PyNode>.pivot_blue` | Attribute |
| `<PyNode>.channel` | Attribute |
| `<PyNode>.level` | Attribute |

### 公式サブ節

- MediaHub
- Batch - Deinterlace
- Batch - Difference Matte
- Batch - Exposure
- Batch - Monochrome
- Batch - Write File

## What's New in 2021.1

The Python API is augmented with additional methods and properties in the Flame module, Action, Batch, and Timeline groups and segments.

### 追加・更新 API（索引）

| API | Type |
|-----|------|
| `flame.get_current_tab()` | Function |
| `flame.set_current_tab()` | Function |

### 公式サブ節

- Flame
- Action
- Batch
- Timeline Groups
- Timeline Segments

## What's New in 2021

The Python API is augmented with additional methods in Action, Batch, and Project management.

### 追加・更新 API（索引）

| API | Type |
|-----|------|
| `<PyCoNode>.pos_y` | Attribute |
| `<PyActionNode>.cursor_position` | Read-Only Property |
| `<PyClipNode>` | Read-Only Property |
| `flame.batch.cursor_position` | Read-Only Property |
| `<PyNode>.compress_mode` | Attribute |
| `<PyNode>.colour_type` | Attribute |
| `flame.project.current_project.nickname` | Read-Only Property |

### 公式サブ節

- Action

## What's New in 2020.2

Here are the updates to the Python API for this 2020.2 Update release. Attributes for the Comp and Burn-In Letterbox Timeline FX can now be modified on a timeline segment. Python functions can be executed asynchronously at an undetermined time in Flame's idle loop using the flame.schedule_idle_event(). The software automatically triggers the Flame idle loop when it doesn't register any activity (pointer movement, playback, rendering, etc.) for a…

## What's New in 2020.1

Here are the updates to the Python API for this 2020.1 Update release. flame.execute_shortcut(): Execute the specified keyboard shortcut. Updates to Action: <PyNodeObject>.cache_range(): You can now cache range on Z-Depth and Normals map, in addition to the previously accessible Motion Vectors map. Compass Node: Use a Compass node in Action. Create it with <PyCoNode>.encompass_nodes. Updates to Batch: flame.batch.create_node(): Create Matchbox, …

### 要点

- **Deprecated Entities** — The property <PyProject>.current_name is now deprecated and replaced with <PyProject>.name.

### 公式サブ節

- Deprecated Entities

## What's New in 2020

We've augmented the Python API with the following: <PyObject>.parent: Get the parent of the object. flame.import_clips(): Import a clip to a specified PyReel, PyLibrary, PyFolder or PySharedLibrary. New Batch Nodes are now available with the Python API: Auto-Matte Average Burn-in Letterbox Clamp Compound Deal To support the import of UDIM textures, some <PyActionNode> functions are augmented: <PyActionNode>.import_fbx: New is_udim parameter. <Py…

## What's New in 2019.2

New Classes: PyMarker: Get and set information on Markers and Segment Markers. PySegment: Access a sequence's segment, adding Timeline FX or read its source path. PyTime: Define a time in frame or timecode that can then be used in a variety of attributes and functions. PyTimelineFX: Get a Timeline FX, or bypass it. Notable updates to classes: PyBatch : The Render Node supports for bit depth and render destination. PyClip now has the same propert…

## What's New in 2019.1

### 要点

- **Action Scriptability** — With the Python API, you create scripts to:

### 公式サブ節

- General Improvements
- Action Scriptability
- Media Management
- Import & Export

## What's New in 2019

### 要点

- **Media Panel Scriptability** — You can now script the Media Panel.
- **Catching Exception** — Exceptions can now be caught in a Python script. For example, the following will now work:
- **Additional Python API Improvements** — The address of a python object is now preserved, allowing for two variables to share a single address pointing to the same python object.

### 公式サブ節

- Media Panel Scriptability
- Catching Exception
- Additional Python API Improvements

---

## 注記

- API 表は Help の `Command:` 行および Command/Type/Description 表から抽出。説明・サンプル全文は一次情報 HTML を参照。
- 属性の型・値域は [attributes/](./attributes/) を優先。
- Autodesk Help は CC BY-NC-SA 等の表記あり。Embr 向け要約であり公式の代替ではない。
