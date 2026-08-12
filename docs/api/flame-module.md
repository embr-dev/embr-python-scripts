# flame モジュール索引（Flame 2025）

公式 Help「Autodesk Flame Python: flame module」から抽出した索引。
メソッド／モジュール関数の情報量は維持し、**属性の詳細は [attributes/](./attributes/) に集約**する。

| 項目 | 内容 |
|------|------|
| 一次情報 | `docs/API Documentation/Autodesk Flame Family Python Module/` |
| 公開メソッド（dunder 除く） | 406 |
| クラス節 | 52 |
| モジュール Functions | 26 |
| モジュール Data | 10 |

関連: [attributes/](./attributes/) · [defines.md](./defines.md) · [recipes.md](./recipes.md) · [getting-started.md](./getting-started.md) · [hooks.md](./hooks.md)

## 目次

1. [カバレッジ](#カバレッジ)
2. [モジュール Data](#モジュール-data)
3. [モジュール Functions](#モジュール-functions)
4. [クラス索引](#クラス索引)
5. [クラス別メソッド](#クラス別メソッド)

---

## カバレッジ

| 公式の塊 | この文書 | 備考 |
|----------|----------|------|
| 末尾 Functions（26） | 収録 | 抜けなし |
| 末尾 Data（10） | 収録 | 抜けなし |
| 各クラス公開 Static methods | 収録 | 突合差分 0 |
| 属性中心クラス（PyTime 等） | 名前のみ → [attributes/](./attributes/) | 属性本文は Attributes 側 |
| Read-only / Data descriptors | [attributes/](./attributes/) | メソッド索引から分離 |
| Data and other（PresetType 等） | [attributes/Data_and_other_attributes.md](./attributes/Data_and_other_attributes.md) | |
| dunder | 省略 | `__init__` 等 |

---

## モジュール Data

公式 Help 末尾 **Data**。呼び出しは `flame.<name>`。

| 属性 | 型 | 用途 |
|------|-----|------|
| `flame.batch` | `PyBatch` | 現在の Batch グループ |
| `flame.browser` | `PyBrowser` | ブラウザ |
| `flame.media_panel` | `PyMediaPanel` | Media Panel（move / copy / selected_entries 等） |
| `flame.mediahub` | `PyMediaHub` | MediaHub |
| `flame.messages` | `PyMessages` | メッセージバー（show_in_console 等） |
| `flame.project` | `PyProjectSelector` | 互換用のプロジェクト選択子 |
| `flame.projects` | `PyProjectSelector` | **推奨**（2020.1+）。`current_project` など |
| `flame.search` | `PySearch` | 検索 |
| `flame.timeline` | `PyTimeline` | タイムライン |
| `flame.users` | `PyUsers` | ユーザー（current_user 等） |

```python
import flame

batch = flame.batch
project = flame.projects.current_project
flame.messages.show_in_console("ok", "info", 3)
```

到達パス: [defines.md](./defines.md)。属性詳細: [attributes/README.md](./attributes/README.md)。

---

## モジュール Functions

公式 Help 末尾 **Functions**。呼び出しは `flame.<name>(...)`。

| 関数 | 説明（Help 抜粋） |
|------|-------------------|
| `delete(...)` | delete ( ( PyFlameObject )object [, (bool)confirm=True]) -> bool : Delete the target object. |
| `dump(...)` | dump () -> None |
| `duplicate(...)` | duplicate ( ( PyFlameObject )object [, (bool)keep_node_connections=False]) -> object : Duplicate the target object. |
| `duplicate_many(...)` | duplicate_many ( (list)object_list [, (bool)keep_node_connections=False]) -> list : Duplicate the target objects. |
| `execute_command(...)` | *(説明なし — Help 原文も空に近い)* |
| `execute_shortcut(...)` | execute_shortcut ( (str)description [, (bool)update_list=True]) -> bool : Execute the Flame shortcut. description -- The description in the Keyboard Shortcut editor. |
| `exit(...)` | exit () -> None : Exit the application. |
| `find_by_name(...)` | find_by_name ( (str)name [, (object)parent=None]) -> list : Find a Flame object in the Media Panel by name. |
| `find_by_uid(...)` | find_by_uid ( (str)uid) -> object : Find a Flame object in the Media Panel by UID. |
| `find_by_wiretap_node_id(...)` | find_by_wiretap_node_id ( (str)node_id) -> object : Find a Flame object in the Media Panel by Wiretap Node ID. |
| `get_current_tab(...)` | get_current_tab () -> str : Get the current tab name. |
| `get_home_directory(...)` | get_home_directory () -> str : Get the application home directory. |
| `get_init_cfg_path(...)` | get_init_cfg_path () -> str : Get the application init configuration file. |
| `get_selected_segment(...)` | get_selected_segment () -> object |
| `get_selected_version(...)` | get_selected_version () -> object |
| `get_version(...)` | get_version () -> str : Get the application version. |
| `get_version_major(...)` | get_version_major () -> str : Get the application major version. |
| `get_version_minor(...)` | get_version_minor () -> str : Get the application minor version. |
| `get_version_patch(...)` | get_version_patch () -> str : Get the application patch version. |
| `get_version_stamp(...)` | get_version_stamp () -> str : Get the application version stamp. |
| `go_to(...)` | go_to ( (str)tab) -> bool : Deprecated / use set_current_tab () instead. |
| `import_clips(...)` | import_clips ( (object)path [, (object)destination=None]) -> list : Import one or many clips from a path. Keyword arguments: path -- The path to the media can be: - A path to a single media file. - A path to a sequence of media files (ie "/dir/clip.[100-2000].dpx"). - A folder containing media files. - A pattern to media files (ie "/dir/{name}_v{version}.{frame}.{extension}"). - A list of paths. destination -- Flame object containing a clip like a reel or a folder object. |
| `press_button(...)` | press_button ( (str)name [, (float)param=0]) -> bool : Press the Flame button or assign a given value to it's variable. name -- The unique name of the menu item. param -- An optional value to be assigned to the button's variable. |
| `schedule_idle_event(...)` | schedule_idle_event ( (object)function [, (int)delay=0]) -> None : Register a function callback that will be called eventually when the application is idle. The function must not block and be quick since it will be executed in the main application thread. Keyword arguments: function -- Callable object to be called. delay -- Minimum time (in seconds) to wait before calling function. |
| `set_current_tab(...)` | set_current_tab ( (str)arg1) -> bool : Set the given tab as the active environment. Keyword arguments: tab -- The tab to set active (MediaHub, Conform, Timeline, Effects, Batch, Tools) |
| `set_render_option(...)` | set_render_option ( (str)render_option [, (str)render_context='']) -> bool : Set the default render option. Keyword arguments: render_option -- Defines the rendering method used. (Foreground, Background Reactor, Background Reactor (Auto), Burn) render_context -- Defines the rendering context. (Timeline, Conform, Effects, BFX, Batch). None for all of them. Note: Batch does not support Background Reactor (Auto) and will default to Background Reactor if (Auto) is passed. |

---

## クラス索引

| クラス | メソッド数 | Attributes |
|--------|------------|------------|
| [`PyProject`](#pyproject) | 7 | [doc](./attributes/PyProject.md) |
| [`PyBatch`](#pybatch) | 35 | [doc](./attributes/PyBatch.md) |
| [`PyClip`](#pyclip) | 19 | [doc](./attributes/PyClip.md) |
| [`PySequence`](#pysequence) | 31 | [doc](./attributes/PySequence.md) |
| [`PyDesktop`](#pydesktop) | 8 | [doc](./attributes/PyDesktop.md) |
| [`PyWorkspace`](#pyworkspace) | 8 | [doc](./attributes/PyWorkspace.md) |
| [`PyLibrary`](#pylibrary) | 13 | [doc](./attributes/PyLibrary.md) |
| [`PyFolder`](#pyfolder) | 9 | [doc](./attributes/PyFolder.md) |
| [`PyReel`](#pyreel) | 7 | [doc](./attributes/PyReel.md) |
| [`PyReelGroup`](#pyreelgroup) | 7 | [doc](./attributes/PyReelGroup.md) |
| [`PyNode`](#pynode) | 6 | [doc](./attributes/PyNode.md) |
| [`PySegment`](#pysegment) | 25 | [doc](./attributes/PySegment.md) |
| [`PyTrack`](#pytrack) | 3 | [doc](./attributes/PyTrack.md) |
| [`PyVersion`](#pyversion) | 3 | [doc](./attributes/PyVersion.md) |
| [`PyTimelineFX`](#pytimelinefx) | 5 | [doc](./attributes/PyTimelineFX.md) |
| [`PyMediaPanel`](#pymediapanel) | 2 | [doc](./attributes/PyMediaPanel.md) |
| [`PyMessages`](#pymessages) | 3 | [doc](./attributes/PyMessages.md) |
| [`PyBrowser`](#pybrowser) | 1 | [doc](./attributes/PyBrowser.md) |
| [`PySearch`](#pysearch) | 5 | [doc](./attributes/PySearch.md) |
| [`PyExporter`](#pyexporter) | 3 | [doc](./attributes/PyExporter.md) |
| [`PyActionNode`](#pyactionnode) | 21 | [doc](./attributes/PyActionNode.md) |
| [`PyActionFamilyNode`](#pyactionfamilynode) | 12 | [doc](./attributes/PyActionFamilyNode.md) |
| [`PyArchiveEntry`](#pyarchiveentry) | 4 | [doc](./attributes/PyArchiveEntry.md) |
| [`PyAttribute`](#pyattribute) | 2 | [doc](./attributes/PyAttribute.md) |
| [`PyAudioTrack`](#pyaudiotrack) | 1 | [doc](./attributes/PyAudioTrack.md) |
| [`PyBatchIteration`](#pybatchiteration) | 5 | [doc](./attributes/PyBatchIteration.md) |
| [`PyClipNode`](#pyclipnode) | 5 | [doc](./attributes/PyClipNode.md) |
| [`PyCoCameraAnalysis`](#pycocameraanalysis) | 7 | [doc](./attributes/PyCoCameraAnalysis.md) |
| [`PyCoCompass`](#pycocompass) | 5 | [doc](./attributes/PyCoCompass.md) |
| [`PyCompassNode`](#pycompassnode) | 5 | [doc](./attributes/PyCompassNode.md) |
| [`PyCoNode`](#pyconode) | 5 | [doc](./attributes/PyCoNode.md) |
| [`PyGMaskTracerNode`](#pygmasktracernode) | 19 | [doc](./attributes/PyGMaskTracerNode.md) |
| [`PyHDRNode`](#pyhdrnode) | 14 | [doc](./attributes/PyHDRNode.md) |
| [`PyHDRTimelineFX`](#pyhdrtimelinefx) | 14 | [doc](./attributes/PyHDRTimelineFX.md) |
| [`PyImageNode`](#pyimagenode) | 13 | [doc](./attributes/PyImageNode.md) |
| [`PyInferenceNode`](#pyinferencenode) | 5 | [doc](./attributes/PyInferenceNode.md) |
| [`PyLensDistortionNode`](#pylensdistortionnode) | 6 | [doc](./attributes/PyLensDistortionNode.md) |
| [`PyMediaHubFilesEntry`](#pymediahubfilesentry) | 4 | [doc](./attributes/PyMediaHubFilesEntry.md) |
| [`PyMediaHubFilesFolder`](#pymediahubfilesfolder) | 4 | [doc](./attributes/PyMediaHubFilesFolder.md) |
| [`PyMediaHubFilesTab`](#pymediahubfilestab) | 2 | [doc](./attributes/PyMediaHubFilesTab.md) |
| [`PyMediaHubFilesTabOptions`](#pymediahubfilestaboptions) | 1 | [doc](./attributes/PyMediaHubFilesTabOptions.md) |
| [`PyMediaHubProjectsEntry`](#pymediahubprojectsentry) | 4 | [doc](./attributes/PyMediaHubProjectsEntry.md) |
| [`PyMediaHubProjectsFolder`](#pymediahubprojectsfolder) | 4 | [doc](./attributes/PyMediaHubProjectsFolder.md) |
| [`PyMediaHubTab`](#pymediahubtab) | 2 | [doc](./attributes/PyMediaHubTab.md) |
| [`PyMorphNode`](#pymorphnode) | 6 | [doc](./attributes/PyMorphNode.md) |
| [`PyOFXNode`](#pyofxnode) | 6 | [doc](./attributes/PyOFXNode.md) |
| [`PyPaintNode`](#pypaintnode) | 6 | [doc](./attributes/PyPaintNode.md) |
| [`PyRenderNode`](#pyrendernode) | 6 | [doc](./attributes/PyRenderNode.md) |
| [`PySequenceGroup`](#pysequencegroup) | 2 | [doc](./attributes/PySequenceGroup.md) |
| [`PySubtitleTrack`](#pysubtitletrack) | 5 | [doc](./attributes/PySubtitleTrack.md) |
| [`PyTransition`](#pytransition) | 4 | [doc](./attributes/PyTransition.md) |
| [`PyWriteFileNode`](#pywritefilenode) | 7 | [doc](./attributes/PyWriteFileNode.md) |

属性中心（メソッドほぼ無し）:

- [`PyFlameObject`](./attributes/PyFlameObject.md)
- [`PyMarker`](./attributes/PyMarker.md)
- [`PyMediaHub`](./attributes/PyMediaHub.md)
- [`PyProjectSelector`](./attributes/PyProjectSelector.md)
- [`PyResolution`](./attributes/PyResolution.md)
- [`PyTime`](./attributes/PyTime.md)
- [`PyTimeline`](./attributes/PyTimeline.md)
- [`PyUser`](./attributes/PyUser.md)
- [`PyUsers`](./attributes/PyUsers.md)

---

## クラス別メソッド

### `PyProject`

メソッド数: **7** · [Attributes](./attributes/PyProject.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `create_shared_library(...)` | create_shared_library ( ( PyProject )arg1, (str)name) -> object : Create a new Shared Library in the Project. |
| `get_available_colour_spaces(...)` | get_available_colour_spaces ( ( PyProject )arg1) -> object : Return a list of all the available colour spaces. |
| `refresh_shared_libraries(...)` | refresh_shared_libraries ( ( PyProject )arg1) -> bool : Refresh the Shared Libraries list in the Media Panel. |
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PyBatch`

メソッド数: **35** · [Attributes](./attributes/PyBatch.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `append_setup(...)` | append_setup ( ( PyBatch )arg1, (str)setup_path [, (bool)confirm=True]) -> bool : Append a Batch setup file to the existing Batch setup. Keywords arguments: setup_path -- A path and a filename must be defined as arguments. confirm -- Set to True (default) to display a dialogue box in case of |
| `append_to_batch(...)` | append_to_batch ( ( PyBatch )arg1, ( PyBatchIteration )batch_iteration) -> bool : Append a Batch Iteration object to the current Batch Group. A duplicate Batch Iteration object is renamed to the next available *vDD*. Batch Iteration objects are displayed in the Iterations folder. Iterations folder is a UI construction, not accessible directly. |
| `append_to_setup(...)` | append_to_setup ( ( PyBatch )arg1, ( PyBatchIteration )batch_iteration) -> bool : Append a Batch Iteration object to the Batch Group's setup. |
| `clear(...)` | clear ( ( PyBatch )arg1 [, (bool)confirm=True]) -> bool : Clear the Batch Group. |
| `clear_all_contexts(...)` | clear_all_contexts ( ( PyBatch )arg1) -> bool : Clear all registered Context views in the Batch Group. |
| `clear_colour(...)` | clear_colour ( ( PyBatch )arg1, (int)index) -> bool : Clear the colour of the the Batch Group. |
| `clear_context(...)` | clear_context ( ( PyBatch )arg1, (int)index) -> bool : Clear a specific Context view in the Batch Group. |
| `clear_setup(...)` | clear_setup ( ( PyBatch )arg1) -> bool : Clear the Batch Group's setup. |
| `close(...)` | close ( ( PyBatch )arg1) -> bool : Close the Batch Group. You cannot close the Batch Group currently selected. Closing a Batch Group frees up the application it occupies when open. The size of the used memory is significant if in Batch Group schematic hosts many Action nodes with textures or 3D geoms. |
| `connect_nodes(...)` | connect_nodes ( ( PyBatch )arg1, ( PyNode )output_node, (str)output_socket_name='Default', ( PyNode )input_node [, (str)input_socket_name='Default']) -> bool : Connect two nodes in the Batch schematic. Keyword arguments: output_node -- The Batch node object, the origin of the connection. output_socket_name -- The name of the output socket where the connector starts; use *Default* to use the first output socket, usually *Result*. input_node -- The child Batch node object, the target of the connec |
| `create_batch_group(...)` | create_batch_group ( ( PyBatch )arg1, (str)name [, (int)nb_reels=4 [, (int)nb_shelf_reels=1 [, (list)reels=[] [, (list)shelf_reels=[] [, (int)start_frame=1 [, (object)duration=None]]]]]]) -> object : Create a new Batch Group object in the Desktop catalogue. Keyword arguments: name -- Name of the Batch Group. nb_reels -- Number of reels created. *reels* overrides *nb_reels*. nb_shelf_reels -- Number of shelf reels. The first shelf reel created is named Batch Renders. *shelf_reels* ovverides *nb_s |
| `create_node(...)` | create_node ( ( PyBatch )arg1, (str)node_type [, (str)file_path='']) -> object : Create a Batch node object in the Batch schematic. Keyword argument: node_type -- Must be a value from the PyBatch .node_types. |
| `create_reel(...)` | create_reel ( ( PyBatch )arg1, (str)name) -> object : Create a new Schematic Reel in the Batch Gtroup. |
| `create_shelf_reel(...)` | create_shelf_reel ( ( PyBatch )arg1, (str)name) -> object : Create a new Shelf Reel in the Batch Group. |
| `disconnect_node(...)` | disconnect_node ( ( PyBatch )arg1, ( PyNode )node [, (str)input_socket_name='']) -> bool : Disconnect the input links of a given node, given an input socket. Keyword arguments: node -- The Batch node object, the origin of the connection. input_socket_name -- The name of the input socket to disconnect. |
| `encompass_nodes(...)` | encompass_nodes ( ( PyBatch )arg1, (list)nodes) -> object : Create a Compass around a list of nodes in the Batch schematic. Keyword argument: nodes -- List of strings of node names. |
| `frame_all(...)` | frame_all ( ( PyBatch )arg1) -> bool : Set the Batch schematic view to frame all the nodes in the Batch schematic. |
| `frame_selected(...)` | frame_selected ( ( PyBatch )arg1) -> bool : Set the Batch schematic view to frame the nodes selected in the Batch schematic. |
| `get_node(...)` | get_node ( ( PyBatch )arg1, (str)node_name) -> object : Return a Batch node object with a name matching the parameter. Every node in a Batch schematic has a unique name: no duplicates allowed. Keyword argument: node_name -- Node name. |
| `go_to(...)` | go_to ( ( PyBatch )arg1) -> bool : Display and set the Batch tab as the active environment. |
| `import_clip(...)` | import_clip ( ( PyBatch )arg1, (str)file_path, (str)reel_name) -> object : Import a clip using the Import node, and create a Clip node. Keyword arguments: file_path -- The path to the media can be: - A path to a single media file. - A path to a sequence of media files (ie "/dir/clip.[100-2000].dpx"). - A pattern to media files (ie "/dir/name_v{version}.{frame}.{extension}").reel_name -- The name of the destination Schematic Reel. |
| `import_clips(...)` | import_clips ( ( PyBatch )arg1, (object)file_paths, (str)reel_name) -> object : Import clips using the Import node, and then create Clip nodes in the Schematic Reel. Keyword arguments: file_paths -- A path, or a list of paths, to the media that can be: - A path to a single media file. - A path to a sequence of media files (ie "/dir/clip.[100-2000].dpx"). - A pattern to media files (ie "/dir/name_v{version}.{frame}.{extension}").reel_name -- The name of the destination Schematic Reel. |
| `iterate(...)` | iterate ( ( PyBatch )arg1 [, (int)index=-1]) -> object : Iterate the current Batch Setup, creating a new iteration named BatchSetupName_X, where X is the Batch Iteration's index, and starts at 001. Keyword argument: index -- Specifies the iteration's index. If none is specified, the iteration is assigned the next available index (max index + 1). If the index matches that of an existing Batch Iteration, its overwrites the iteration without warning. |
| `load_setup(...)` | load_setup ( ( PyBatch )arg1, (str)setup_path) -> bool : Load a Batch setup from disk and replace the current Batch Group's setup. Keyword argument: setup_path -- Filepath + Batch Setup filename. |
| `mimic_link(...)` | mimic_link ( ( PyBatch )arg1, ( PyNode )leader_node, ( PyNode )follower_node) -> bool : Create a Mimic Link between two Batch nodes. They must be of the same node_type. Keyword arguments: leader_node -- The node being mimicked. follower_node -- The node doing the mimicking. |
| `open(...)` | open ( ( PyBatch )arg1) -> bool : Open the Batch Group and display it in the Batch view. |
| `open_as_batch_group(...)` | open_as_batch_group ( ( PyBatch )arg1 [, (bool)confirm=True]) -> bool : Open a Batch Group as a new Batch Group, adding it to PyDesktop .batch_groups. Can only be called from a Library. |
| `organize(...)` | organize ( ( PyBatch )arg1) -> bool : Clean up the nodes layout in the Batch schematic. |
| `render(...)` | render ( ( PyBatch )arg1 [, (str)render_option='Foreground' [, (bool)generate_proxies=False [, (bool)include_history=False]]]) -> bool : Trigger the rendering of the Batch Group setup. Every active Render and Write File nodes render. If specified render_option is not supported by the workstation, returns an error. Keyword arguments: render_option -- Defines the rendering method used. (Foreground, Background Reactor, Burn) generate_proxies -- Set to True to render at proxy resolution. (Default: F |
| `replace_setup(...)` | replace_setup ( ( PyBatch )arg1, ( PyBatchIteration )batch_iteration [, (bool)confirm=True]) -> bool : Replace the Batch Group setup with the specified Batch Iteration. Cannot be called on the Batch Group currently selected and displayed in the Batch view. |
| `save(...)` | save ( ( PyBatch )arg1) -> object : Save the Batch Group to the location defined by PyDesktop .destination. |
| `save_current_iteration(...)` | save_current_iteration ( ( PyBatch )arg1) -> object : Save the current Batch Group setup to the location defined by PyDesktop .destination. |
| `save_setup(...)` | save_setup ( ( PyBatch )arg1, (str)setup_path) -> bool : Save the Batch Group setup to disk. Includes media paths for clip node object, but not the media files themselves. Keyword argument: setup_path -- The filepath includes the filename. File extension must be .batch. |
| `select_nodes(...)` | select_nodes ( ( PyBatch )arg1, (object)nodes) -> bool : Select nodes. Keyword argument: nodes -- A list of the names of Batch node objects. |
| `set_viewport_layout(...)` | set_viewport_layout ( ( PyBatch )arg1, (object)num_views) -> bool : Set the viewport layout for Batch. Keyword argument: num_views -- The layout used. (1-Up, 2-Up, 3-Up, 3-Up Split Top, 3-Up Split Left, 3-Up Split Right, 3-Up Split Bottom, 4-Up Split, 4-Up) |

### `PyClip`

メソッド数: **19** · [Attributes](./attributes/PyClip.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `cache_media(...)` | cache_media ( ( PyClip )arg1 [, (str)mode='current']) -> bool : Cache the Clip's linked media. Keyword argument: mode -- Determine the version to cache (currently selected or all versions). All Versions is only useful with to multi-version clips (Current, All Versions) |
| `change_dominance(...)` | change_dominance ( ( PyClip )arg1, (str)scan_mode) -> None : Change the Clip's dominance. Changes only the clip's metadata. Keyword argument: scan_mode -- Field dominance. (P, F1, F2) |
| `change_start_frame(...)` | change_start_frame ( ( PyClip )arg1, (int)start_frame [, (bool)use_segment_connections=True]) -> None : Modify the start frame of a source Clip. Keywords argument: start_frame -- New start frame of the clip. use_segment_connections -- Sync the start frame of connected segments. |
| `close_container(...)` | close_container ( ( PyClip )arg1) -> None : Close the container timeline if the Clip is inside a container. |
| `create_marker(...)` | create_marker ( ( PyClip )arg1, (object)location) -> object : Add a Marker to the Clip.Keyword argument: location -- The frame where the marker gets created. |
| `cut(...)` | cut ( ( PyClip )arg1, ( PyTime )cut_time) -> None : Cut all tracks of the Clip. |
| `flush_cache_media(...)` | flush_cache_media ( ( PyClip )arg1 [, (str)mode='current']) -> bool : Flush the Clip's media cache. Keyword argument: mode -- Determine the version's cache to flush. (Current, All Versions, All But Current) |
| `flush_renders(...)` | flush_renders ( ( PyClip )arg1) -> None : Flush the Clip's TimelineFX renders. |
| `get_colour_space(...)` | get_colour_space ( ( PyClip )arg1 [, ( PyTime )time=None]) -> str : Return the colour space at the requested time. Use current_time when no time is supplied. |
| `is_rendered(...)` | is_rendered ( ( PyClip )arg1 [, (bool)top_only=False [, (str)render_quality='Full Resolution']]) -> bool : Return if a Clip is rendered. The following attributes can be defined: top_only, render_quality. |
| `open_as_sequence(...)` | open_as_sequence ( ( PyClip )arg1) -> object : Open the Clip as a Sequence. Mutates the PyClip object into a PySequence object. |
| `open_container(...)` | open_container ( ( PyClip )arg1) -> bool : Open the container timeline if the Clip is inside a container. |
| `reformat(...)` | reformat ( ( PyClip )arg1 [, (int)width=0 [, (int)height=0 [, (float)ratio=0.0 [, (int)bit_depth=0 [, (str)scan_mode='' [, (str)frame_rate='' [, (str)resize_mode='Letterbox']]]]]]]) -> None : Reformat the Clip to the specified format. Keywords arguments: width -- Integer between 24 and 16384. height -- Integer between 24 and 16384. ratio -- Frame aspect ratio. Float between 0.01 and 100. bit_depth -- Bit depth. (8, 10, 12, 16 or 32) scan_mode -- Scan mode of the sequence. (F1, F2, P) frame_rate  |
| `render(...)` | render ( ( PyClip )arg1 [, (str)render_mode='All' [, (str)render_option='Foreground' [, (str)render_quality='Full Resolution' [, (str)effect_type='' [, (str)effect_caching_mode='Current' [, (bool)include_handles=False]]]]]]) -> bool : Trigger a render of the Clip The following attributes can be defined: render_mode, render_option, render_quality, effect_type, effect_caching_mode and include_handles. |
| `save(...)` | save ( ( PyClip )arg1) -> bool : Save the Clip to the defined save destination. |
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PySequence`

メソッド数: **31** · [Attributes](./attributes/PySequence.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `copy_selection_to_media_panel(...)` | copy_selection_to_media_panel ( ( PySequence )arg1, ( PyArchiveEntry )destination [, (str)duplicate_action='add']) -> object : Create a new clip by copying the currently selected segments. Return the new PyClip . Keyword arguments: destination -- The PyObject that acts as the destination. duplicate_action -- Action to take when an object with the same name already exists (add or replace). |
| `create_audio(...)` | create_audio ( ( PySequence )arg1 [, (bool)stereo=False]) -> object : Add an Audio Track to the Sequence. |
| `create_container(...)` | create_container ( ( PySequence )arg1) -> object : Create a container with the selected segments or between the in and out marks. |
| `create_group(...)` | create_group ( ( PySequence )arg1, (str)name) -> object : Creates a new PySequenceGroup . The group name must be supplied as argument. |
| `create_subtitle(...)` | create_subtitle ( ( PySequence )arg1) -> object : Add a Subtitle Track to the Sequence. |
| `create_version(...)` | create_version ( ( PySequence )arg1 [, (bool)stereo=False]) -> object : Add a Version to the Sequence. |
| `extract_selection_to_media_panel(...)` | extract_selection_to_media_panel ( ( PySequence )arg1 [, ( PyArchiveEntry )destination=None [, (str)duplicate_action='add']]) -> object : Extract the selection from the sequence. Return the new PyClip created from the selection when a destination is supplied. Keyword arguments: destination -- The PyObject that acts as the destination. duplicate_action -- Action to take when an object with the same name already exists (add or replace). |
| `import_subtitles_file(...)` | import_subtitles_file ( ( PySequence )arg1, (str)file_name [, (object)file_type=None [, (bool)align_first_event_to_clip_start=False [, (object)convert_from_frame_rate=None]]]) -> object : Import a subtitles file into a new Subtitles Track. Return the new PySubtitleTrack . Keyword arguments: file_name -- The path and name of the file to import. file_type -- The type of subtitle if it is not the file extension (srt or txt). align_first_event_to_clip_start -- Force the first event to be aligned wit |
| `insert(...)` | insert ( ( PySequence )arg1, ( PyClip )source_clip [, ( PyTime )insert_time=None [, ( PyTrack )destination_track=None]]) -> bool : Creates a new PySequenceGroup . The group name must be supplied as argument. |
| `lift_selection_to_media_panel(...)` | lift_selection_to_media_panel ( ( PySequence )arg1 [, ( PyArchiveEntry )destination=None [, (str)duplicate_action='add']]) -> object : Lift the selection from the sequence. Return the new PyClip created from the selection when a destination is supplied. Keyword arguments: destination -- The PyObject that acts as the destination. duplicate_action -- Action to take when an object with the same name already exists (add or replace). |
| `open(...)` | open ( ( PySequence )arg1) -> bool : Open the Sequence. |
| `overwrite(...)` | overwrite ( ( PySequence )arg1, ( PyClip )source_clip [, ( PyTime )overwrite_time=None [, ( PyTrack )destination_track=None]]) -> bool : Creates a new PySequenceGroup . The group name must be supplied as argument. |
| `cache_media(...)` | cache_media ( ( PyClip )arg1 [, (str)mode='current']) -> bool : Cache the Clip's linked media. Keyword argument: mode -- Determine the version to cache (currently selected or all versions). All Versions is only useful with to multi-version clips (Current, All Versions) |
| `change_dominance(...)` | change_dominance ( ( PyClip )arg1, (str)scan_mode) -> None : Change the Clip's dominance. Changes only the clip's metadata. Keyword argument: scan_mode -- Field dominance. (P, F1, F2) |
| `change_start_frame(...)` | change_start_frame ( ( PyClip )arg1, (int)start_frame [, (bool)use_segment_connections=True]) -> None : Modify the start frame of a source Clip. Keywords argument: start_frame -- New start frame of the clip. use_segment_connections -- Sync the start frame of connected segments. |
| `close_container(...)` | close_container ( ( PyClip )arg1) -> None : Close the container timeline if the Clip is inside a container. |
| `create_marker(...)` | create_marker ( ( PyClip )arg1, (object)location) -> object : Add a Marker to the Clip.Keyword argument: location -- The frame where the marker gets created. |
| `cut(...)` | cut ( ( PyClip )arg1, ( PyTime )cut_time) -> None : Cut all tracks of the Clip. |
| `flush_cache_media(...)` | flush_cache_media ( ( PyClip )arg1 [, (str)mode='current']) -> bool : Flush the Clip's media cache. Keyword argument: mode -- Determine the version's cache to flush. (Current, All Versions, All But Current) |
| `flush_renders(...)` | flush_renders ( ( PyClip )arg1) -> None : Flush the Clip's TimelineFX renders. |
| `get_colour_space(...)` | get_colour_space ( ( PyClip )arg1 [, ( PyTime )time=None]) -> str : Return the colour space at the requested time. Use current_time when no time is supplied. |
| `is_rendered(...)` | is_rendered ( ( PyClip )arg1 [, (bool)top_only=False [, (str)render_quality='Full Resolution']]) -> bool : Return if a Clip is rendered. The following attributes can be defined: top_only, render_quality. |
| `open_as_sequence(...)` | open_as_sequence ( ( PyClip )arg1) -> object : Open the Clip as a Sequence. Mutates the PyClip object into a PySequence object. |
| `open_container(...)` | open_container ( ( PyClip )arg1) -> bool : Open the container timeline if the Clip is inside a container. |
| `reformat(...)` | reformat ( ( PyClip )arg1 [, (int)width=0 [, (int)height=0 [, (float)ratio=0.0 [, (int)bit_depth=0 [, (str)scan_mode='' [, (str)frame_rate='' [, (str)resize_mode='Letterbox']]]]]]]) -> None : Reformat the Clip to the specified format. Keywords arguments: width -- Integer between 24 and 16384. height -- Integer between 24 and 16384. ratio -- Frame aspect ratio. Float between 0.01 and 100. bit_depth -- Bit depth. (8, 10, 12, 16 or 32) scan_mode -- Scan mode of the sequence. (F1, F2, P) frame_rate  |
| `render(...)` | render ( ( PyClip )arg1 [, (str)render_mode='All' [, (str)render_option='Foreground' [, (str)render_quality='Full Resolution' [, (str)effect_type='' [, (str)effect_caching_mode='Current' [, (bool)include_handles=False]]]]]]) -> bool : Trigger a render of the Clip The following attributes can be defined: render_mode, render_option, render_quality, effect_type, effect_caching_mode and include_handles. |
| `save(...)` | save ( ( PyClip )arg1) -> bool : Save the Clip to the defined save destination. |
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PyDesktop`

メソッド数: **8** · [Attributes](./attributes/PyDesktop.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `clear(...)` | clear ( ( PyDesktop )arg1) -> bool : Clear the Desktop. |
| `create_batch_group(...)` | create_batch_group ( ( PyDesktop )arg1, (str)name [, (int)nb_reels=4 [, (int)nb_shelf_reels=1 [, (list)reels=[] [, (list)shelf_reels=[] [, (int)start_frame=1 [, (object)duration=None]]]]]]) -> object : Create a new Batch Group object in the Desktop catalogue. Keyword arguments: name -- Name of the Batch Group. nb_reels -- Number of reels created. *reels* overrides *nb_reels*. nb_shelf_reels -- Number of shelf reels. The first shelf reel created is named Batch Renders. *shelf_reels* ovverides *nb |
| `create_reel_group(...)` | create_reel_group ( ( PyDesktop )arg1, (str)name) -> object : Create a new Reel Group object in the Desktop catalogue. |
| `save(...)` | save ( ( PyDesktop )arg1) -> bool : Save the Desktop to the location defined by the *destination* attribute. |
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PyWorkspace`

メソッド数: **8** · [Attributes](./attributes/PyWorkspace.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `create_library(...)` | create_library ( ( PyWorkspace )arg1, (str)name) -> object : Create a new Library in a Workspace. |
| `replace_desktop(...)` | replace_desktop ( ( PyWorkspace )arg1, ( PyDesktop )desktop) -> bool : Replace the Workspace active Desktop with another one. |
| `set_desktop_reels(...)` | set_desktop_reels ( ( PyWorkspace )arg1 [, (object)group=None]) -> bool : Set the Desktop Reels view mode. |
| `set_freeform(...)` | set_freeform ( ( PyWorkspace )arg1 [, (object)reel=None]) -> bool : Set the Freeform view mode. |
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PyLibrary`

メソッド数: **13** · [Attributes](./attributes/PyLibrary.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `acquire_exclusive_access(...)` | acquire_exclusive_access ( ( PyLibrary )arg1) -> bool : Acquire exclusive access to the Shared Library. Shared Libraries are created locked. Only use with Shared Libraries. |
| `clear(...)` | clear ( ( PyLibrary )arg1 [, (bool)confirm=True]) -> bool : Clear the Library's contents. |
| `close(...)` | close ( ( PyLibrary )arg1) -> bool : Close a Library to release it from the application memory. |
| `create_folder(...)` | create_folder ( ( PyLibrary )arg1, (str)name) -> object : Create a Folder inside a Library. |
| `create_reel(...)` | create_reel ( ( PyLibrary )arg1, (str)name) -> object : Create a Reel inside a Library. |
| `create_reel_group(...)` | create_reel_group ( ( PyLibrary )arg1, (str)name) -> object : Create a Reel Group inside a Library. |
| `create_sequence(...)` | *(説明なし)* |
| `open(...)` | open ( ( PyLibrary )arg1) -> bool : Open a Library and load it in the application memory. Until a Library is open, it cannot be accessed. Libraries are created open. |
| `release_exclusive_access(...)` | release_exclusive_access ( ( PyLibrary )arg1) -> bool : Release exclusive access to the Shared Library. Only used for Shared Libraries. Only use with Shared Libraries. |
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PyFolder`

メソッド数: **9** · [Attributes](./attributes/PyFolder.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `clear(...)` | clear ( ( PyFolder )arg1 [, (bool)confirm=True]) -> bool : Clear the contents of the Folder object. |
| `create_folder(...)` | create_folder ( ( PyFolder )arg1, (str)name) -> object : Create a new Folder object inside the Folder. |
| `create_reel(...)` | create_reel ( ( PyFolder )arg1, (str)name) -> object : Create a new Reel object inside the Folder. |
| `create_reel_group(...)` | create_reel_group ( ( PyFolder )arg1, (str)name) -> object : Create a new Reel Group object inside the Folder. |
| `create_sequence(...)` | *(説明なし)* |
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PyReel`

メソッド数: **7** · [Attributes](./attributes/PyReel.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `clear(...)` | clear ( ( PyReel )arg1 [, (bool)confirm=True]) -> bool : Clear the Reel content. |
| `create_sequence(...)` | *(説明なし)* |
| `save(...)` | save ( ( PyReel )arg1) -> bool : Save the Reel to the defined save destination. |
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PyReelGroup`

メソッド数: **7** · [Attributes](./attributes/PyReelGroup.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `clear(...)` | clear ( ( PyReelGroup )arg1 [, (bool)confirm=True]) -> bool : Clear the Reel Group content. |
| `create_reel(...)` | create_reel ( ( PyReelGroup )arg1, (str)name [, (bool)sequence=False]) -> object : Create a new Reel inside a Reel Group. |
| `save(...)` | save ( ( PyReelGroup )arg1) -> bool : Save the Reel Group to the defined save destination. |
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PyNode`

メソッド数: **6** · [Attributes](./attributes/PyNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |
| `set_context(...)` | clear_schematic_colour ( ( PyNode )arg1) -> None : Clear the schematic colour of the Node. |

### `PySegment`

メソッド数: **25** · [Attributes](./attributes/PySegment.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `change_start_frame(...)` | change_start_frame ( ( PySegment )arg1, (int)start_frame [, (bool)use_segment_connections=True]) -> None : Modify the start frame of the segment. Keywords argument: start_frame -- New start frame of the segment. use_segment_connections -- Sync the start frame of connected segments. |
| `clear_colour(...)` | clear_colour ( ( PySegment )arg1) -> None : Clear the colour of the Segment. |
| `connected_segments(...)` | connected_segments ( ( PySegment )arg1 [, (str)scoping='all reels']) -> object : Return a list of the connected segments. Keywords argument: scoping -- Scopes of the sequences to query (all reels, sequences reels, current reel, current sequence). (Default:all reels) |
| `copy_to_media_panel(...)` | copy_to_media_panel ( ( PySegment )arg1, ( PyArchiveEntry )destination [, (str)duplicate_action='add']) -> object : Create a new clip with a copy of the PyObject. |
| `create_connection(...)` | create_connection ( ( PySegment )arg1) -> None : Create a connected segment connection. |
| `create_effect(...)` | create_effect ( ( PySegment )arg1, (str)effect_type [, (str)after_effect_type='']) -> object : Add an effect of effect_type on the Segment. after_effect_type can be specified to insert the effect at a specific position. |
| `create_marker(...)` | create_marker ( ( PySegment )arg1, (object)location) -> object : Create a Marker at the specified location on the Segment. |
| `create_unlinked_segment(...)` | *(説明なし)* |
| `duplicate_source(...)` | duplicate_source ( ( PySegment )arg1) -> None : Insure that the segment's source is not shared anymore. |
| `get_colour_space(...)` | get_colour_space ( ( PySegment )arg1 [, ( PyTime )time=None]) -> str : Return the colour space at the requested time. Use record_in when no time is supplied. |
| `is_rendered(...)` | is_rendered ( ( PySegment )arg1 [, (str)render_quality='Full Resolution']) -> bool : Return if the segment is rendered. |
| `match(...)` | *(説明なし)* |
| `remove_connection(...)` | remove_connection ( ( PySegment )arg1) -> None : Remove the connected segment connection. |
| `set_gap_bars(...)` | set_gap_bars ( ( PySegment )arg1 [, (str)type='smpte' [, (bool)full_luminance=False [, (float)softness=0.0]]]) -> object : Create colour bars segment for the duration of the gap. Returns a new PySegment on success. Keywords argument: type -- smpte or pal. full_luminance -- bars created at 100 or 75 percent luminance. softness -- softness to apply between the bars. |
| `set_gap_colour(...)` | set_gap_colour ( ( PySegment )arg1 [, (float)r=0.0 [, (float)g=0.0 [, (float)b=0.0]]]) -> None : Create a colour source segment for the duration of the gap, or set the colour of an existing colour source. |
| `set_matte_channel(...)` | set_matte_channel ( ( PySegment )arg1 [, (str)channel_name='' [, (int)channel_index=-1 [, (str)scope='Follow Preferences' [, (str)matte_mode='Custom Matte']]]]) -> bool : Set the Matte channel of the source specified by channel_index or by channel_name if the matte_mode is set to Custom Matte. Keywords argument: channel_name -- Name of the channel found in matte_channels. channel_index -- Index of the channel found in matte_chanels. scope -- Scope of the changes ( Follow Preferences, No Sharing, |
| `set_rgb_channel(...)` | set_rgb_channel ( ( PySegment )arg1 [, (str)channel_name='' [, (int)channel_index=-1 [, (str)scope='Follow Preferences']]]) -> bool : Set the RGB channel of the source specified by channel_index or by channel_name Keywords argument: channel_name -- Name of the channel found in rgb_channels. channel_index -- Index of the channel found in rgb_chanels. scope -- Scope of the changes ( Follow Preferences, No Sharing, Follow Source Sharing, Follow Connected Segments). |
| `shared_source_segments(...)` | shared_source_segments ( ( PySegment )arg1) -> object : Return a list of the segments sharing this segment's source. |
| `slide_keyframes(...)` | slide_keyframes ( ( PySegment )arg1, (int)offset [, (bool)sync=False]) -> bool : Slide the keyframes the PySegment . Keywords argument: offset -- Relative offset to slide the keyframes. sync -- Enable to perform the same operation on the segments that belong to the same sync group as the current PySegment . |
| `slip(...)` | slip ( ( PySegment )arg1, (int)offset [, (bool)sync=False [, (str)keyframes_move_mode='Shift']]) -> bool : Slip the media of the PySegment . Keywords argument: offset -- Relative offset to slip the media. sync -- Enable to perform the same operation on the segments that belong to the same sync group as the current PySegment . keyframes_move_mode -- Select how the animation channels are affected ( Pin, Shift, Prop) |
| `smart_replace(...)` | smart_replace ( ( PySegment )arg1, ( PyClip )source_clip) -> None : Replace the PySegment by the source_clip segment, including the TimelineFX. |
| `smart_replace_media(...)` | smart_replace_media ( ( PySegment )arg1, ( PyClip )source_clip) -> None : Replace the media of PySegment by the source_clip segment, leaving the PySegment TimelineFX untouched |
| `sync_connected_segments(...)` | sync_connected_segments ( ( PySegment )arg1) -> None : Sync connected segments with the Timeline FXs of the current segment. |
| `trim_head(...)` | trim_head ( ( PySegment )arg1, (int)offset [, (bool)ripple=False [, (bool)sync=False [, (str)keyframes_move_mode='Shift']]]) -> bool : Modify the amount of head of the PySegment . Keywords argument: offset -- Number of frames to add or remove from the head. ripple -- Enable to prevent gaps from appearing when performing a trim. sync -- Enable to perform the same operation on the segments that belong to the same sync group as the current PySegment . keyframes_move_mode -- Select how the animation |
| `trim_tail(...)` | trim_tail ( ( PySegment )arg1, (int)offset [, (bool)ripple=False [, (bool)sync=False [, (str)keyframes_move_mode='Shift']]]) -> bool : Modify the amount of tail of the PySegment . Keywords argument: offset -- Number of frames to add or remove from the tail. ripple -- Enable to prevent gaps from appearing when performing a trim. sync -- Enable to perform the same operation on the segments that belong to the same sync group as the current PySegment . keyframes_move_mode -- Select how the animation |

### `PyTrack`

メソッド数: **3** · [Attributes](./attributes/PyTrack.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `copy_to_media_panel(...)` | copy_to_media_panel ( ( PyTrack )arg1, ( PyArchiveEntry )destination [, (str)duplicate_action='add']) -> object : Create a new clip with a copy of the PyObject. |
| `cut(...)` | cut ( ( PyTrack )arg1, ( PyTime )cut_time [, (bool)sync=False]) -> None : Cut the Track. |
| `insert_transition(...)` | insert_transition ( ( PyTrack )arg1, ( PyTime )record_time, (str)type [, (int)duration=10 [, (str)alignment='Centred' [, (int)in_offset=0 [, (bool)sync=False]]]]) -> object : Insert a Transition on the Track. Returns the new PyTransition if successful. Keywords argument: record_time -- Time at which the Transition is inserted. type -- Type of the new Transition. duration -- Duration of the new Transition in frames. alignment -- Alignment of the new Transition. in_offset -- Number of frames on le |

### `PyVersion`

メソッド数: **3** · [Attributes](./attributes/PyVersion.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `copy_to_media_panel(...)` | copy_to_media_panel ( ( PyVersion )arg1, ( PyArchiveEntry )destination [, (str)duplicate_action='add']) -> object : Create a new clip with a copy of the PyObject. |
| `create_track(...)` | create_track ( ( PyVersion )arg1 [, (int)track_index=-1 [, (bool)hdr=False]]) -> object : Add a track to the Version.Keywords arguments: track_index -- Index to insert the new track at, -1 to append at the top. hdr -- Set to True to create an HDR track. |
| `import_DolbyVision_xml(...)` | import_DolbyVision_xml ( ( PyVersion )arg1, (str)file_name [, (str)mode='Include Frame Based Transitions Trims' [, (int)track_index=-1]]) -> object : Add a track to the Version.Keywords arguments: track_index -- Index to insert the new track at, -1 to append at the top. hdr -- Set to True to create an HDR track. |

### `PyTimelineFX`

メソッド数: **5** · [Attributes](./attributes/PyTimelineFX.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `flush_maps_cache_media(...)` | flush_maps_cache_media ( ( PyTimelineFX )arg1) -> bool : Flush the Timeline FX Maps and ML cached media. |
| `load_setup(...)` | load_setup ( ( PyTimelineFX )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_setup(...)` | save_setup ( ( PyTimelineFX )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `slide_keyframes(...)` | slide_keyframes ( ( PyTimelineFX )arg1, (float)offset) -> None : Slide the keyframes the PySegment . Keywords argument: offset -- Relative offset to slide the keyframes. sync -- Enable to perform the same operation on the segments that belong to the same sync group as the current PySegment . |
| `sync_connected_segments(...)` | sync_connected_segments ( ( PyTimelineFX )arg1) -> None : Push the Timeline FX to connected segments. |

### `PyMediaPanel`

メソッド数: **2** · [Attributes](./attributes/PyMediaPanel.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `copy(...)` | copy ( ( PyMediaPanel )arg1, (object)source_entries, (object)destination [, (str)duplicate_action='add']) -> object : Copy a PyObject or a list of PyObjects from the Media Panel to a destination inside the Media Panel.Return a list of the copied PyObjects.Keyword arguments: source_entries -- The PyObject or list of PyObjects to copy. destination -- The PyObject that acts as destination. duplicate_action -- Action to take when finding an object with the same name (add or replace). |
| `move(...)` | move ( ( PyMediaPanel )arg1, (object)source_entries, (object)destination [, (str)duplicate_action='add']) -> object : Move a PyObject or a list of PyObjects from the Media Panel to a destination inside the Media Panel. Return a list of the moved PyObjects. Keyword arguments: source_entries -- The PyObject or list of PyObjects to move. destination -- The PyObject that acts as destination. duplicate_action -- Action to take when finding an object with the same name (add or replace). |

### `PyMessages`

メソッド数: **3** · [Attributes](./attributes/PyMessages.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `clear_console(...)` | clear_console ( ( PyMessages )arg1) -> None : Remove currently displayed message in the message bar. |
| `show_in_console(...)` | show_in_console ( ( PyMessages )arg1, (str)message [, (str)type='info' [, (int)duration=-1]]) -> None : Display an informative message in application message bar. message -- Message string to display. type -- Message type can be info, warning, or error. duration -- An optional time in seconds to keep message on screen. |
| `show_in_dialog(...)` | show_in_dialog ( ( PyMessages )arg1, (str)title, (str)message, (str)type, (list)buttons [, (str)cancel_button='']) -> str : Display a custom dialog with a selection of options. Keywords argument: title -- The title of the dialog. message -- The message displayed in the center of the dialog. type -- The type of dialog. Can be error, info, question, or warning. buttons -- The list of titles used to refer to the options cancel_button -- The text displayed in the cancel option |

### `PyBrowser`

メソッド数: **1** · [Attributes](./attributes/PyBrowser.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `show(...)` | show ( ( PyBrowser )arg1, (str)default_path [, (object)extension='' [, (bool)select_directory=False [, (bool)multi_selection=False [, (object)include_resolution=False [, (str)title='Load']]]]]) -> None : Show the file browser.Keyword arguments: default_path -- Set the path. extension -- Set the extension filter. Can be a single extension or a list of extensions. Leave empty to see all files. select_directory -- Only show directories. multi_selection -- Allow the user to select multiple files. in |

### `PySearch`

メソッド数: **5** · [Attributes](./attributes/PySearch.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `activate_search_result(...)` | activate_search_result ( ( PySearch )arg1, (str)name, (str)type [, (str)tab='Tools']) -> None : Activate a search result. |
| `search_results(...)` | search_results ( ( PySearch )arg1 [, (str)search_str='*' [, (str)tab='Tools']]) -> list : Search results that match a string. |
| `set_tool_favorite(...)` | set_tool_favorite ( ( PySearch )arg1, (str)arg2, (str)name, (bool)type) -> None : Return the favorite status of a tool. |
| `set_tool_hidden(...)` | set_tool_hidden ( ( PySearch )arg1, (str)arg2, (str)name, (bool)type) -> None : Return the hidden status of a tool. |
| `set_tool_weight(...)` | set_tool_weight ( ( PySearch )arg1, (str)arg2, (str)name, (int)type) -> None : Return the tool weight. |

### `PyExporter`

メソッド数: **3** · [Attributes](./attributes/PyExporter.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `export(...)` | *(説明なし)* |
| `get_presets_base_dir(...)` | get_presets_base_dir ( (PresetVisibility)preset_visibility) -> str : Get a presets base directory. |
| `get_presets_dir(...)` | get_presets_dir ( (PresetVisibility)preset_visibility, (PresetType)preset_type) -> str : Get a presets directory. |

### `PyActionNode`

メソッド数: **21** · [Attributes](./attributes/PyActionNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `add_media(...)` | add_media ( ( PyActionFamilyNode )arg1) -> object : Add a Media layer to the Batch Action node. Also instantiates a matching Surface node (and Axis) in the Action node schematic. |
| `disable_output(...)` | disable_output ( ( PyActionFamilyNode )arg1, (str)output_type) -> bool : Disable the render output_type for the Action node. Keyword argument: output_type -- The output to enable. (Comp, Matte, 3D Motion, Albedo, AO, Background, Emissive, GMask, Lens Flare, Motion Vectors, Normals, Object ID, Occluder, Position, Projectors Matte, Reflection, Roughness, Shadow, Specular, UV, Z-Depth HQ, Z-Depth) |
| `enable_output(...)` | enable_output ( ( PyActionFamilyNode )arg1, (str)output_type) -> bool : Enable the render output_type for the Action node. Keyword argument: output_type -- The output to enable. (Comp, Matte, 3D Motion, Albedo, AO, Background, Emissive, GMask, Lens Flare, Motion Vectors, Normals, Object ID, Occluder, Position, Projectoars Matte, Reflection, Roughness, Shadow, Specular, UV, Z-Depth HQ, Z-Depth) |
| `export_fbx(...)` | export_fbx ( ( PyActionFamilyNode )arg1, (str)file_path [, (bool)only_selected_nodes=False [, (float)pixel_to_units=0.10000000149011612 [, (str)frame_rate='23.976 fps' [, (bool)bake_animation=False [, (bool)export_axes=True [, (bool)export_point_locators=False [, (bool)combine_material=True [, (bool)duplicate_material=False]]]]]]]]) -> bool : Export Action nodes to an FBX file. Keyword argument: file_path -- Path to the output FBX file. Mandatory. |
| `import_abc(...)` | import_abc ( ( PyActionFamilyNode )arg1, (str)file_path [, (bool)lights=True [, (bool)cameras=True [, (bool)models=True [, (bool)normals=True [, (bool)mesh_animations=True [, (str)frame_rate='23.976 fps' [, (bool)auto_fit=False [, (float)unit_to_pixels=10.0 [, (bool)consolidate_geometry=True [, (bool)create_object_group=False]]]]]]]]]]) -> list : Import an Alembic (ABC) file into the Action schematic using the Action Objects mode. Keyword argument: file_path -- Path to the ABC file. Mandatory. |
| `import_fbx(...)` | import_fbx ( ( PyActionFamilyNode )arg1, (str)file_path [, (bool)lights=True [, (bool)cameras=True [, (bool)models=True [, (bool)normals=True [, (bool)mesh_animations=True [, (bool)keep_frame_rate=True [, (bool)bake_animation=False [, (bool)object_properties=True [, (bool)auto_fit=False [, (float)unit_to_pixels=10.0 [, (bool)create_media=True [, (bool)is_udim=False [, (bool)relink_material=True [, (str)input_colour_space='']]]]]]]]]]]]]]) -> list : Import an FBX file into the Action schematic us |
| `import_psd(...)` | import_psd ( ( PyActionFamilyNode )arg1, (str)file_path [, (str)input_colour_space='']) -> list : Import a PSD file into the Action schematic. Keyword arguments: file_path -- Path to the PSD file. Mandatory. input_colour_space -- The colour space used as input. Optional. |
| `read_abc(...)` | read_abc ( ( PyActionFamilyNode )arg1, (str)file_path [, (bool)lights=True [, (bool)cameras=True [, (bool)models=True [, (bool)normals=True [, (bool)mesh_animations=True [, (str)frame_rate='23.976 fps' [, (bool)auto_fit=False [, (float)unit_to_pixels=10.0 [, (bool)consolidate_geometry=True [, (bool)create_object_group=False]]]]]]]]]]) -> object : Import an Alembic (ABC) file into the Action schematic using the Read File mode. Keyword argument: file_path -- Path to the ABC file. Mandatory. |
| `read_fbx(...)` | read_fbx ( ( PyActionFamilyNode )arg1, (str)file_path [, (bool)lights=True [, (bool)cameras=True [, (bool)models=True [, (bool)normals=True [, (bool)mesh_animations=True [, (bool)keep_frame_rate=True [, (bool)bake_animation=False [, (bool)object_properties=True [, (bool)auto_fit=False [, (float)unit_to_pixels=10.0 [, (bool)is_udim=False [, (bool)relink_material=True [, (str)input_colour_space='']]]]]]]]]]]]]) -> object : Import an FBX file into the Action schematic using the Read File mode. Keyw |
| `clear_schematic(...)` | clear_schematic ( ( PyActionFamilyNode )arg1) -> bool : Clear the Action/Image/GMaskTracer schematic of all nodes. |
| `connect_nodes(...)` | connect_nodes ( ( PyActionFamilyNode )arg1, ( PyFlameObject )parent_node, ( PyFlameObject )child_node [, (str)link_type='Default']) -> bool : Connect two nodes in the Action/Image/GMaskTracer schematic. Keyword argument: type -- The type of link used to connect the nodes (default, look at, gmask, gmask exclusive, light, light exclusive, mimic) |
| `create_node(...)` | create_node ( ( PyActionFamilyNode )arg1, (str)node_type [, (str)file_path='' [, (bool)is_udim=False [, (int)tile_resolution=0 [, (str)input_colour_space='']]]]) -> object : Add an Action/Image/GMaskTracer object node to the Action/Image/GMaskTracer schematic. Keyword argument: file_path -- Required by nodes that load an asset, such as Matchbox. |
| `disconnect_nodes(...)` | disconnect_nodes ( ( PyActionFamilyNode )arg1, ( PyFlameObject )parent_node, ( PyFlameObject )child_node [, (str)link_type='Default']) -> bool : Disconnect two nodes in the Action/Image/GMaskTracer schematic. Keyword argument: type -- The type of link used to connect the nodes (default, look at, gmask, gmask exclusive, light, light exclusive, mimic) |
| `encompass_nodes(...)` | encompass_nodes ( ( PyActionFamilyNode )arg1, (list)node_list) -> object : Create a compass including the node list given as argument Keyword argument: node_list -- a list of nodes (either string or node objects) output_type -- the created compass node |
| `get_node(...)` | get_node ( ( PyActionFamilyNode )arg1, (str)node_name) -> object : Get a node by node name. Doesn't select it in the UI. |
| `organize(...)` | organize ( ( PyActionFamilyNode )arg1) -> bool : Clean up the Action/Image/GMaskTracer schematic. |
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |

### `PyActionFamilyNode`

メソッド数: **12** · [Attributes](./attributes/PyActionFamilyNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `clear_schematic(...)` | clear_schematic ( ( PyActionFamilyNode )arg1) -> bool : Clear the Action/Image/GMaskTracer schematic of all nodes. |
| `connect_nodes(...)` | connect_nodes ( ( PyActionFamilyNode )arg1, ( PyFlameObject )parent_node, ( PyFlameObject )child_node [, (str)link_type='Default']) -> bool : Connect two nodes in the Action/Image/GMaskTracer schematic. Keyword argument: type -- The type of link used to connect the nodes (default, look at, gmask, gmask exclusive, light, light exclusive, mimic) |
| `create_node(...)` | create_node ( ( PyActionFamilyNode )arg1, (str)node_type [, (str)file_path='' [, (bool)is_udim=False [, (int)tile_resolution=0]]]) -> object : Add an Action/Image/GMaskTracer object node to the Action/Image/GMaskTracer schematic. Keyword argument: file_path -- Required by nodes that load an asset, such as Matchbox. |
| `disconnect_nodes(...)` | disconnect_nodes ( ( PyActionFamilyNode )arg1, ( PyFlameObject )parent_node, ( PyFlameObject )child_node [, (str)link_type='Default']) -> bool : Disconnect two nodes in the Action/Image/GMaskTracer schematic. Keyword argument: type -- The type of link used to connect the nodes (default, look at, gmask, gmask exclusive, light, light exclusive, mimic) |
| `encompass_nodes(...)` | encompass_nodes ( ( PyActionFamilyNode )arg1, (list)node_list) -> object : Create a compass including the node list given as argument Keyword argument: node_list -- a list of nodes (either string or node objects) output_type -- the created compass node |
| `get_node(...)` | get_node ( ( PyActionFamilyNode )arg1, (str)node_name) -> object : Get a node by node name. Doesn't select it in the UI. |
| `organize(...)` | organize ( ( PyActionFamilyNode )arg1) -> bool : Clean up the Action/Image/GMaskTracer schematic. |
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |

### `PyArchiveEntry`

メソッド数: **4** · [Attributes](./attributes/PyArchiveEntry.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PyAttribute`

メソッド数: **2** · [Attributes](./attributes/PyAttribute.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `get_value(...)` | get_value ( ( PyAttribute )arg1) -> object : Get the value of an attribute. |
| `set_value(...)` | set_value ( ( PyAttribute )arg1, (object)arg2) -> bool : Set the value of an attribute. |

### `PyAudioTrack`

メソッド数: **1** · [Attributes](./attributes/PyAudioTrack.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `copy_to_media_panel(...)` | copy_to_media_panel ( ( PyAudioTrack )arg1, ( PyArchiveEntry )destination [, (str)duplicate_action='add']) -> object : Create a new clip with a copy of the PyObject. |

### `PyBatchIteration`

メソッド数: **5** · [Attributes](./attributes/PyBatchIteration.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `open_as_batch_group(...)` | open_as_batch_group ( ( PyBatchIteration )arg1 [, (bool)confirm=True]) -> bool : Open a Batch Iteration as a new Batch Group, adding it to PyDesktop .batch_groups. Can only be called from a Library. |
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PyClipNode`

メソッド数: **5** · [Attributes](./attributes/PyClipNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |

### `PyCoCameraAnalysis`

メソッド数: **7** · [Attributes](./attributes/PyCoCameraAnalysis.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `analyseRange(...)` | analyseRange ( ( PyCoCameraAnalysis )arg1, (object)arg2, (object)start) -> bool : Run the analysis for the given frame range using the first frame as a reference if none has been already set. |
| `resetAnalysis(...)` | resetAnalysis ( ( PyCoCameraAnalysis )arg1) -> bool : Reset the current analysis. |
| `add_reference(...)` | add_reference ( ( PyCoNode )arg1, (object)frame) -> bool : Add a Motion Warp map's reference frame at specified index. Keyword argument frame -- The reference frame's index. An integer. |
| `assign_media(...)` | assign_media ( ( PyCoNode )arg1, (object)media_name) -> bool : Assign a media layer to the node. Keyword argument media_name -- The index of the media layer from Actions' *media_layers*; or the name of the media layer. |
| `cache_range(...)` | cache_range ( ( PyCoNode )arg1, (object)arg2, (object)start) -> bool : Cache the selected Map Analysis over the specified range. Keyword arguments start -- The first frame of the range. An integer. end -- The last frame of the range. An integer. |
| `children(...)` | children ( ( PyCoNode )arg1 [, (str)link_type='Default']) -> list : Return a list of PyCoNode objects that are the children of the action node. Keyword argument: link_type -- The type of link used to connect the nodes (default, look at, gmask, gmask exclusive, light, light exclusive, mimic) |
| `parents(...)` | parents ( ( PyCoNode )arg1 [, (str)link_type='Default']) -> list : Return a list of PyCoNode objects that are the parents of the action node. Keyword argument: link_type -- The type of link used to connect the nodes (default, look at, gmask, gmask exclusive, light, light exclusive, mimic) |

### `PyCoCompass`

メソッド数: **5** · [Attributes](./attributes/PyCoCompass.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `add_reference(...)` | add_reference ( ( PyCoNode )arg1, (object)frame) -> bool : Add a Motion Warp map's reference frame at specified index. Keyword argument frame -- The reference frame's index. An integer. |
| `assign_media(...)` | assign_media ( ( PyCoNode )arg1, (object)media_name) -> bool : Assign a media layer to the node. Keyword argument media_name -- The index of the media layer from Actions' *media_layers*; or the name of the media layer. |
| `cache_range(...)` | cache_range ( ( PyCoNode )arg1, (object)arg2, (object)start) -> bool : Cache the selected Map Analysis over the specified range. Keyword arguments start -- The first frame of the range. An integer. end -- The last frame of the range. An integer. |
| `children(...)` | children ( ( PyCoNode )arg1 [, (str)link_type='Default']) -> list : Return a list of PyCoNode objects that are the children of the action node. Keyword argument: link_type -- The type of link used to connect the nodes (default, look at, gmask, gmask exclusive, light, light exclusive, mimic) |
| `parents(...)` | parents ( ( PyCoNode )arg1 [, (str)link_type='Default']) -> list : Return a list of PyCoNode objects that are the parents of the action node. Keyword argument: link_type -- The type of link used to connect the nodes (default, look at, gmask, gmask exclusive, light, light exclusive, mimic) |

### `PyCompassNode`

メソッド数: **5** · [Attributes](./attributes/PyCompassNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |

### `PyCoNode`

メソッド数: **5** · [Attributes](./attributes/PyCoNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `add_reference(...)` | add_reference ( ( PyCoNode )arg1, (object)frame) -> bool : Add a Motion Warp map's reference frame at specified index. Keyword argument frame -- The reference frame's index. An integer. |
| `assign_media(...)` | assign_media ( ( PyCoNode )arg1, (object)media_name) -> bool : Assign a media layer to the node. Keyword argument media_name -- The index of the media layer from Actions' *media_layers*; or the name of the media layer. |
| `cache_range(...)` | cache_range ( ( PyCoNode )arg1, (object)arg2, (object)start) -> bool : Cache the selected Map Analysis over the specified range. Keyword arguments start -- The first frame of the range. An integer. end -- The last frame of the range. An integer. |
| `children(...)` | children ( ( PyCoNode )arg1 [, (str)link_type='Default']) -> list : Return a list of PyCoNode objects that are the children of the action node. Keyword argument: link_type -- The type of link used to connect the nodes (default, look at, gmask, gmask exclusive, light, light exclusive, mimic) |
| `parents(...)` | parents ( ( PyCoNode )arg1 [, (str)link_type='Default']) -> list : Return a list of PyCoNode objects that are the parents of the action node. Keyword argument: link_type -- The type of link used to connect the nodes (default, look at, gmask, gmask exclusive, light, light exclusive, mimic) |

### `PyGMaskTracerNode`

メソッド数: **19** · [Attributes](./attributes/PyGMaskTracerNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `disable_output(...)` | disable_output ( ( PyActionFamilyNode )arg1, (str)output_type) -> bool : Disable the render output_type for the GMask Tracer node. Keyword argument: output_type -- The output to enable. (Comp, Matte, 3D Motion, Albedo, AO, Background, Emissive, GMask, Lens Flare, Motion Vectors, Normals, Object ID, Occluder, Position, Projectors Matte, Reflection, Roughness, Shadow, Specular, UV, Z-Depth HQ, Z-Depth) |
| `enable_output(...)` | enable_output ( ( PyActionFamilyNode )arg1, (str)output_type) -> bool : Enable the render output_type for the GMask Tracer node. Keyword argument: output_type -- The output to enable. (Comp, Matte, 3D Motion, Albedo, AO, Background, Emissive, GMask, Lens Flare, Motion Vectors, Normals, Object ID, Occluder, Position, Projectoars Matte, Reflection, Roughness, Shadow, Specular, UV, Z-Depth HQ, Z-Depth) |
| `export_fbx(...)` | export_fbx ( ( PyActionFamilyNode )arg1, (str)file_path [, (bool)only_selected_nodes=False [, (float)pixel_to_units=0.10000000149011612 [, (str)frame_rate='23.976 fps' [, (bool)bake_animation=False [, (bool)export_axes=True [, (bool)export_point_locators=False [, (bool)combine_material=True [, (bool)duplicate_material=False]]]]]]]]) -> bool : Export GMask Tracer nodes to an FBX file. Keyword argument: file_path -- Path to the output FBX file. Mandatory. |
| `import_abc(...)` | import_abc ( ( PyActionFamilyNode )arg1, (str)file_path [, (bool)lights=True [, (bool)cameras=True [, (bool)models=True [, (bool)normals=True [, (bool)mesh_animations=True [, (str)frame_rate='23.976 fps' [, (bool)auto_fit=False [, (float)unit_to_pixels=10.0 [, (bool)consolidate_geometry=True [, (bool)create_object_group=False]]]]]]]]]]) -> list : Import an Alembic (ABC) file into the GMask Tracer schematic using the GMask Tracer Objects mode. Keyword argument: file_path -- Path to the ABC file.  |
| `import_fbx(...)` | import_fbx ( ( PyActionFamilyNode )arg1, (str)file_path [, (bool)lights=True [, (bool)cameras=True [, (bool)models=True [, (bool)normals=True [, (bool)mesh_animations=True [, (bool)keep_frame_rate=True [, (bool)bake_animation=False [, (bool)object_properties=True [, (bool)auto_fit=False [, (float)unit_to_pixels=10.0 [, (bool)create_media=True [, (bool)is_udim=False [, (bool)relink_material=True]]]]]]]]]]]]]) -> list : Import an FBX file into the GMask Tracer schematic using the GMask Tracer Obje |
| `read_abc(...)` | read_abc ( ( PyActionFamilyNode )arg1, (str)file_path [, (bool)lights=True [, (bool)cameras=True [, (bool)models=True [, (bool)normals=True [, (bool)mesh_animations=True [, (str)frame_rate='23.976 fps' [, (bool)auto_fit=False [, (float)unit_to_pixels=10.0 [, (bool)consolidate_geometry=True [, (bool)create_object_group=False]]]]]]]]]]) -> object : Import an Alembic (ABC) file into the GMask Tracer schematic using the Read File mode. Keyword argument: file_path -- Path to the ABC file. Mandatory. |
| `read_fbx(...)` | read_fbx ( ( PyActionFamilyNode )arg1, (str)file_path [, (bool)lights=True [, (bool)cameras=True [, (bool)models=True [, (bool)normals=True [, (bool)mesh_animations=True [, (bool)keep_frame_rate=True [, (bool)bake_animation=False [, (bool)object_properties=True [, (bool)auto_fit=False [, (float)unit_to_pixels=10.0 [, (bool)is_udim=False [, (bool)relink_material=True]]]]]]]]]]]]) -> object : Import an FBX file into the GMask Tracer schematic using the Read File mode. Keyword argument: file_path - |
| `clear_schematic(...)` | clear_schematic ( ( PyActionFamilyNode )arg1) -> bool : Clear the Action/Image/GMaskTracer schematic of all nodes. |
| `connect_nodes(...)` | connect_nodes ( ( PyActionFamilyNode )arg1, ( PyFlameObject )parent_node, ( PyFlameObject )child_node [, (str)link_type='Default']) -> bool : Connect two nodes in the Action/Image/GMaskTracer schematic. Keyword argument: type -- The type of link used to connect the nodes (default, look at, gmask, gmask exclusive, light, light exclusive, mimic) |
| `create_node(...)` | create_node ( ( PyActionFamilyNode )arg1, (str)node_type [, (str)file_path='' [, (bool)is_udim=False [, (int)tile_resolution=0]]]) -> object : Add an Action/Image/GMaskTracer object node to the Action/Image/GMaskTracer schematic. Keyword argument: file_path -- Required by nodes that load an asset, such as Matchbox. |
| `disconnect_nodes(...)` | disconnect_nodes ( ( PyActionFamilyNode )arg1, ( PyFlameObject )parent_node, ( PyFlameObject )child_node [, (str)link_type='Default']) -> bool : Disconnect two nodes in the Action/Image/GMaskTracer schematic. Keyword argument: type -- The type of link used to connect the nodes (default, look at, gmask, gmask exclusive, light, light exclusive, mimic) |
| `encompass_nodes(...)` | encompass_nodes ( ( PyActionFamilyNode )arg1, (list)node_list) -> object : Create a compass including the node list given as argument Keyword argument: node_list -- a list of nodes (either string or node objects) output_type -- the created compass node |
| `get_node(...)` | get_node ( ( PyActionFamilyNode )arg1, (str)node_name) -> object : Get a node by node name. Doesn't select it in the UI. |
| `organize(...)` | organize ( ( PyActionFamilyNode )arg1) -> bool : Clean up the Action/Image/GMaskTracer schematic. |
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |

### `PyHDRNode`

メソッド数: **14** · [Attributes](./attributes/PyHDRNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `analyze(...)` | analyze ( ( PyHDRNode )arg1 [, (str)analyze_mode='Current Shot']) -> None : Perform HDR analysis. |
| `export_DolbyVision_xml(...)` | export_DolbyVision_xml ( ( PyHDRNode )arg1, (str)file_name [, (str)comment='']) -> None : Export the current HDR to a Dolby Vision XML file. |
| `has_trim(...)` | has_trim ( ( PyHDRNode )arg1, (int)target_display_id) -> bool : Returns True if the given Target Display ID has trims. |
| `import_DolbyVision_xml(...)` | import_DolbyVision_xml ( ( PyHDRNode )arg1, (str)file_name [, (str)mode='Include Frame Based Transitions Trims' [, (int)shot_idx=0]]) -> None : Import the current HDR from a Dolby Vision XML file. |
| `interpolate_trims(...)` | interpolate_trims ( ( PyHDRNode )arg1) -> None : Interpolate the current HDR trims. |
| `keep_analysis(...)` | keep_analysis ( ( PyHDRNode )arg1) -> None : Remove the dirty flag from the HDR analysis. |
| `l2_from_l8(...)` | l2_from_l8 ( ( PyHDRNode )arg1) -> object : Dictionary containing the L2 values based on L8 values. Not valid in Dolby Vision 2.9. |
| `reset_analysis(...)` | reset_analysis ( ( PyHDRNode )arg1) -> None : Reset the current HDR analysis. |
| `reset_trims(...)` | reset_trims ( ( PyHDRNode )arg1) -> None : Reset the current HDR trims. |
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |

### `PyHDRTimelineFX`

メソッド数: **14** · [Attributes](./attributes/PyHDRTimelineFX.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `analyze(...)` | analyze ( ( PyHDRTimelineFX )arg1 [, (str)analyze_mode='Current Shot']) -> None : Perform HDR analysis. |
| `export_DolbyVision_xml(...)` | export_DolbyVision_xml ( ( PyHDRTimelineFX )arg1, (str)file_name [, (bool)shot_only=False [, (str)comment='']]) -> None : Export the current HDR to a Dolby Vision XML file. |
| `has_trim(...)` | has_trim ( ( PyHDRTimelineFX )arg1, (int)target_display_id) -> bool : Returns True if the given Target Display ID has trims. |
| `import_DolbyVision_xml(...)` | import_DolbyVision_xml ( ( PyHDRTimelineFX )arg1, (str)file_name [, (str)mode='Include Frame Based Transitions Trims' [, (int)shot_idx=0]]) -> None : Import the current HDR from a Dolby Vision XML file. |
| `interpolate_trims(...)` | interpolate_trims ( ( PyHDRTimelineFX )arg1, (str)arg2) -> None : Interpolate the current HDR trims. |
| `keep_analysis(...)` | keep_analysis ( ( PyHDRTimelineFX )arg1) -> None : Remove the dirty flag from the HDR analysis. |
| `l2_from_l8(...)` | l2_from_l8 ( ( PyHDRTimelineFX )arg1) -> object : Dictionary containing the L2 values based on L8 values. Not valid in Dolby Vision 2.9. |
| `reset_analysis(...)` | reset_analysis ( ( PyHDRTimelineFX )arg1) -> None : Reset the current HDR analysis. |
| `reset_trims(...)` | reset_trims ( ( PyHDRTimelineFX )arg1) -> None : Reset the current HDR trims. |
| `flush_maps_cache_media(...)` | flush_maps_cache_media ( ( PyTimelineFX )arg1) -> bool : Flush the Timeline FX Maps and ML cached media. |
| `load_setup(...)` | load_setup ( ( PyTimelineFX )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_setup(...)` | save_setup ( ( PyTimelineFX )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `slide_keyframes(...)` | slide_keyframes ( ( PyTimelineFX )arg1, (float)offset) -> None : Slide the keyframes the PySegment . Keywords argument: offset -- Relative offset to slide the keyframes. sync -- Enable to perform the same operation on the segments that belong to the same sync group as the current PySegment . |
| `sync_connected_segments(...)` | sync_connected_segments ( ( PyTimelineFX )arg1) -> None : Push the Timeline FX to connected segments. |

### `PyImageNode`

メソッド数: **13** · [Attributes](./attributes/PyImageNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `add_media(...)` | add_media ( ( PyActionFamilyNode )arg1) -> object : Add a Media layer to the Batch Image node. |
| `clear_schematic(...)` | clear_schematic ( ( PyActionFamilyNode )arg1) -> bool : Clear the Action/Image/GMaskTracer schematic of all nodes. |
| `connect_nodes(...)` | connect_nodes ( ( PyActionFamilyNode )arg1, ( PyFlameObject )parent_node, ( PyFlameObject )child_node [, (str)link_type='Default']) -> bool : Connect two nodes in the Action/Image/GMaskTracer schematic. Keyword argument: type -- The type of link used to connect the nodes (default, look at, gmask, gmask exclusive, light, light exclusive, mimic) |
| `create_node(...)` | create_node ( ( PyActionFamilyNode )arg1, (str)node_type [, (str)file_path='' [, (bool)is_udim=False [, (int)tile_resolution=0]]]) -> object : Add an Action/Image/GMaskTracer object node to the Action/Image/GMaskTracer schematic. Keyword argument: file_path -- Required by nodes that load an asset, such as Matchbox. |
| `disconnect_nodes(...)` | disconnect_nodes ( ( PyActionFamilyNode )arg1, ( PyFlameObject )parent_node, ( PyFlameObject )child_node [, (str)link_type='Default']) -> bool : Disconnect two nodes in the Action/Image/GMaskTracer schematic. Keyword argument: type -- The type of link used to connect the nodes (default, look at, gmask, gmask exclusive, light, light exclusive, mimic) |
| `encompass_nodes(...)` | encompass_nodes ( ( PyActionFamilyNode )arg1, (list)node_list) -> object : Create a compass including the node list given as argument Keyword argument: node_list -- a list of nodes (either string or node objects) output_type -- the created compass node |
| `get_node(...)` | get_node ( ( PyActionFamilyNode )arg1, (str)node_name) -> object : Get a node by node name. Doesn't select it in the UI. |
| `organize(...)` | organize ( ( PyActionFamilyNode )arg1) -> bool : Clean up the Action/Image/GMaskTracer schematic. |
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |

### `PyInferenceNode`

メソッド数: **5** · [Attributes](./attributes/PyInferenceNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |

### `PyLensDistortionNode`

メソッド数: **6** · [Attributes](./attributes/PyLensDistortionNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `import_lens_distortion(...)` | import_lens_distortion ( ( PyLensDistortionNode (str)filename) -> None : Import a Lens Distortion file. |
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |

### `PyMediaHubFilesEntry`

メソッド数: **4** · [Attributes](./attributes/PyMediaHubFilesEntry.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PyMediaHubFilesFolder`

メソッド数: **4** · [Attributes](./attributes/PyMediaHubFilesFolder.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PyMediaHubFilesTab`

メソッド数: **2** · [Attributes](./attributes/PyMediaHubFilesTab.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `get_path(...)` | get_path ( ( PyMediaHubTab )arg1) -> str : Return the MediaHub tab current path. |
| `set_path(...)` | set_path ( ( PyMediaHubTab )arg1, (str)arg2 [, (bool)allow_partial_success=False]) -> bool : Set the MediaHub tab current path. If allow_partial_success is True, the path will be set to the last valid folder in the path. |

### `PyMediaHubFilesTabOptions`

メソッド数: **1** · [Attributes](./attributes/PyMediaHubFilesTabOptions.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `set_tagged_colour_space(...)` | set_tagged_colour_space ( ( PyMediaHubFilesTabOptions )arg1, (str)colour_space) -> None : Import pixel ratio value. Returns None when resolution is not set to Same As Source. |

### `PyMediaHubProjectsEntry`

メソッド数: **4** · [Attributes](./attributes/PyMediaHubProjectsEntry.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PyMediaHubProjectsFolder`

メソッド数: **4** · [Attributes](./attributes/PyMediaHubProjectsFolder.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `clear_colour(...)` | clear_colour ( ( PyArchiveEntry )arg1) -> None : Clear the colour of an object in the Media Panel. |
| `commit(...)` | commit ( ( PyArchiveEntry )arg1) -> None : Commit to disk the Media Panel object or its closest container possible. |
| `get_wiretap_node_id(...)` | get_wiretap_node_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap Node ID of the Flame object, but only if the object is in the Media Panel. |
| `get_wiretap_storage_id(...)` | get_wiretap_storage_id ( ( PyArchiveEntry )arg1) -> str : Return the Wiretap server's storage ID for the Flame object, but only if the object is in the Media Panel. |

### `PyMediaHubTab`

メソッド数: **2** · [Attributes](./attributes/PyMediaHubTab.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `get_path(...)` | get_path ( ( PyMediaHubTab )arg1) -> str : Return the MediaHub tab current path. |
| `set_path(...)` | set_path ( ( PyMediaHubTab )arg1, (str)arg2 [, (bool)allow_partial_success=False]) -> bool : Set the MediaHub tab current path. If allow_partial_success is True, the path will be set to the last valid folder in the path. |

### `PyMorphNode`

メソッド数: **6** · [Attributes](./attributes/PyMorphNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `set_mix_to_range(...)` | set_mix_to_range ( ( PyMorphNode )arg1) -> None : Move the first and last keyframes of the mix curve to the range's first and last frame. |
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |

### `PyOFXNode`

メソッド数: **6** · [Attributes](./attributes/PyOFXNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `change_plugin(...)` | change_plugin ( ( PyOFXNode )arg1, (str)plugin_name) -> bool : Change the active plugin for the openFX node |
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |

### `PyPaintNode`

メソッド数: **6** · [Attributes](./attributes/PyPaintNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `add_source(...)` | add_source ( ( PyPaintNode )arg1) -> object : Add a Source layer to a Paint node. |
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |

### `PyRenderNode`

メソッド数: **6** · [Attributes](./attributes/PyRenderNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `set_channel_name(...)` | set_channel_name ( ( PyRenderNode )arg1, (object)channel, (object)name) -> None : Rename a channel, using its index or front channel name as the index key. Keyword arguments: channel -- The channel to rename. Can be the channel index or the current name of the channel's front socket. name -- The new name of the channel. The type is either a string or a tuple. A Write File node always takes a string. A Render node takes a string or a tuple. In a Render node, a string only sets the name of the cha |
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |

### `PySequenceGroup`

メソッド数: **2** · [Attributes](./attributes/PySequenceGroup.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `add(...)` | add ( ( PySequenceGroup )arg1, (object)segments) -> None : Adds a PySegment or list of PySegments to the Group. |
| `remove(...)` | remove ( ( PySequenceGroup )arg1, (object)segments) -> None : Remove a PySegment or list of PySegments from the Group. |

### `PySubtitleTrack`

メソッド数: **5** · [Attributes](./attributes/PySubtitleTrack.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `export_as_avid_txt_file(...)` | export_as_avid_txt_file ( ( PySubtitleTrack )arg1, (str)file_name [, (str)start_timecode='Same as Clip']) -> None : Export the Subtitle Track as a Avid Caption (txt) file.Keyword arguments: file_name -- The path and name of the file to write. start_timecode -- Specify the timecode mode, Same As Clip or, Relative to Clip Start. |
| `export_as_srt_file(...)` | *(説明なし)* |
| `copy_to_media_panel(...)` | copy_to_media_panel ( ( PyTrack )arg1, ( PyArchiveEntry )destination [, (str)duplicate_action='add']) -> object : Create a new clip with a copy of the PyObject. |
| `cut(...)` | cut ( ( PyTrack )arg1, ( PyTime )cut_time [, (bool)sync=False]) -> None : Cut the Track. |
| `insert_transition(...)` | insert_transition ( ( PyTrack )arg1, ( PyTime )record_time, (str)type [, (int)duration=10 [, (str)alignment='Centred' [, (int)in_offset=0 [, (bool)sync=False]]]]) -> object : Insert a Transition on the Track. Returns the new PyTransition if successful. Keywords argument: record_time -- Time at which the Transition is inserted. type -- Type of the new Transition. duration -- Duration of the new Transition in frames. alignment -- Alignment of the new Transition. in_offset -- Number of frames on le |

### `PyTransition`

メソッド数: **4** · [Attributes](./attributes/PyTransition.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `set_dissolve_to_from_colour(...)` | set_dissolve_to_from_colour ( ( PyTransition )arg1 [, (float)r=0.0 [, (float)g=0.0 [, (float)b=0.0]]]) -> None : Make a dissolve transition dissolve to/from a colour. |
| `set_fade_to_from_silence(...)` | set_fade_to_from_silence ( ( PyTransition )arg1) -> None : Make a fade dip to/from silence. |
| `set_transition(...)` | set_transition ( ( PyTransition )arg1, (str)type [, (int)duration=10 [, (str)alignment='Centred' [, (int)in_offset=0]]]) -> object : Replace the Transition with another type of Transition. Returns the new PyTransition if successful. Keywords argument: type -- Type of the new Transition. duration -- Duration of the new Transition in frames. alignment -- Alignment of the new Transition. in_offset -- Number of frames on left side of the cut in custom alignment. |
| `slide(...)` | slide ( ( PyTransition )arg1, (int)offset [, (bool)sync=False]) -> bool : Slide the Transition. Keywords argument: offset -- Amount of frames to slide the Transition with. sync -- Enable to perform the same operation on transitions that belong to the same sync group as the current PyTransition . |

### `PyWriteFileNode`

メソッド数: **7** · [Attributes](./attributes/PyWriteFileNode.md)

| メソッド | 説明（Help 抜粋） |
|----------|-------------------|
| `get_resolved_media_path(...)` | get_resolved_media_path ( ( PyWriteFileNode )arg1 [, (bool)show_extension=True [, (bool)translate_path=True [, (object)frame=None]]]) -> object : Return the resolved media path. Keyword arguments: show_extension -- Set True to display the extension. translate_path -- Set True to apply the Media Location Path Translation. frame -- Pass a frame number, between range_start and range_end, to get the path for that frame. |
| `set_channel_name(...)` | set_channel_name ( ( PyRenderNode )arg1, (object)channel, (object)name) -> None : Rename a channel, using its index or front channel name as the index key. Keyword arguments: channel -- The channel to rename. Can be the channel index or the current name of the channel's front socket. name -- The new name of the channel. The type is either a string or a tuple. A Write File node always takes a string. A Render node takes a string or a tuple. In a Render node, a string only sets the name of the cha |
| `delete(...)` | delete ( ( PyFlameObject )arg1 [, (bool)confirm=True]) -> bool : Delete the node. |
| `duplicate(...)` | duplicate ( ( PyNode )arg1 [, (bool)keep_node_connections=False]) -> object : Duplicate the node. |
| `load_node_setup(...)` | load_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Load a Node setup. A path and a file name must be defined as arguments. |
| `save_node_setup(...)` | save_node_setup ( ( PyNode )arg1, (str)file_name) -> bool : Save a Node setup. A path and a file name must be defined as arguments. |
| `set_context(...)` | set_context ( ( PyNode )arg1, (int)index [, (str)socket_name='Default']) -> bool : Set a Context view on a Node socket. An index and a socket name must be defined as arguments. |

