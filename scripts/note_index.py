#!/usr/bin/env python3
"""Generate a machine-maintained article and analysis index.

The index covers every catalogued note article. Public metadata comes from
sources/note/catalog.json, corpus-level analysis coverage comes from
analysis/COVERAGE.json, and an individual card is linked only when one actually
exists. Card existence/content status and source-strength audit status are kept
separate.
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
    "analyzed": "個別カードあり・内容記入済み",
    "reviewed": "個別カードあり・内容記入済み",
    "proposed": "個別カード案",
    "unreviewed": "個別カード未確認",
    "missing": "個別カードなし",
    "unknown": "個別カード状態不明",
}
STRENGTH_AUDIT_LABELS = {
    "pending": "強度監査待ち",
    "high-risk": "安定化高リスク",
    "confirmed": "安定化確認済み・要改稿",
    "rewrite-required": "要全面改稿",
    "passed": "強度監査通過",
    "unknown": "強度監査状態不明",
}
ANALYSIS_STATE_LABELS = {
    "covered": "文脈解析あり",
    "pending": "文脈未解析",
    "deferred": "文脈判定保留",
    "unknown": "文脈状態不明",
}


def card_info(path: Path) -> dict[str, str]:
    data = base.parse_front_matter(path)
    return {
        "id": data.get("id", ""),
        "title": data.get("title", path.stem),
        "status": data.get("status", "unknown"),
        "strength_audit": data.get("strength_audit", "pending"),
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


def load_articles(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    articles = payload.get("articles")
    return articles if isinstance(articles, dict) else {}


def coverage_for(note_id: str) -> dict[str, Any] | None:
    value = load_articles(COVERAGE_PATH).get(note_id)
    return value if isinstance(value, dict) else None


def indexed_articles() -> list[dict[str, str]]:
    catalog = load_articles(CATALOG_PATH)
    coverage = load_articles(COVERAGE_PATH)
    cards = grouped_cards()
    note_ids = set(catalog) | set(coverage) | set(cards)
    rows: list[dict[str, str]] = []

    for note_id in note_ids:
        current = catalog.get(note_id, {})
        covered = coverage.get(note_id, {})
        card_items = cards.get(note_id, [])
        card = choose_canonical(card_items) if card_items else None

        row = {
            "id": note_id,
            "title": str(current.get("title") or (card or {}).get("title") or note_id),
            "published_at": str(
                current.get("published_at") or (card or {}).get("published_at") or ""
            ),
            "note_url": str(current.get("note_url") or (card or {}).get("note_url") or ""),
            "public_status": str(current.get("public_status") or "unknown"),
            "analysis_state": str(covered.get("analysis_state") or "unknown"),
            "analysis_label": str(covered.get("analysis_label") or ""),
            "analysis_ref": str(covered.get("analysis_ref") or ""),
            "card_status": str((card or {}).get("status") or "missing"),
            "strength_audit": str((card or {}).get("strength_audit") or "unknown"),
            "card_path": str((card or {}).get("relative_path") or ""),
        }
        rows.append(row)

    rows.sort(key=lambda item: (item["published_at"], item["id"]), reverse=True)
    return rows


def canonical_cards() -> list[dict[str, str]]:
    """Backward-compatible alias for callers expecting the generated rows."""
    return indexed_articles()


def analysis_cell(article: dict[str, str]) -> str:
    state = article.get("analysis_state", "unknown")
    state_label = ANALYSIS_STATE_LABELS.get(state, f"文脈状態：{state}")
    label = article.get("analysis_label", "")
    ref = article.get("analysis_ref", "")
    if label and ref:
        return f"{state_label}（[{label}](../{ref})）"
    if label:
        return f"{state_label}（{label}）"
    return state_label


def card_cell(article: dict[str, str]) -> str:
    status = article.get("card_status", "missing")
    card_label = CARD_STATUS_LABELS.get(status, f"個別カード：{status}")
    path = article.get("card_path", "")
    if path:
        audit = article.get("strength_audit", "unknown")
        audit_label = STRENGTH_AUDIT_LABELS.get(audit, f"強度監査：{audit}")
        return f"[{card_label}／{audit_label}]({path})"
    if article.get("analysis_state") == "covered":
        return "個別カードなし（資料束・横断索引に記述あり）"
    return card_label


def article_cell(article: dict[str, str]) -> str:
    title = article["title"].replace("|", "\\|")
    card_path = article.get("card_path", "")
    note_url = article.get("note_url", "")
    if card_path:
        return f"[{title}]({card_path})"
    if note_url:
        return f"[{title}]({note_url})"
    return title


def write_index() -> None:
    articles = indexed_articles()
    analysis_counts = Counter(
        article.get("analysis_state", "unknown") for article in articles
    )
    card_counts = Counter(article.get("card_status", "missing") for article in articles)
    audit_counts = Counter(
        article.get("strength_audit", "unknown")
        for article in articles
        if article.get("card_status") != "missing"
    )
    cards_present = len(articles) - card_counts.get("missing", 0)

    lines = [
        "# 記事・解析索引",
        "",
        "このファイルは収集処理が自動生成する。人間が編集する全体案内は `INDEX.md` を参照する。",
        "",
        "全記事を一覧化するが、全記事へ個別カードを作ることはしない。",
        "個別カードの存在・内容記入と、元文章の強度監査通過を分けて表示する。",
        "",
        "```text",
        "文脈解析あり",
        "  → 何らかの解析文書に記述がある",
        "",
        "個別カードあり・内容記入済み",
        "  → 記事専用文書が存在する",
        "",
        "強度監査通過",
        "  → 原文との比較で、安定化による弱化がないことを確認した",
        "```",
        "",
        "カードが存在しても、強度監査待ちのものは信頼済み分析として扱わない。",
        "",
        f"- 登録記事：{len(articles)}件",
        f"- 文脈解析あり：{analysis_counts.get('covered', 0)}件",
        f"- 文脈未解析：{analysis_counts.get('pending', 0)}件",
        f"- 文脈判定保留：{analysis_counts.get('deferred', 0)}件",
        f"- 個別カードあり：{cards_present}件",
        f"- 強度監査通過：{audit_counts.get('passed', 0)}件",
        f"- 強度監査待ち：{audit_counts.get('pending', 0)}件",
        f"- 安定化高リスク：{audit_counts.get('high-risk', 0)}件",
        f"- 安定化確認済み・要改稿：{audit_counts.get('confirmed', 0) + audit_counts.get('rewrite-required', 0)}件",
        f"- 個別カードなし：{card_counts.get('missing', 0)}件",
        "",
        "| 公開日 | note ID | 記事 | 文脈記述 | 個別カード・強度監査 | 公開状態 | note |",
        "|---|---|---|---|---|---|---|",
    ]
    for article in articles:
        url_cell = (
            f"[公開本文]({article['note_url']})" if article["note_url"] else "-"
        )
        lines.append(
            f"| {article['published_at']} | `{article['id']}` | "
            f"{article_cell(article)} | {analysis_cell(article)} | "
            f"{card_cell(article)} | {article['public_status']} | {url_cell} |"
        )
    if not articles:
        lines.append("| - | - | まだ登録されていません | - | - | - | - |")
    INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    write_index()
    print(f"wrote {INDEX_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
