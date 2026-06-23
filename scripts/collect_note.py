#!/usr/bin/env python3
"""Collect recent note articles and create source snapshots plus analysis stubs.

This is intentionally a thin collector. It discovers article URLs from note RSS,
extracts readable text from each public page, and creates unreviewed article cards.
It does not classify or interpret the articles.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_markdown

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "sources" / "note"
CARD_DIR = ROOT / "articles" / "cards"
INDEX_PATH = ROOT / "articles" / "INDEX.md"
START_MARKER = "<!-- AUTO-GENERATED-ARTICLES:START -->"
END_MARKER = "<!-- AUTO-GENERATED-ARTICLES:END -->"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/149.0 Safari/537.36 ContextManagementBot/0.1"
)


@dataclass(frozen=True)
class Article:
    note_id: str
    title: str
    url: str
    published_at: str
    body_markdown: str
    extraction_method: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        default="https://note.com/shirokuma1970",
        help="note creator profile URL",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="number of recent RSS entries to process; 0 means all entries in the feed",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace existing source snapshots and unreviewed cards",
    )
    return parser.parse_args()


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def fetch(session: requests.Session, url: str) -> str:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def walk_json(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def extract_from_json_ld(soup: BeautifulSoup) -> tuple[str, str] | None:
    for script in soup.select('script[type="application/ld+json"]'):
        raw = script.string or script.get_text(strip=True)
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for item in walk_json(data):
            body = item.get("articleBody")
            if isinstance(body, str) and len(body.strip()) >= 100:
                return body.strip(), "json-ld:articleBody"
    return None


def cleanup_container(container: Any) -> str:
    for tag in container.select(
        "script, style, noscript, nav, header, footer, button, svg, form, aside"
    ):
        tag.decompose()
    markdown = html_to_markdown(str(container), heading_style="ATX")
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    return markdown.strip()


def extract_body(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    json_ld = extract_from_json_ld(soup)
    if json_ld:
        return json_ld

    selectors = (
        '[data-testid="note-content"]',
        ".note-common-styles__textnote-body",
        ".p-article__content",
        "article",
        "main",
    )
    for selector in selectors:
        container = soup.select_one(selector)
        if container is None:
            continue
        markdown = cleanup_container(container)
        if len(markdown) >= 100:
            return markdown, f"css:{selector}"

    text = soup.get_text("\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text, "fallback:page-text"


def note_id_from_url(url: str) -> str:
    path_parts = [part for part in urlparse(url).path.split("/") if part]
    if "n" in path_parts:
        index = path_parts.index("n")
        if index + 1 < len(path_parts):
            return path_parts[index + 1]
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def feed_date(entry: Any) -> str:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        return datetime(*parsed[:6], tzinfo=timezone.utc).date().isoformat()
    return "unknown-date"


def collect_entries(profile: str, limit: int, session: requests.Session) -> list[Any]:
    feed_url = f"{profile.rstrip('/')}/rss"
    response = session.get(feed_url, timeout=30)
    response.raise_for_status()
    feed = feedparser.parse(response.content)
    if getattr(feed, "bozo", False) and not feed.entries:
        raise RuntimeError(f"RSS parse failed: {getattr(feed, 'bozo_exception', 'unknown')}")
    entries = list(feed.entries)
    return entries if limit == 0 else entries[:limit]


def build_article(entry: Any, session: requests.Session) -> Article:
    url = str(entry.get("link", "")).strip()
    if not url:
        raise ValueError("RSS entry has no link")
    html = fetch(session, url)
    body, method = extract_body(html)
    title = str(entry.get("title") or "無題").strip()
    return Article(
        note_id=note_id_from_url(url),
        title=title,
        url=url,
        published_at=feed_date(entry),
        body_markdown=body,
        extraction_method=method,
    )


def source_path(article: Article) -> Path:
    return SOURCE_DIR / f"{article.note_id}.md"


def card_path(article: Article) -> Path:
    safe_date = article.published_at if article.published_at != "unknown-date" else "undated"
    return CARD_DIR / f"{safe_date}-{article.note_id}.md"


def write_source(article: Article, overwrite: bool) -> bool:
    path = source_path(article)
    if path.exists() and not overwrite:
        return False
    digest = hashlib.sha256(article.body_markdown.encode("utf-8")).hexdigest()
    fetched_at = datetime.now(timezone.utc).isoformat()
    content = f"""---
note_id: {yaml_string(article.note_id)}
title: {yaml_string(article.title)}
note_url: {yaml_string(article.url)}
published_at: {yaml_string(article.published_at)}
fetched_at: {yaml_string(fetched_at)}
content_sha256: {yaml_string(digest)}
extraction_method: {yaml_string(article.extraction_method)}
---

# {article.title}

> 公開本文の正本：{article.url}
>
> このファイルは文脈解析用の取得時スナップショットです。

{article.body_markdown}
"""
    path.write_text(content, encoding="utf-8")
    return True


def card_status(path: Path) -> str | None:
    if not path.exists():
        return None
    head = path.read_text(encoding="utf-8")[:1500]
    match = re.search(r"^status:\s*([^\n]+)", head, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def write_card(article: Article, overwrite: bool) -> bool:
    path = card_path(article)
    existing_status = card_status(path)
    if path.exists() and (not overwrite or existing_status not in {"unreviewed", "proposed"}):
        return False
    relative_source = Path("../../sources/note") / f"{article.note_id}.md"
    content = f"""---
id: {yaml_string(article.note_id)}
title: {yaml_string(article.title)}
published_at: {yaml_string(article.published_at)}
note_url: {yaml_string(article.url)}
status: unreviewed
themes: []
concepts: []
related_articles: []
source_snapshot: {yaml_string(str(relative_source).replace('\\', '/'))}
---

# {article.title}

## 記事の位置づけ

未解析。

## 出発点となる問い

未解析。

## 中心命題

未解析。

## 論理の流れ

未解析。

## 以前の記事から維持したもの

未解析。

## この記事で新しく押し広げたもの

未解析。

## 文脈差分

未解析。

## 棄却した読み

本文だけで確認できない場合は、執筆時の会話記録を参照する。

## 次に残った問い

未解析。

## 関連記事

未解析。

## 解析上の不確実性

未解析。

## 参照

- [公開本文をnoteで読む]({article.url})
- [取得時スナップショット]({relative_source.as_posix()})
"""
    path.write_text(content, encoding="utf-8")
    return True


def parse_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        try:
            parsed = json.loads(value)
            if isinstance(parsed, str):
                value = parsed
        except json.JSONDecodeError:
            pass
        result[key.strip()] = value
    return result


def update_index() -> None:
    rows: list[tuple[str, str, str, str, str]] = []
    for path in CARD_DIR.glob("*.md"):
        data = parse_front_matter(path)
        rows.append(
            (
                data.get("published_at", ""),
                data.get("title", path.stem),
                data.get("status", "unknown"),
                path.relative_to(INDEX_PATH.parent).as_posix(),
                data.get("note_url", ""),
            )
        )
    rows.sort(key=lambda row: row[0], reverse=True)

    generated = [
        START_MARKER,
        "| 公開日 | 記事 | 状態 | note |",
        "|---|---|---|---|",
    ]
    for published_at, title, status, relative_path, url in rows:
        escaped_title = title.replace("|", "\\|")
        generated.append(
            f"| {published_at} | [{escaped_title}]({relative_path}) | {status} | [公開本文]({url}) |"
        )
    if not rows:
        generated.append("| - | まだ登録されていません | - | - |")
    generated.append(END_MARKER)
    block = "\n".join(generated)

    current = INDEX_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        flags=re.DOTALL,
    )
    if pattern.search(current):
        updated = pattern.sub(block, current)
    else:
        updated = current.rstrip() + "\n\n" + block + "\n"
    INDEX_PATH.write_text(updated, encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.limit < 0:
        print("--limit must be 0 or greater", file=sys.stderr)
        return 2

    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    CARD_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "ja,en;q=0.8"})

    entries = collect_entries(args.profile, args.limit, session)
    if not entries:
        print("No RSS entries found", file=sys.stderr)
        return 1

    failures = 0
    changed_sources = 0
    changed_cards = 0
    for entry in entries:
        try:
            article = build_article(entry, session)
            changed_sources += int(write_source(article, args.overwrite))
            changed_cards += int(write_card(article, args.overwrite))
            print(f"collected: {article.published_at} {article.title}")
        except Exception as exc:  # continue collecting the remaining entries
            failures += 1
            print(f"failed: {entry.get('link', '(no link)')}: {exc}", file=sys.stderr)

    update_index()
    print(
        f"done: entries={len(entries)} sources_changed={changed_sources} "
        f"cards_changed={changed_cards} failures={failures}"
    )
    return 1 if failures == len(entries) else 0


if __name__ == "__main__":
    raise SystemExit(main())
