#!/usr/bin/env python3
"""Generate a machine-maintained index of canonical note article cards.

Card paths and analysis status come from article cards. Current public metadata
comes from sources/note/catalog.json when available. This keeps date/title
changes from forcing analyzed card renames.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import collect_note as base

INDEX_PATH = base.ROOT / "articles" / "CARD_INDEX.md"
CATALOG_PATH = base.SOURCE_DIR / "catalog.json"
STATUS_RANK = {
    "analyzed": 30,
    "reviewed": 30,
    "proposed": 20,
    "unreviewed": 10,
    "unknown": 0,
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


def load_catalog_articles() -> dict[str, dict[str, Any]]:
    if not CATALOG_PATH.exists():
        return {}
    try:
        payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    articles = payload.get("articles")
    return articles if isinstance(articles, dict) else {}


def canonical_cards() -> list[dict[str, str]]:
    catalog = load_catalog_articles()
    cards: list[dict[str, str]] = []
    for items in grouped_cards().values():
        card = dict(choose_canonical(items))
        current = catalog.get(card["id"])
        if isinstance(current, dict):
            for key in ("title", "published_at", "note_url", "public_status"):
                value = current.get(key)
                if isinstance(value, str) and value:
                    card[key] = value
        cards.append(card)
    cards.sort(
        key=lambda item: (item["published_at"], item["id"]),
        reverse=True,
    )
    return cards


def write_index() -> None:
    cards = canonical_cards()
    lines = [
        "# 記事カード索引",
        "",
        "このファイルは収集処理が自動生成する。人間が編集する全体案内は `INDEX.md` を参照する。",
        "",
        "note IDを主キーとする。カードのパスと解析状態は記事カード、公開日・タイトル・公開状態は状態目録の最新値を優先する。",
        "",
        "公開日が変わっても、解析済みカードを自動改名・上書きしない。",
        "",
        f"登録カード：{len(cards)}件",
        "",
        "| 公開日 | note ID | 記事 | 解析状態 | 公開状態 | note |",
        "|---|---|---|---|---|---|",
    ]
    for card in cards:
        title = card["title"].replace("|", "\\|")
        url_cell = f"[公開本文]({card['note_url']})" if card["note_url"] else "-"
        lines.append(
            f"| {card['published_at']} | `{card['id']}` | "
            f"[{title}]({card['relative_path']}) | {card['status']} | "
            f"{card['public_status']} | {url_cell} |"
        )
    if not cards:
        lines.append("| - | - | まだ登録されていません | - | - | - |")
    INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    write_index()
    print(f"wrote {INDEX_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
