# PySegment Attributes

公式 Help の Attributes ページを原文寄りに整理したもの。

| 項目 | 内容 |
|------|------|
| 一次情報 | `docs/API Documentation/Attributes/PySegment Attributes/` |
| 関連 | [flame-module.md](../flame-module.md)（メソッド索引） |

---

### `name`

- **Type:** `str`
- **Description:** The name of the Segment.

### `shot_name`

- **Type:** `str`
- **Description:** Return the shot name of the Segment.

### `comment`

- **Type:** `str`
- **Description:** Return the comment of the Segment.

### `hidden`

- **Type:** `bool`
- **Description:** The hidden status of the Segment.
- **Value range:** True · False

### `colour`

- **Type:** `tuple`
- **Description:** The colour of the Segment.
- **Value range:** (0.0, 0.0, 0.0) · (1.0, 1.0, 1.0)

### `colour_label`

- **Type:** `str`
- **Description:** The colour label of the Segment.
- **Value range:** None

### `selected`

- **Type:** `bool`
- **Description:** Select a segment on the Clip.
- **Value range:** True · False

### `selected_markers`

- **Type:** `list`
- **Description:** Return a list of PyMarker currently selected.

### `tags`

- **Type:** `list`
- **Description:** The tag list of the Segment.
- **Value range:** None Parent page: Autodesk Flame Python: flame module

###
