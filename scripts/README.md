# Scripts

Flame が読む Python hooks を置く。開発時は `DL_PYTHON_HOOK_PATH` でこのディレクトリを指定する（[docs/dev-setup.md](../docs/dev-setup.md)）。

| Path | Role |
|------|------|
| `embr/` | 共通ユーティリティ（フック関数なし）+ `assets/`（ロゴ・Figtree） |
| `embr_manager/` | Script Manager（Install / Update / Uninstall / Repair） |
| `embr_<tool>/` | その他ツール本体（フック入口はここ） |

規約: [docs/conventions.md](../docs/conventions.md)  
前提: [docs/prerequisites.md](../docs/prerequisites.md)  
util API: [docs/embr-util.md](../docs/embr-util.md)  
Script Manager: [docs/script-manager.md](../docs/script-manager.md)
