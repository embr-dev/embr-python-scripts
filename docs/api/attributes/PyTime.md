# PyTime Attributes

時間単位。コンストラクタ: `PyTime(timecode, frame_rate)` / `PyTime(relative_frame)` / `PyTime(absolute_frame, frame_rate)`。

| 項目 | 内容 |
|------|------|
| 一次情報 | flame module HTML（属性中心クラス） |
| 関連 | [flame-module.md](../flame-module.md) · [README.md](./README.md) |

## Read-only properties

| 属性 | 説明 |
|------|------|
| `frame` | Return the absolute frame number. |
| `frame_rate` | Return the object frame rate. |
| `relative_frame` | Return the relative frame number. |
| `timecode` | Return the timecode. |

