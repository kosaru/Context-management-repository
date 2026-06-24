#!/usr/bin/env python3
"""Generate a machine-maintained index of canonical note article cards."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import collect_note as base

INDEX_PATH = base.ROOT / "articles" / "CARD_INDEX.md"
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


def canonical_cards() -> list[dict[str, str]]:
    cards = [choose_canonical(items) for items in grouped_cards().values()]
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
        "note IDを主キーとし、同じnote IDのカードが複数ある場合は、解析済み・確認済みのカードを優先する。",
        "",
        f"登録カード：{len(cards)}件",
        "",
        "| 公開日 | note ID | 記事 | 状態 | note |",
        "|---|---|---|---|---|",
    ]
    for card in cards:
        title = card["title"].replace("|", "\\|")
        url_cell = f"[公開本文]({card['note_url']})" if card["note_url"] else "-"
        lines.append(
            f"| {card['published_at']} | `{card['id']}` | "
            f"[{title}]({card['relative_path']}) | {card['status']} | {url_cell} |"
        )
    if not cards:
        lines.append("| - | - | まだ登録されていません | - | - |")
    INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    write_index()
    print(f"wrote {INDEX_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
