# PyActionNode Attributes

公式 Help の Attributes ページを原文寄りに整理したもの。

| 項目 | 内容 |
|------|------|
| 一次情報 | `docs/API Documentation/Attributes/PyActionNode Attributes/` |
| 関連 | [flame-module.md](../flame-module.md)（メソッド索引） |

---

### `pos_x`

- **Type:** `int`
- **Description:** The x position of a node in the Batch schematic.
- **Value range:** Min: -2147483647 · Max: 2147483647

### `pos_y`

- **Type:** `int`
- **Description:** The y position of a node in the Batch schematic.
- **Value range:** Min: -2147483647 · Max: 2147483647

### `name`

- **Type:** `str`
- **Description:** The name of the node in the Batch schematic.

### `collapsed`

- **Type:** `bool`
- **Description:** The collapsed status of a node in the Batch schematic.
- **Value range:** True · False

### `note`

- **Type:** `str`
- **Description:** The Node's note.

### `note_collapsed`

- **Type:** `bool`
- **Description:** The collapsed status of a note in the Batch schematic.
- **Value range:** True · False

### `selected`

- **Type:** `bool`
- **Description:** Select a Node in the Batch schematic.
- **Value range:** True · False

### `type`

- **Type:** `str`
- **Description:** Return the type of the node.

### `selected_nodes`

- **Type:** `list`
- **Description:** The list of Action object nodes that are currently selected in the Action schematic.

### `current_node`

- **Type:** `flame.PyCoNode`
- **Description:** Return the currently selected action object node in the Action schematic. Parent page: Autodesk Flame Python: flame module

###
