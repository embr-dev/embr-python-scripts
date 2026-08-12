# PyCoCompass Attributes

公式 Help の Attributes ページを原文寄りに整理したもの。

| 項目 | 内容 |
|------|------|
| 一次情報 | `docs/API Documentation/Attributes/PyCoCompass Attributes/` |
| 関連 | [flame-module.md](../flame-module.md)（メソッド索引） |

---

### `name`

- **Type:** `str`
- **Description:** The name of the Action node in the Action schematic.
- **Value range:** None

### `position`

- **Type:** `tuple`
- **Description:** The XYZ position of the Action node in the Action 3D space.
- **Value range:** (-3.4028234663852886e+38, -3.4028234663852886e+38, -3.4028234663852886e+38) (3.4028234663852886e+38, 3.4028234663852886e+38, 3.4028234663852886e+38)

### `selected`

- **Type:** `bool`
- **Description:** The Action node is selected.
- **Value range:** True · False

### `collapsed_in_manager`

- **Type:** `bool`
- **Description:** The Action node is collapsed in the Action Manager
- **Value range:** True · False

### `colour`

- **Type:** `tuple`
- **Description:** The Colour attribute of the Compass node.
- **Value range:** (0.0, 0.0, 0.0) · (1.0, 1.0, 1.0)

### `width`

- **Type:** `int`
- **Description:** The Width attribute of the Compass node.
- **Value range:** Min: 1.0 · Max: 10000.0

### `height`

- **Type:** `int`
- **Description:** The Height attribute of the Compass node.
- **Value range:** Min: 1.0 Max: 10000.0 Parent page: Autodesk Flame Python: flame module

###
