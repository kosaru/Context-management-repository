#!/usr/bin/env python3
"""Generate a machine-maintained index of canonical note article cards.

Card paths and individual-card status come from article cards. Current public
metadata comes from sources/note/catalog.json. Corpus-level analysis coverage
comes from analysis/COVERAGE.json. These are deliberately shown separately so
an unreviewed auto-generated card is not mistaken for an unanalyzed article.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import collect_note as base

INDEX_PATH = base.ROOT / "articles" / "CARD_INDEX.md"
CATALOG_PATH = base.SOURCE_DIR / "catalog.json"
COVERAGE_PATH = base.ROOT / "analysis" / "COVERAGE.json"
STATUS_RANK = {
    "analyzed": 30,
    "reviewed": 30,
    "proposed": 20,
    "unreviewed": 10,
    "unknown": 0,
}
CARD_STATUS_LABELS = {
    "analyzed": "個別カード精査済み",
    "reviewed": "個別カード精査済み",
    "proposed": "個別カード案",
    "unreviewed": "個別カード未精査",
    "unknown": "個別カード状態不明",
}
ANALYSIS_STATE_LABELS = {
    "covered": "文脈解析済み",
    "pending": "文脈未解析",
    "deferred": "文脈判定保留",
}


def card_info(path: Path) -> dict[str, str]:
    data = base.parse_front_matter(path)
    return {
        "id": data.get("id", ""),
        "title": data.get("title", path.stem),
        "status": data.get("status", "unknown"),
        "published_at": data.get("published_at", ""),
        "note_url": data.get("note_url", ""),
        "public_status": "unknown",
        "analysis_state": "unknown",
        "analysis_label": "",
        "analysis_ref": "",
        "relative_path": path.relative_to(INDEX_PATH.parent).as_posix(),
        "absolute_path": path.as_posix(),
    }


def choose_canonical(items: list[dict[str, str]]) -> dict[str, str]:
    return max(
        items,
        key=lambda item: (
            STATUS_RANK.get(item["status"], 0),
            bool(item["published_at"]),
            item["relative_path"],
        ),
    )


def grouped_cards() -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for path in sorted(base.CARD_DIR.glob("*.md")):
        info = card_info(path)
        if info["id"]:
            grouped[info["id"]].append(info)
    return grouped


def canonical_card(note_id: str) -> dict[str, str] | None:
    items = grouped_cards().get(note_id, [])
    return choose_canonical(items) if items else None


def load_articles(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    articles = payload.get("articles")
    return articles if isinstance(articles, dict) else {}


def canonical_cards() -> list[dict[str, str]]:
    catalog = load_articles(CATALOG_PATH)
    coverage = load_articles(COVERAGE_PATH)
    cards: list[dict[str, str]] = []
    for items in grouped_cards().values():
        card = dict(choose_canonical(items))
        current = catalog.get(card["id"])
        if isinstance(current, dict):
            for key in ("title", "published_at", "note_url", "public_status"):
                value = current.get(key)
                if isinstance(value, str) and value:
                    card[key] = value
        covered = coverage.get(card["id"])
        if isinstance(covered, dict):
            for key in ("analysis_state", "analysis_label", "analysis_ref"):
                value = covered.get(key)
                if isinstance(value, str) and value:
                    card[key] = value
        cards.append(card)
    cards.sort(
        key=lambda item: (item["published_at"], item["id"]),
        reverse=True,
    )
    return cards


def analysis_cell(card: dict[str, str]) -> str:
    state = card.get("analysis_state", "unknown")
    state_label = ANALYSIS_STATE_LABELS.get(state, f"文脈状態：{state}")
    label = card.get("analysis_label", "")
    ref = card.get("analysis_ref", "")
    if label and ref:
        return f"{state_label}（[{label}](../{ref})）"
    if label:
        return f"{state_label}（{label}）"
    return state_label


def card_status_label(status: str) -> str:
    return CARD_STATUS_LABELS.get(status, f"個別カード：{status}")


def write_index() -> None:
    cards = canonical_cards()
    analysis_counts = Counter(card.get("analysis_state", "unknown") for card in cards)
    card_counts = Counter(card.get("status", "unknown") for card in cards)
    individually_reviewed = card_counts.get("analyzed", 0) + card_counts.get("reviewed", 0)
    individually_unreviewed = card_counts.get("unreviewed", 0)

    lines = [
        "# 記事カード索引",
        "",
        "このファイルは収集処理が自動生成する。人間が編集する全体案内は `INDEX.md` を参照する。",
        "",
        "**ここでいう「個別カード未精査」は、記事本文が未分析という意味ではない。**",
        "第1〜第6期の資料束で文脈解析済みの記事でも、自動生成された個別カードを一件ずつ整えていなければ「個別カード未精査」と表示する。",
        "",
        "```text",
        "文脈解析状態",
        "  → 記事本文が、どの解析単位で読まれているか",
        "",
        "個別カード状態",
        "  → その記事専用のカードが、一件単位で精査されているか",
        "```",
        "",
        "note IDを主キーとする。公開日・タイトル・公開状態は状態目録、文脈解析状態はカバレッジ台帳、個別カード状態は記事カードを正本とする。",
        "",
        "公開日が変わっても、解析済みカードを自動改名・上書きしない。",
        "",
        f"- 登録記事：{len(cards)}件",
        f"- 文脈解析済み：{analysis_counts.get('covered', 0)}件",
        f"- 文脈未解析：{analysis_counts.get('pending', 0)}件",
        f"- 文脈判定保留：{analysis_counts.get('deferred', 0)}件",
        f"- 個別カード精査済み：{individually_reviewed}件",
        f"- 個別カード未精査：{individually_unreviewed}件",
        "",
        "| 公開日 | note ID | 記事 | 文脈解析 | 個別カード | 公開状態 | note |",
        "|---|---|---|---|---|---|---|",
    ]
    for card in cards:
        title = card["title"].replace("|", "\\|")
        url_cell = f"[公開本文]({card['note_url']})" if card["note_url"] else "-"
        lines.append(
            f"| {card['published_at']} | `{card['id']}` | "
            f"[{title}]({card['relative_path']}) | {analysis_cell(card)} | "
            f"{card_status_label(card['status'])} | {card['public_status']} | {url_cell} |"
        )
    if not cards:
        lines.append("| - | - | まだ登録されていません | - | - | - | - |")
    INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    write_index()
    print(f"wrote {INDEX_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
