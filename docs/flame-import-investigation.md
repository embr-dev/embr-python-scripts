# 調査メモ: Flame hooks と相対 import

調査日: 2026-08-12  
対象: Flame 2025 + `DL_PYTHON_HOOK_PATH` → 本リポ `scripts/`

---

## 結論（要約）

| 問い | 答え |
|------|------|
| 相対 import は **絶対に不可能**か？ | **いいえ。条件付きで可能。** |
| hooks スキャンで各 `.py` を読む経路では？ | **相対 import は失敗する**（`__package__` が空）。 |
| `import embr` のような通常パッケージ import では？ | **相対 import は動く。** |
| 実務上の推奨は？ | hooks 配下は **一意 basename + 絶対 import** が安全（現行方針は妥当）。 |

`DL_PYTHON_HOOK_PATH` が悪いのではなく、**Flame の hooks ローダが「ファイル名＝モジュール名」で読む**ことが本質。

---

## 根拠 1: Flame 本体のログ文言（実機）

実ログ（`Duplicate module name found ui (.../embr_manager/ui.py vs .../embr/ui.py)`）より:

- モジュール名は **パスではなくファイル名（stem）**
- 同名 `.py` が2つあると、片方だけが使われ、もう一方の hooks は無視される

Flame バイナリ内の文字列（抜粋）:

```text
[PYTHON HOOK] Scanning '%s' for python hooks
[PYTHON HOOK] Added '%s' to PYTHONPATH
[PYTHON HOOK] Loading '%s'...
[PYTHON HOOK] Duplicate module name found %s (%s vs %s). ... %s will be used.
[PYTHON HOOK] Reloading '%s'...
[PYTHON HOOK] An error occurred. Ignoring python hooks from %s
```

→ スキャン時にディレクトリを PYTHONPATH へ足し、各 `.py` をロード／リロードする実装。

---

## 根拠 2: 再現実験（Flame 同梱 Python 3.11）

Flame 風ロードを `importlib.util.spec_from_file_location(name=path.stem, …)` で再現。

| ケース | 結果 |
|--------|------|
| A. 親を path に載せ `import demo_pkg`（通常パッケージ） | `__package__=="demo_pkg"`。`from . import helper` **成功** |
| B. `__init__.py` を basename `__init__` として単体ロード | **`attempted relative import with no known parent package`** |
| D. 任意 `.py` を basename でロードし `from . import helper` | **同じエラー** |
| E. basename ロードした hook から `import demo_pkg.helper` | **成功**（パッケージが通常 import できる場合） |

つまり:

- **「相対 import が言語として死んでいる」わけではない**
- **「Flame が hooks 用にファイルを単体ロードしたとき」は相対 import が使えない**

---

## 根拠 3: 今回の実エラーとの対応

| 観測 | 解釈 |
|------|------|
| `embr_manager` is not a package | `embr_manager.py` がモジュール名 `embr_manager` になり、ディレクトリパッケージを潰す |
| Duplicate `ui` / `__init__` | basename 衝突 |
| `relative import with no known parent package`（`embr/__init__.py`） | `__init__.py` がパッケージ文脈ではなく単体／reload された |
| `No module named 'embr_sm_window'` | サブディレクトリが path に無く、一意モジュールを解決できなかった |

開発起動（`DL_PYTHON_HOOK_PATH=…/scripts`）でも、本番の user/shared python でも、**ローダ仕様は同じ**。

---

## 使えるパターン / 使えないパターン

### 使えない（hooks スキャン対象ファイル内）

```python
from . import helper          # basename ロード時に必ず失敗
from .helper import ping
```

### 使える

```python
# 1) 親が PYTHONPATH にあり、通常のパッケージ import ができるとき
import embr.embr_paths as paths
from embr import log

# 2) ファイル名が一意で、そのディレクトリが path にあるとき（現行）
import embr_paths as paths
import embr_sm_window
```

Shotgun / Toolkit 側に `from . import tk_flame` があるが、それは **Toolkit がパッケージとして import する経路**向けで、Flame hooks の「全 `.py` を basename ロード」と同じ前提ではない。

---

## 本リポ方針への含意

現行の「一意 basename（`embr_paths.py` / `embr_sm_*.py`）+ path 追加 + 絶対 import」は、調査結果と整合している。

将来パッケージ相対 import（`from . import …`）に戻すなら、少なくとも次が必要:

1. hooks に拾わせる入口 `.py` は相対 import を書かない  
2. ライブラリ本体は Flame にスキャンさせない場所へ置く、または  
3. スキャンされても壊れないよう `__init__.py` を相対 import なしにする  

現状の hooks 配置のまま全面的に相対 import へ戻すのは **非推奨**。
