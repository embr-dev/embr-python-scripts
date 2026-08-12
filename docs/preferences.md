# Embr Preferences

Main Menu → **Embr → Preferences**。Embr メニューの **並び順**と **表示/非表示**をユーザーが変えられる。

## データ

| 種別 | 場所 | 役割 |
|------|------|------|
| デフォルト | `scripts/embr/menus/defaults.json` | 開発者が決める最適順・初期表示（リポ管理） |
| ユーザー | **`…/flame/embr/prefs.json`**（常にユーザー側） | 差分のみ（`order` / `hidden`） |

インストールが Shared でも prefs はユーザーフォルダ。`…/python/Embr/.embr/state.json`（チャネル・インストール状態）とは分離。

| OS | prefs パス |
|----|------------|
| Linux | `~/flame/embr/prefs.json` |
| macOS | `~/Library/Preferences/Autodesk/flame/embr/prefs.json` |

prefs 例:

```json
{
  "schema": 1,
  "menus": {
    "main_menu": {
      "order": ["preferences", "script_manager"],
      "hidden": ["script_manager"]
    }
  }
}
```

- キーは表示名ではなく **安定 action id**。
- 新しいツールは defaults の末尾に追従（prefs の `order` に無い ID）。
- **Reset to Defaults** で `menus` を空にする。

## ランタイム

各ツールは `embr.menus.action` / `group` だけ使う。Apply 後は `hooks.refresh()` 相当で Rescan。

パッケージ: `scripts/embr_preferences/`（UI）。API: `scripts/embr/embr_menus.py` · `paths.flame_user_embr_dir()`。
