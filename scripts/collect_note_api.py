#!/usr/bin/env python3
"""Discover all public note articles through the creator contents endpoint.

The existing collect_note.py remains responsible for article-page extraction,
source snapshots, card stubs, and index generation. This file only extends URL
discovery beyond the small RSS window. If the endpoint changes, it falls back
to RSS and records the failure in sources/note/discovery.json.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

import collect_note as base

DIAGNOSTIC_PATH = base.SOURCE_DIR / "discovery.json"


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
        default=0,
        help="maximum articles to process; 0 means all discovered articles",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=100,
        help="safety limit for creator API pagination",
    )
    parser.add_argument(
        "--request-interval",
        type=float,
        default=0.35,
        help="seconds between article-page requests",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace existing source snapshots and unreviewed cards",
    )
    return parser.parse_args()


def creator_name(profile: str) -> str:
    parts = [part for part in urlparse(profile).path.split("/") if part]
    if not parts:
        raise ValueError(f"Cannot determine creator from profile URL: {profile}")
    return parts[-1]


def nested_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nested_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from nested_dicts(child)


def find_contents(payload: Any) -> list[dict[str, Any]]:
    preferred: list[Any] = []
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict):
            preferred.extend([data.get("contents"), data.get("notes"), data.get("items")])
        preferred.extend([payload.get("contents"), payload.get("notes"), payload.get("items")])

    for candidate in preferred:
        if isinstance(candidate, list) and all(isinstance(item, dict) for item in candidate):
            return candidate

    for item in nested_dicts(payload):
        for value in item.values():
            if not isinstance(value, list) or not value:
                continue
            if not all(isinstance(row, dict) for row in value):
                continue
            keys = set().union(*(row.keys() for row in value))
            if keys.intersection({"key", "noteUrl", "note_url"}) and keys.intersection(
                {"name", "title"}
            ):
                return value
    return []


def find_last_page_flag(payload: Any) -> bool | None:
    for item in nested_dicts(payload):
        for key in ("isLastPage", "is_last_page", "lastPage", "last_page"):
            value = item.get(key)
            if isinstance(value, bool):
                return value
    return None


def first_string(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def normalize_date(value: str) -> str:
    if len(value) >= 10:
        candidate = value[:10]
        try:
            datetime.strptime(candidate, "%Y-%m-%d")
            return candidate
        except ValueError:
            pass
    return "unknown-date"


def api_item_to_entry(item: dict[str, Any], profile: str) -> dict[str, Any] | None:
    key = first_string(item, "key", "noteKey", "note_key")
    url = first_string(item, "noteUrl", "note_url", "url")
    if url.startswith("/"):
        url = f"https://note.com{url}"
    if not url and key:
        url = f"{profile.rstrip('/')}/n/{key}"
    if "/n/" not in url:
        return None

    title = first_string(item, "name", "title") or "無題"
    published = first_string(
        item,
        "publishAt",
        "publishedAt",
        "published_at",
        "createdAt",
        "created_at",
    )
    date = normalize_date(published)
    parsed = None
    if date != "unknown-date":
        parsed = time.strptime(date, "%Y-%m-%d")

    return {
        "link": url,
        "title": title,
        "published_parsed": parsed,
        "api_raw_date": published,
    }


def discover_from_api(
    profile: str, session: requests.Session, max_pages: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    creator = creator_name(profile)
    endpoint = f"https://note.com/api/v2/creators/{creator}/contents"
    entries: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    page_stats: list[dict[str, Any]] = []

    for page in range(1, max_pages + 1):
        response = session.get(endpoint, params={"kind": "note", "page": page}, timeout=30)
        response.raise_for_status()
        payload = response.json()
        contents = find_contents(payload)
        last_page = find_last_page_flag(payload)
        new_count = 0

        for item in contents:
            entry = api_item_to_entry(item, profile)
            if entry is None or entry["link"] in seen_urls:
                continue
            seen_urls.add(entry["link"])
            entries.append(entry)
            new_count += 1

        page_stats.append(
            {
                "page": page,
                "items_found": len(contents),
                "new_urls": new_count,
                "is_last_page": last_page,
                "status_code": response.status_code,
            }
        )

        if last_page is True or not contents or new_count == 0:
            break

    if not entries:
        raise RuntimeError("Creator contents endpoint returned no article URLs")

    return entries, {
        "method": "creator-api",
        "endpoint": endpoint,
        "pages": page_stats,
        "discovered_count": len(entries),
    }


def discover_from_rss(
    profile: str, session: requests.Session, limit: int
) -> tuple[list[Any], dict[str, Any]]:
    entries = base.collect_entries(profile, limit, session)
    return entries, {
        "method": "rss-fallback",
        "endpoint": f"{profile.rstrip('/')}/rss",
        "discovered_count": len(entries),
    }


def write_diagnostic(data: dict[str, Any]) -> None:
    base.SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        **data,
    }
    DIAGNOSTIC_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    args = parse_args()
    if args.limit < 0 or args.max_pages < 1 or args.request_interval < 0:
        print("Invalid numeric argument", file=sys.stderr)
        return 2

    base.SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    base.CARD_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update(
        {"User-Agent": base.USER_AGENT, "Accept-Language": "ja,en;q=0.8"}
    )

    diagnostic: dict[str, Any]
    try:
        entries, diagnostic = discover_from_api(args.profile, session, args.max_pages)
    except Exception as exc:
        print(f"creator API discovery failed; falling back to RSS: {exc}", file=sys.stderr)
        entries, diagnostic = discover_from_rss(args.profile, session, args.limit)
        diagnostic["api_error"] = f"{type(exc).__name__}: {exc}"

    if args.limit > 0:
        entries = entries[: args.limit]
    diagnostic["processed_count"] = len(entries)

    failures = 0
    changed_sources = 0
    changed_cards = 0
    for index, entry in enumerate(entries):
        try:
            article = base.build_article(entry, session)
            changed_sources += int(base.write_source(article, args.overwrite))
            changed_cards += int(base.write_card(article, args.overwrite))
            print(f"collected: {article.published_at} {article.title}")
        except Exception as exc:
            failures += 1
            link = entry.get("link", "(no link)") if hasattr(entry, "get") else "(unknown)"
            print(f"failed: {link}: {exc}", file=sys.stderr)
        if index + 1 < len(entries) and args.request_interval:
            time.sleep(args.request_interval)

    diagnostic.update(
        {
            "source_files_changed": changed_sources,
            "card_files_changed": changed_cards,
            "failures": failures,
        }
    )
    write_diagnostic(diagnostic)
    base.update_index()

    print(
        f"done: discovered={diagnostic.get('discovered_count')} processed={len(entries)} "
        f"sources_changed={changed_sources} cards_changed={changed_cards} failures={failures}"
    )
    return 1 if entries and failures == len(entries) else 0


if __name__ == "__main__":
    raise SystemExit(main())
