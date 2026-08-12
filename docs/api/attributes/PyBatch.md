# PyBatch Attributes

公式 Help の Attributes ページを原文寄りに整理したもの。

| 項目 | 内容 |
|------|------|
| 一次情報 | `docs/API Documentation/Attributes/PyBatch Attributes/` |
| 関連 | [flame-module.md](../flame-module.md)（メソッド索引） |

---

### `name`

- **Type:** `str`
- **Description:** The name of an object in the Media Panel, resolving tokens if any are present.

### `uid`

- **Type:** `str`
- **Description:** The unique identifier of an object in the Media Panel.

### `token_name`

- **Type:** `str`
- **Description:** The tokenized name of an object in the Media Panel.

### `expanded`

- **Type:** `bool`
- **Description:** The expanded state of an object in the Media Panel. If you're expanding/collapsing a Shared Library, you must have exclusive access if you want this property to be persisted.
- **Value range:** True · False

### `colour`

- **Type:** `tuple`
- **Description:** The colour of an object in the Media Panel.
- **Value range:** (0.0, 0.0, 0.0) · (1.0, 1.0, 1.0)

### `colour_label`

- **Type:** `str`
- **Description:** The colour label of an object in the Media Panel.

### `selected`

- **Type:** `bool`
- **Description:** The PyArchiveEntry is selected in the Media Panel.
- **Value range:** True · False

### `selected_nodes`

- **Type:** `list`
- **Description:** The list of Batch object nodes that are currently selected in the Batch schematic.

### `current_node`

- **Type:** `flame.PyActionNode`
- **Description:** Return the Batch node currently selected in the Batch schematic. Use current_node to capture the node selected by the user. In the case of a multi-selection, return the primary selection (yellow ring).

### `duration`

- **Type:** `int`
- **Description:** The duration of Batch Group.

### `start_frame`

- **Type:** `int`
- **Description:** The start frame of the Batch Group.

### `auto_key`

- **Type:** `bool`
- **Description:** The Auto Key status of the Batch Group.

### `current_frame`

- **Type:** `int`
- **Description:** The current frame of the Batch Group.

### `tags`

- **Type:** `list`
- **Description:** The tag list of an object in the Media Panel. Parent page: Autodesk Flame Python: flame module

###
