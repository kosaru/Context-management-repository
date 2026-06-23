#!/usr/bin/env python3
"""Normalize a note.com WordPress-style XML export into JSONL corpus files.

The raw XML is treated as an import input and is not copied into the repository.
Only published posts are emitted by default.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any

from markdownify import markdownify as to_markdown

NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "wp": "http://wordpress.org/export/1.2/",
}


def normalize_markdown(html: str) -> str:
    text = to_markdown(html, heading_style="ATX", bullets="-").strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return unicodedata.normalize("NFC", text)


def parse_export(xml_path: Path, published_only: bool = True) -> list[dict[str, Any]]:
    root = ET.parse(xml_path).getroot()
    channel = root.find("channel")
    if channel is None:
        raise ValueError("RSS channel element was not found")

    articles: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for item in channel.findall("item"):
        note_id = (item.findtext("guid") or "").strip()
        title = (item.findtext("title") or "").strip()
        url = (item.findtext("link") or "").strip()
        status = (item.findtext("wp:status", namespaces=NS) or "").strip()
        post_type = (item.findtext("wp:post_type", namespaces=NS) or "").strip()
        published_at = (item.findtext("wp:post_date", namespaces=NS) or "").strip()
        updated_at = (item.findtext("wp:post_modified", namespaces=NS) or "").strip()
        html = item.findtext("content:encoded", namespaces=NS) or ""

        if post_type != "post":
            continue
        if published_only and status != "publish":
            continue
        if not note_id:
            raise ValueError(f"Article without note ID: {title!r}")
        if note_id in seen_ids:
            raise ValueError(f"Duplicate note ID: {note_id}")
        seen_ids.add(note_id)

        body = normalize_markdown(html)
        articles.append(
            {
                "note_id": note_id,
                "title": title,
                "note_url": url,
                "published_at": published_at,
                "updated_at": updated_at,
                "status": status,
                "post_type": post_type,
                "content_hash": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "image_count": html.count("<img"),
                "body_markdown": body,
            }
        )

    articles.sort(key=lambda a: (a["published_at"], a["note_id"]))
    return articles


def write_corpus(articles: list[dict[str, Any]], output_dir: Path, max_bytes: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    by_month: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for article in articles:
        by_month[article["published_at"][:7]].append(article)

    files: list[dict[str, Any]] = []
    for month in sorted(by_month):
        part = 1
        lines: list[str] = []
        size = 0

        def flush() -> None:
            nonlocal part, lines, size
            if not lines:
                return
            filename = f"{month}-part{part:02d}.jsonl"
            content = "".join(lines)
            (output_dir / filename).write_text(content, encoding="utf-8")
            files.append(
                {
                    "path": filename,
                    "article_count": len(lines),
                    "bytes": len(content.encode("utf-8")),
                }
            )
            part += 1
            lines = []
            size = 0

        for article in by_month[month]:
            line = json.dumps(article, ensure_ascii=False, separators=(",", ":")) + "\n"
            line_size = len(line.encode("utf-8"))
            if lines and size + line_size > max_bytes:
                flush()
            lines.append(line)
            size += line_size
        flush()

    manifest_articles = [
        {key: value for key, value in article.items() if key != "body_markdown"}
        for article in articles
    ]
    manifest = {
        "article_count": len(articles),
        "first_published_at": articles[0]["published_at"] if articles else None,
        "last_published_at": articles[-1]["published_at"] if articles else None,
        "files": files,
        "articles": manifest_articles,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("xml", type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("sources/note/export"),
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=350_000,
        help="Approximate maximum size of one JSONL part.",
    )
    parser.add_argument(
        "--include-non-public",
        action="store_true",
        help="Include non-published posts. Do not use without reviewing privacy implications.",
    )
    args = parser.parse_args()

    if not args.xml.is_file():
        parser.error(f"XML file not found: {args.xml}")

    articles = parse_export(
        args.xml,
        published_only=not args.include_non_public,
    )
    write_corpus(articles, args.output_dir, args.max_bytes)
    print(f"Exported {len(articles)} articles to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
