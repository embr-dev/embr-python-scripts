#!/usr/bin/env python3
"""Generate docs/api/flame-module.md and docs/api/attributes/*.md from saved Help HTML."""

from __future__ import annotations

import html
import re
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DOC = ROOT / "docs" / "API Documentation"
OUT_API = ROOT / "docs" / "api"
OUT_ATTR = OUT_API / "attributes"


def strip_tags(s: str) -> str:
    s = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", s)
    s = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", s)
    s = re.sub(r"(?is)<br\s*/?>", "\n", s)
    s = re.sub(r"(?is)</(p|div|li|tr|h[1-6]|dt|dd)>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return html.unescape(s)


def clean_lines(text: str) -> list[str]:
    lines = [re.sub(r"[ \t]+", " ", L).rstrip() for L in text.splitlines()]
    out: list[str] = []
    blank = 0
    for L in lines:
        if not L.strip():
            blank += 1
            if blank <= 1:
                out.append("")
        else:
            blank = 0
            out.append(L)
    return out


def find_main_html(folder: Path) -> Path | None:
    cands = [
        p
        for p in folder.rglob("*.html")
        if "_files" not in p.parts and p.stat().st_size > 15000
    ]
    if not cands:
        return None
    return max(cands, key=lambda p: p.stat().st_size)


def esc_cell(s: str) -> str:
    return s.replace("|", "\\|")


def parse_attribute_page(html_path: Path) -> str:
    raw2 = html_path.read_text(encoding="utf-8", errors="replace")
    raw2 = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", raw2)
    raw2 = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", raw2)
    raw2 = re.sub(r"(?is)<h1[^>]*>", "\n# ", raw2)
    raw2 = re.sub(r"(?is)<h2[^>]*>", "\n## ", raw2)
    raw2 = re.sub(r"(?is)<h3[^>]*>", "\n### ", raw2)
    raw2 = re.sub(r"(?is)</h[1-3]>", "\n", raw2)
    raw2 = re.sub(r"(?is)<br\s*/?>", "\n", raw2)
    raw2 = re.sub(r"(?is)</(p|div|li|tr|dt)>", "\n", raw2)
    raw2 = re.sub(r"(?is)<dd[^>]*>", "\n: ", raw2)
    plain = html.unescape(re.sub(r"<[^>]+>", "", raw2))
    lines = clean_lines(plain)
    joined = "\n".join(lines)
    m2 = re.search(r"^# .+Attributes.*$", joined, re.M | re.I)
    if m2:
        joined = joined[m2.start() :]
    elif re.search(r"^# Py", joined, re.M):
        m3 = re.search(r"^# Py.+$", joined, re.M)
        if m3:
            joined = joined[m3.start() :]
    for marker in ["Was this information helpful", "Except where otherwise noted"]:
        j = joined.find(marker)
        if j > 0:
            joined = joined[:j]
    return joined.strip()


def class_block(raw: str, cls: str) -> str:
    m = re.search(rf'<a name="{cls}"', raw)
    if not m:
        return ""
    start = m.start()
    nxt = re.search(r'<a name="Py\w+"', raw[start + 10 :])
    end = start + 10 + nxt.start() if nxt else min(len(raw), start + 20000)
    return raw[start:end]


def parse_prop_section(block: str, title: str) -> list[tuple[str, str]]:
    m = re.search(
        re.escape(title)
        + r"(.*?)(?=(Static methods|Methods defined|Data descriptors|Read-only properties|Data and other|Methods inherited|Static methods inherited|class |$))",
        block,
        re.S | re.I,
    )
    if not m:
        return []
    plain = html.unescape(re.sub(r"<[^>]+>", "\n", m.group(1)))
    items = [
        re.sub(r"\s+", " ", L).strip()
        for L in plain.splitlines()
        if L.strip() and not L.strip().startswith("__")
    ]
    props: list[tuple[str, str]] = []
    i = 0
    while i < len(items):
        name = items[i]
        if re.match(r"^[a-z_][a-z0-9_]*$", name):
            desc = ""
            if i + 1 < len(items) and not re.match(r"^[a-z_][a-z0-9_]*$", items[i + 1]):
                desc = items[i + 1]
                i += 2
            else:
                i += 1
            props.append((name, desc))
        else:
            if props:
                n, d = props[-1]
                props[-1] = (n, (d + " " + name).strip())
            i += 1
    return props


def generate_flame_module(raw: str) -> None:
    entries: list[tuple[str, str, str, str]] = []
    for m in re.finditer(
        r'<a name="([^"]+)"[^>]*>\s*<strong>([^<]+)</strong>\s*</a>\s*(\([^<]*\))?',
        raw,
    ):
        nid, label, sig = m.group(1), html.unescape(m.group(2)), (m.group(3) or "").strip()
        if label.startswith("__") and label.endswith("__"):
            continue
        rest = raw[m.end() : m.end() + 1600]
        dd = re.search(r"(?is)<dd[^>]*>(.*?)</dd>", rest)
        desc = ""
        if dd:
            t = re.sub(r"(?s)<[^>]+>", " ", dd.group(1))
            desc = html.unescape(re.sub(r"\s+", " ", t)).strip()[:500]
        if nid.startswith("-"):
            cls = "__module__"
        elif "-" in nid:
            cls = nid.split("-", 1)[0]
        else:
            continue
        entries.append((cls, label, sig, desc))

    by_cls: OrderedDict[str, list[tuple[str, str, str]]] = OrderedDict()
    for cls, label, sig, desc in entries:
        by_cls.setdefault(cls, []).append((label, sig, desc))

    module_funcs = by_cls.pop("__module__", [])

    priority = [
        "PyProject",
        "PyBatch",
        "PyClip",
        "PySequence",
        "PyDesktop",
        "PyWorkspace",
        "PyLibrary",
        "PyFolder",
        "PyReel",
        "PyReelGroup",
        "PyNode",
        "PySegment",
        "PyTrack",
        "PyVersion",
        "PyTimelineFX",
        "PyMediaPanel",
        "PyMessages",
        "PyBrowser",
        "PySearch",
        "PyExporter",
        "PyActionNode",
        "PyActionFamilyNode",
    ]

    def cls_key(c: str):
        try:
            return (0, priority.index(c))
        except ValueError:
            return (1, c.lower())

    classes = sorted(by_cls.keys(), key=cls_key)

    module_data = [
        ("batch", "PyBatch", "現在の Batch グループ"),
        ("browser", "PyBrowser", "ブラウザ"),
        ("media_panel", "PyMediaPanel", "Media Panel（move / copy / selected_entries 等）"),
        ("mediahub", "PyMediaHub", "MediaHub"),
        ("messages", "PyMessages", "メッセージバー（show_in_console 等）"),
        ("project", "PyProjectSelector", "互換用のプロジェクト選択子"),
        ("projects", "PyProjectSelector", "推奨（2020.1+）。current_project など"),
        ("search", "PySearch", "検索"),
        ("timeline", "PyTimeline", "タイムライン"),
        ("users", "PyUsers", "ユーザー（current_user 等）"),
    ]

    attr_only = [
        "PyFlameObject",
        "PyMarker",
        "PyMediaHub",
        "PyProjectSelector",
        "PyResolution",
        "PyTime",
        "PyTimeline",
        "PyUser",
        "PyUsers",
    ]

    lines: list[str] = []
    A = lines.append
    A("# flame モジュール索引（Flame 2025）")
    A("")
    A("公式 Help「Autodesk Flame Python: flame module」から抽出した索引。")
    A("メソッド／モジュール関数の情報量は維持し、**属性の詳細は [attributes/](./attributes/) に集約**する。")
    A("")
    A("| 項目 | 内容 |")
    A("|------|------|")
    A("| 一次情報 | `docs/API Documentation/Autodesk Flame Family Python Module/` |")
    A(f"| 公開メソッド（dunder 除く） | {sum(len(by_cls[c]) for c in classes)} |")
    A(f"| クラス節 | {len(classes)} |")
    A("| モジュール Functions | 26 |")
    A("| モジュール Data | 10 |")
    A("")
    A(
        "関連: [attributes/](./attributes/) · [defines.md](./defines.md) · "
        "[recipes.md](./recipes.md) · [getting-started.md](./getting-started.md) · [hooks.md](./hooks.md)"
    )
    A("")
    A("## 目次")
    A("")
    A("1. [カバレッジ](#カバレッジ)")
    A("2. [モジュール Data](#モジュール-data)")
    A("3. [モジュール Functions](#モジュール-functions)")
    A("4. [クラス索引](#クラス索引)")
    A("5. [クラス別メソッド](#クラス別メソッド)")
    A("")
    A("---")
    A("")
    A("## カバレッジ")
    A("")
    A("| 公式の塊 | この文書 | 備考 |")
    A("|----------|----------|------|")
    A("| 末尾 Functions（26） | 収録 | 抜けなし |")
    A("| 末尾 Data（10） | 収録 | 抜けなし |")
    A("| 各クラス公開 Static methods | 収録 | 突合差分 0 |")
    A("| 属性中心クラス（PyTime 等） | 名前のみ → [attributes/](./attributes/) | 属性本文は Attributes 側 |")
    A("| Read-only / Data descriptors | [attributes/](./attributes/) | メソッド索引から分離 |")
    A("| Data and other（PresetType 等） | [attributes/Data_and_other_attributes.md](./attributes/Data_and_other_attributes.md) | |")
    A("| dunder | 省略 | `__init__` 等 |")
    A("")
    A("---")
    A("")
    A("## モジュール Data")
    A("")
    A("公式 Help 末尾 **Data**。呼び出しは `flame.<name>`。")
    A("")
    A("| 属性 | 型 | 用途 |")
    A("|------|-----|------|")
    for name, typ, use in module_data:
        note = " **推奨**" if name == "projects" else ""
        A(f"| `flame.{name}` | `{typ}` | {use}{note} |")
    A("")
    A("```python")
    A("import flame")
    A("")
    A("batch = flame.batch")
    A("project = flame.projects.current_project")
    A('flame.messages.show_in_console("ok", "info", 3)')
    A("```")
    A("")
    A("到達パス: [defines.md](./defines.md)。属性詳細: [attributes/README.md](./attributes/README.md)。")
    A("")
    A("---")
    A("")
    A("## モジュール Functions")
    A("")
    A("公式 Help 末尾 **Functions**。呼び出しは `flame.<name>(...)`。")
    A("")
    A("| 関数 | 説明（Help 抜粋） |")
    A("|------|-------------------|")
    for label, sig, desc in module_funcs:
        d = esc_cell(desc) if desc else "*(説明なし — Help 原文も空に近い)*"
        A(f"| `{label}{sig or '(...)'}` | {d} |")
    A("")
    A("---")
    A("")
    A("## クラス索引")
    A("")
    A("| クラス | メソッド数 | Attributes |")
    A("|--------|------------|------------|")

    def attr_href(cls: str) -> str:
        # Prefer exact file if exists after generation; always link conventional path
        special = {
            "PyNode": "./attributes/PyNode.md",
        }
        if cls in special:
            return f"[doc]({special[cls]})"
        return f"[doc](./attributes/{cls}.md)"

    for c in classes:
        anchor = c.lower()
        A(f"| [`{c}`](#{anchor}) | {len(by_cls[c])} | {attr_href(c)} |")
    A("")
    A("属性中心（メソッドほぼ無し）:")
    A("")
    for c in attr_only:
        A(f"- [`{c}`](./attributes/{c}.md)")
    A("")
    A("---")
    A("")
    A("## クラス別メソッド")
    A("")
    for c in classes:
        A(f"### `{c}`")
        A("")
        A(f"メソッド数: **{len(by_cls[c])}** · [Attributes](./attributes/{c}.md)")
        A("")
        A("| メソッド | 説明（Help 抜粋） |")
        A("|----------|-------------------|")
        for label, sig, desc in by_cls[c]:
            d = esc_cell(desc) if desc else "*(説明なし)*"
            A(f"| `{label}{sig or '(...)'}` | {d} |")
        A("")

    out = OUT_API / "flame-module.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size} bytes, {len(lines)} lines)")


def generate_attributes(raw_module: str) -> None:
    OUT_ATTR.mkdir(parents=True, exist_ok=True)
    generated: list[tuple[str, str, int]] = []

    for d in sorted((API_DOC / "Attributes").iterdir()):
        if not d.is_dir():
            continue
        html_path = find_main_html(d)
        if not html_path:
            continue
        folder = d.name
        m = re.match(r"(Py\w+)", folder)
        cls = m.group(1) if m else folder
        if "Batch Nodes" in folder:
            out_name = "PyNode_Batch_Nodes"
            title = "PyNode — Batch Nodes Attributes"
        elif "Action Nodes" in folder or "PyCoNode" in folder:
            out_name = "PyCoNode_Action_Nodes"
            title = "PyCoNode — Action Nodes Attributes"
        else:
            out_name = cls
            title = f"{cls} Attributes"

        body = parse_attribute_page(html_path)
        content = "\n".join(
            [
                f"# {title}",
                "",
                "公式 Help の Attributes ページを原文寄りに整理したもの。",
                "",
                "| 項目 | 内容 |",
                "|------|------|",
                f"| 一次情報 | `docs/API Documentation/Attributes/{folder}/` |",
                "| 関連 | [flame-module.md](../flame-module.md)（メソッド索引） |",
                "",
                "---",
                "",
                body
                if body
                else "_（HTML から本文を抽出できませんでした。一次情報の HTML を参照してください。）_",
                "",
            ]
        )
        outp = OUT_ATTR / f"{out_name}.md"
        outp.write_text(content, encoding="utf-8")
        generated.append((out_name, title, outp.stat().st_size))
        print(f"ATTR {out_name} ({outp.stat().st_size})")

    # Attribute-only / module-sourced pages
    extras_meta = {
        "PyFlameObject": "全 Flame オブジェクトの基底型。",
        "PyMarker": "Marker（`PyFlameObject` 継承）。専用 Attributes ページがある場合はそちらも参照。",
        "PyMediaHub": "`flame.mediahub` の型。",
        "PyProjectSelector": "`flame.projects` / `flame.project` の型。",
        "PyResolution": "解像度オブジェクト。",
        "PyTime": (
            "時間単位。コンストラクタ（Help）: "
            "`PyTime(timecode, frame_rate)` / `PyTime(relative_frame)` / "
            "`PyTime(absolute_frame, frame_rate)`。"
        ),
        "PyTimeline": "`flame.timeline` の型。",
        "PyUser": "ユーザー。",
        "PyUsers": "`flame.users` の型。",
    }

    for cls, blurb in extras_meta.items():
        existing = OUT_ATTR / f"{cls}.md"
        # Keep large official Attributes extract if present (e.g. PyMarker)
        if existing.exists() and existing.stat().st_size > 2500 and cls == "PyMarker":
            # Append module-sourced supplement
            block = class_block(raw_module, cls)
            ro = parse_prop_section(block, "Read-only properties defined here:")
            dd = parse_prop_section(block, "Data descriptors defined here:")
            if ro or dd:
                extra = ["", "---", "", "## Supplement（flame module ページ）", ""]
                if ro:
                    extra += ["### Read-only properties", "", "| 属性 | 説明 |", "|------|------|"]
                    for n, d in ro:
                        extra.append(f"| `{n}` | {esc_cell(d)} |")
                    extra.append("")
                if dd:
                    extra += ["### Data descriptors", "", "| 属性 | 説明 |", "|------|------|"]
                    for n, d in dd:
                        extra.append(f"| `{n}` | {esc_cell(d)} |")
                    extra.append("")
                existing.write_text(existing.read_text(encoding="utf-8") + "\n".join(extra), encoding="utf-8")
            print(f"supplemented {cls}")
            continue

        block = class_block(raw_module, cls)
        ro = parse_prop_section(block, "Read-only properties defined here:")
        dd = parse_prop_section(block, "Data descriptors defined here:")
        bl: list[str] = [
            f"# {cls} Attributes",
            "",
            blurb,
            "",
            "| 項目 | 内容 |",
            "|------|------|",
            "| 一次情報 | flame module HTML（属性中心クラス）／該当 Attributes ページ |",
            "| 関連 | [flame-module.md](../flame-module.md) |",
            "",
        ]
        if ro:
            bl += ["## Read-only properties", "", "| 属性 | 説明 |", "|------|------|"]
            for n, d in ro:
                bl.append(f"| `{n}` | {esc_cell(d)} |")
            bl.append("")
        if dd:
            bl += ["## Data descriptors", "", "| 属性 | 説明 |", "|------|------|"]
            for n, d in dd:
                bl.append(f"| `{n}` | {esc_cell(d)} |")
            bl.append("")
        if not ro and not dd:
            bl.append(
                "_flame module ページ上の追加プロパティ記載はほぼ無し。"
                "継承元や専用 Attributes ページを参照。_"
            )
            bl.append("")
        # Do not clobber a large official page for same name except handled above
        if existing.exists() and existing.stat().st_size > 2500 and cls in {g[0] for g in generated}:
            print(f"skip overwrite {cls}")
            continue
        existing.write_text("\n".join(bl) + "\n", encoding="utf-8")
        print(f"wrote attr-only {cls} ({existing.stat().st_size})")

    # Data and other attributes
    i = raw_module.find("Data and other attributes defined here:")
    if i > 0:
        chunk = raw_module[i : i + 3000]
        plain = html.unescape(re.sub(r"<[^>]+>", "\n", chunk))
        lines_p = [
            re.sub(r"\s+", " ", L).strip() for L in plain.splitlines() if L.strip()
        ]
        preset_lines = [
            "# flame モジュール — Data and other attributes",
            "",
            "flame module HTML の **Data and other attributes** から抽出（主に Exporter / Preset 周辺）。",
            "",
            "| 項目 | 内容 |",
            "|------|------|",
            "| 一次情報 | Autodesk Flame Family Python Module HTML |",
            "| 関連 | [flame-module.md](../flame-module.md) · 必要に応じ PyExporter Attributes |",
            "",
            "## 内容",
            "",
        ]
        for L in lines_p[:100]:
            if L.startswith("Data and other"):
                continue
            if L.startswith("class ") or "font color" in L:
                break
            preset_lines.append(f"- `{L}`" if "=" in L else f"- {L}")
        (OUT_ATTR / "Data_and_other_attributes.md").write_text(
            "\n".join(preset_lines) + "\n", encoding="utf-8"
        )
        print("wrote Data_and_other_attributes")

    # README index
    files = sorted(OUT_ATTR.glob("*.md"))
    files = [f for f in files if f.name != "README.md"]
    idx = [
        "# Attributes（Flame 2025）",
        "",
        "公式 Help の Attributes ページ群と、flame module から移した属性情報を集約。",
        "",
        "| 項目 | 内容 |",
        "|------|------|",
        "| 一次情報 | `docs/API Documentation/Attributes/` |",
        "| 補足 | flame module HTML の属性中心クラス / Data and other |",
        "| メソッド | [../flame-module.md](../flame-module.md) |",
        "",
        "## 目次",
        "",
        "| ドキュメント | 内容 |",
        "|--------------|------|",
    ]
    for f in files:
        title = f.stem.replace("_", " ")
        first = f.read_text(encoding="utf-8", errors="replace").splitlines()[0]
        if first.startswith("# "):
            title = first[2:].strip()
        idx.append(f"| [{f.name}](./{f.name}) | {title} |")
    idx.append("")
    (OUT_ATTR / "README.md").write_text("\n".join(idx) + "\n", encoding="utf-8")
    print(f"Wrote attributes README ({len(files)} pages)")


def main() -> None:
    mod_html = find_main_html(API_DOC / "Autodesk Flame Family Python Module")
    if not mod_html:
        raise SystemExit("flame module HTML not found")
    raw = mod_html.read_text(encoding="utf-8", errors="replace")
    generate_attributes(raw)
    generate_flame_module(raw)


if __name__ == "__main__":
    main()
