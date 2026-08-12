# PyMarker Attributes

公式 Help の Attributes ページを原文寄りに整理したもの。

| 項目 | 内容 |
|------|------|
| 一次情報 | `docs/API Documentation/Attributes/PyMarker Attributes/` |
| 関連 | [flame-module.md](../flame-module.md)（メソッド索引） |

---

### `name`

- **Type:** `str`
- **Description:** The Marker's name

### `comment`

- **Type:** `str`
- **Description:** The Marker's comment

### `location`

- **Type:** `flame.PyTime`
- **Description:** The Marker's location

### `locked_location`

- **Type:** `bool`
- **Description:** Lock the Marker location.
- **Value range:** True · False

### `duration`

- **Type:** `flame.PyTime`
- **Description:** The Marker's duration

### `colour`

- **Type:** `tuple`
- **Description:** The Marker's colour
- **Value range:** (0.0, 0.0, 0.0) · (1.0, 1.0, 1.0)

### `colour_label`

- **Type:** `str`
- **Description:** The Marker's colour label.
- **Value range:** None

### `selected`

- **Type:** `bool`
- **Description:** Select a Marker on the Clip or Segment.
- **Value range:** True False Parent page: Autodesk Flame Python: flame module

###
