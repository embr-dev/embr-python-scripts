# embr-python-scripts

Python scripts and utilities for **Autodesk Flame**.

Part of **[Embr](https://github.com/embr-dev/Embr)** — tools and community resources for Flame, with a Japan-focused outlook.

## Status

Early setup. Hooks / util は `scripts/`。規約は [docs/conventions.md](./docs/conventions.md)。

## Documentation

| Document | Contents |
|----------|----------|
| [docs/prerequisites.md](./docs/prerequisites.md) | Flame 2025.0+ 向け開発前提 |
| [docs/conventions.md](./docs/conventions.md) | スクリプト／パッケージ規約 |
| [docs/dev-setup.md](./docs/dev-setup.md) | `DL_PYTHON_HOOK_PATH` の出典と試し方 |
| [docs/embr-util.md](./docs/embr-util.md) | `scripts/embr` 共通 util |
| [docs/script-manager.md](./docs/script-manager.md) | Embr Manager（Scripts タブ / カタログ） |
| [docs/ai-runtime.md](./docs/ai-runtime.md) | PyBox / AI ランタイム（`~/Embr`） |
| [docs/api/](./docs/api/) | Flame Python API（hooks / module / attributes / examples） |
| [docs/api/attributes/](./docs/api/attributes/) | Attributes（属性）原文寄り集約 |
| [docs/pyflame-reference.md](./docs/pyflame-reference.md) | PyFlame 参照メモ（Embr 自前 util 設計用） |

**Target:** Autodesk Flame Family **2025.0+**（Python 3.11 / PySide6）。PyFlame は使わず、共通機能は Embr 側で用意する。

開発時の起動例:

```bash
./tools/run_flame_dev.sh
```

配布相当（チャンネル `dev` から User `python/Embr` へ）:

```bash
git clone -b dev https://github.com/embr-dev/embr-python-scripts.git
cd embr-python-scripts
"$(./tools/find_flame_python.sh)" tools/bootstrap_from_channel.py --channel dev
```

（`/opt/Autodesk/python/2025` は無い環境が多い。実体は `2025.2.7` のようなマイナー付きフォルダ。）

詳細: [docs/script-manager.md](./docs/script-manager.md)。

## Related repositories

| Repository | Role |
|------------|------|
| [Embr](https://github.com/embr-dev/Embr) | Brand, docs, shared assets |
| [embr-matchbox-shaders](https://github.com/embr-dev/embr-matchbox-shaders) | Matchbox shaders |
| **embr-python-scripts** (this repo) | Flame Python scripts |

## License

MIT — see [LICENSE](./LICENSE).
