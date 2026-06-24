#!/usr/bin/env python3
"""Scan every detailed article card for structural stabilization risks.

This script does not decide whether a card is faithful. It exposes sections and
phrases that commonly weaken source strength so every card is included in the
manual source-to-card audit.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD_DIR = ROOT / "articles" / "cards"
OUTPUT = ROOT / "analysis" / "stabilization_audit" / "AUTOMATED_CARD_SCAN.md"

SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

PATTERNS: dict[str, tuple[str, ...]] = {
    "RETROACTIVE": (
        "後期",
        "初期段階",
        "初期仮説",
        "初期の試行",
        "前史",
        "後の記事",
        "後続",
        "修正対象",
        "現在の最終",
    ),
    "MODEL_CLOSURE": (
        "モデル",
        "段階",
        "三機能",
        "七層",
        "八つの責任",
        "判定条件",
        "チェック",
        "整理する",
        "位置づける",
    ),
    "PROVIDER_TO_USER": (
        "利用者が",
        "利用者側",
        "使い方",
        "稽古",
        "点検する",
        "リテラシー",
        "人間側",
    ),
    "INTENT_CAUTION": (
        "意図を断定",
        "意図は確認",
        "意図の一致",
        "利害が一致",
        "共謀",
        "市場圧力",
        "構造推論",
    ),
    "MODERATING_CAVEAT": (
        "一律に否定",
        "全面否定",
        "すべてが",
        "必ず",
        "悪意",
        "単純化",
        "ただし",
        "一方で",
    ),
}

RISK_SECTIONS = (
    "記事の位置づけ",
    "中心命題",
    "論理の流れ",
    "以前の記事から維持したもの",
    "この記事で新しく押し広げたもの",
    "文脈差分",
    "棄却した読み",
    "解析上の不確実性",
)


def parse_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def split_sections(text: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).strip()] = text[start:end].strip()
    return sections


def compact(value: str, limit: int = 260) -> str:
    value = re.sub(r"```.*?```", " ", value, flags=re.DOTALL)
    value = re.sub(r"\s+", " ", value).strip()
    value = value.replace("|", "\\|")
    if len(value) > limit:
        return value[: limit - 1] + "…"
    return value


def main() -> int:
    rows: list[dict[str, object]] = []
    tag_counts: Counter[str] = Counter()

    for path in sorted(CARD_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta = parse_front_matter(text)
        note_id = meta.get("id", path.stem)
        title = meta.get("title", path.stem)
        sections = split_sections(text)

        tags: list[str] = []
        for tag, phrases in PATTERNS.items():
            if any(phrase in text for phrase in phrases):
                tags.append(tag)
                tag_counts[tag] += 1
        if "棄却した読み" in sections:
            tags.append("REJECTED_READINGS_SECTION")
            tag_counts["REJECTED_READINGS_SECTION"] += 1
        if "解析上の不確実性" in sections:
            tags.append("UNCERTAINTY_SECTION")
            tag_counts["UNCERTAINTY_SECTION"] += 1
        if all(name in sections for name in ("中心命題", "論理の流れ", "文脈差分")):
            tags.append("LINEAR_CARD_STRUCTURE")
            tag_counts["LINEAR_CARD_STRUCTURE"] += 1

        excerpts: list[str] = []
        for name in RISK_SECTIONS:
            value = sections.get(name, "")
            if value:
                excerpts.append(f"**{name}**: {compact(value)}")

        rows.append(
            {
                "id": note_id,
                "title": title,
                "path": path.relative_to(ROOT).as_posix(),
                "tags": tags,
                "excerpts": excerpts,
            }
        )

    lines = [
        "# 全詳細カードの自動安定化走査",
        "",
        "この走査は意味上の最終判定ではない。全カードを漏れなく人間の原文比較へ送るため、安定化に使われやすい構造と語句を露出する。",
        "",
        f"- 走査カード：{len(rows)}件",
        "- 強度監査通過：0件",
        "",
        "## 検出数",
        "",
        "| タグ | 件数 |",
        "|---|---:|",
    ]
    for tag, count in sorted(tag_counts.items()):
        lines.append(f"| `{tag}` | {count} |")

    lines.extend(["", "## 全カード", ""])
    for row in rows:
        tags = ", ".join(f"`{tag}`" for tag in row["tags"]) or "なし"
        lines.extend(
            [
                f"### `{row['id']}` {row['title']}",
                "",
                f"- カード：`{row['path']}`",
                f"- 検出タグ：{tags}",
                "",
            ]
        )
        for excerpt in row["excerpts"]:
            lines.extend([f"- {excerpt}", ""])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT} ({len(rows)} cards)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
