# PyReel Attributes

公式 Help の Attributes ページを原文寄りに整理したもの。

| 項目 | 内容 |
|------|------|
| 一次情報 | `docs/API Documentation/Attributes/PyReel Attributes/` |
| 関連 | [flame-module.md](../flame-module.md)（メソッド索引） |

---

### `name`

- **Type:** `str`
- **Description:** The name of an object in the Media Panel, resolving tokens if any are present.
- **Value range:** None

### `uid`

- **Type:** `str`
- **Description:** The unique identifier of an object in the Media Panel.
- **Value range:** None

### `token_name`

- **Type:** `str`
- **Description:** The tokenized name of an object in the Media Panel.
- **Value range:** None

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
- **Value range:** None

### `selected`

- **Type:** `bool`
- **Description:** The PyArchiveEntry is selected in the Media Panel.
- **Value range:** True · False

### `tags`

- **Type:** `list`
- **Description:** The tag list of an object in the Media Panel.
- **Value range:** None Parent page: Autodesk Flame Python: flame module

###
