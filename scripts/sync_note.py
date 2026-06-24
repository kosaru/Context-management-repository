#!/usr/bin/env python3
"""Incrementally synchronize public note articles into the context repository.

The note ID is the primary key. The collector keeps public-page snapshots,
creates a pending card only for a previously unseen or currently unassigned
article, records metadata/body changes, and never rewrites analyzed cards.
Articles already covered by a phase bundle or cross index do not need empty
individual-card placeholders.

Normal runs fetch article pages only when:
- the note ID is new,
- the source snapshot is missing,
- title/published/updated metadata changed, or
- --verify-all is requested.

A complete creator-API discovery may mark previously known articles as
missing-from-public-index, but it never deletes snapshots or analyzed cards.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

import collect_note as base
import collect_note_api as discovery
import note_index

CATALOG_PATH = base.SOURCE_DIR / "catalog.json"
CHANGE_LOG_PATH = base.SOURCE_DIR / "change-log.jsonl"
LAST_SYNC_PATH = base.SOURCE_DIR / "last-sync.json"
SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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
        help="maximum discovered articles to process; 0 means all",
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
        "--verify-all",
        action="store_true",
        help="fetch every discovered article page and compare the body hash",
    )
    return parser.parse_args()


def load_catalog() -> dict[str, Any]:
    if not CATALOG_PATH.exists():
        return {
            "schema_version": SCHEMA_VERSION,
            "updated_at": "",
            "articles": {},
        }
    payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("articles"), dict):
        raise ValueError(f"Invalid catalog structure: {CATALOG_PATH}")
    payload.setdefault("schema_version", SCHEMA_VERSION)
    payload.setdefault("updated_at", "")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def append_events(events: list[dict[str, Any]]) -> None:
    if not events:
        return
    CHANGE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CHANGE_LOG_PATH.open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def source_record(path: Path) -> dict[str, str]:
    data = base.parse_front_matter(path)
    return {
        "note_id": data.get("note_id", ""),
        "title": data.get("title", ""),
        "note_url": data.get("note_url", ""),
        "published_at": data.get("published_at", ""),
        "fetched_at": data.get("fetched_at", ""),
        "content_hash": data.get("content_sha256", ""),
        "snapshot_path": path.relative_to(base.ROOT).as_posix(),
    }


def bootstrap_catalog(catalog: dict[str, Any], now: str) -> int:
    """Populate missing catalog records from committed snapshots/cards."""
    articles: dict[str, dict[str, Any]] = catalog["articles"]
    added = 0
    for path in sorted(base.SOURCE_DIR.glob("*.md")):
        record = source_record(path)
        note_id = record["note_id"]
        if not note_id or note_id in articles:
            continue
        card = note_index.canonical_card(note_id)
        coverage = note_index.coverage_for(note_id) or {}
        first_seen = record["fetched_at"] or now
        articles[note_id] = {
            "note_id": note_id,
            "title": record["title"],
            "note_url": record["note_url"],
            "published_at": record["published_at"],
            "source_updated_at": "",
            "first_seen_at": first_seen,
            "last_seen_at": first_seen,
            "last_checked_at": record["fetched_at"],
            "content_hash": record["content_hash"],
            "public_status": "public",
            "snapshot_path": record["snapshot_path"],
            "card_path": card["relative_path"] if card else "",
            "analysis_status": (
                card["status"]
                if card
                else str(coverage.get("analysis_state") or "missing")
            ),
        }
        added += 1
    return added


def entry_metadata(entry: Any) -> dict[str, str]:
    url = str(entry.get("link", "")).strip()
    note_id = str(entry.get("note_id") or base.note_id_from_url(url)).strip()
    title = str(entry.get("title") or "無題").strip()
    published_at = base.feed_date(entry)
    source_updated_at = str(entry.get("api_updated_at") or "").strip()
    return {
        "note_id": note_id,
        "title": title,
        "note_url": url,
        "published_at": published_at,
        "source_updated_at": source_updated_at,
    }


def metadata_changes(
    existing: dict[str, Any] | None,
    metadata: dict[str, str],
) -> dict[str, dict[str, str]]:
    if existing is None:
        return {}
    changes: dict[str, dict[str, str]] = {}
    for key in ("title", "note_url", "published_at"):
        before = str(existing.get(key) or "")
        after = metadata[key]
        if after and before != after:
            changes[key] = {"before": before, "after": after}
    previous_updated = str(existing.get("source_updated_at") or "")
    current_updated = metadata["source_updated_at"]
    if previous_updated and current_updated and previous_updated != current_updated:
        changes["source_updated_at"] = {
            "before": previous_updated,
            "after": current_updated,
        }
    return changes


def source_hash(article: base.Article) -> str:
    return hashlib.sha256(article.body_markdown.encode("utf-8")).hexdigest()


def ensure_card(article: base.Article) -> tuple[str, str, bool]:
    """Create an individual card only when coverage does not already exist."""
    existing = note_index.canonical_card(article.note_id)
    if existing:
        return existing["relative_path"], existing["status"], False

    coverage = note_index.coverage_for(article.note_id) or {}
    if (
        coverage.get("analysis_state") == "covered"
        and coverage.get("coverage_type") != "individual_card"
    ):
        return "", str(coverage.get("analysis_state") or "covered"), False

    created = base.write_card(article, overwrite=False)
    card = note_index.canonical_card(article.note_id)
    if card is None:
        raise RuntimeError(f"Card creation failed for {article.note_id}")
    return card["relative_path"], card["status"], created


def complete_api_discovery(diagnostic: dict[str, Any], limit: int) -> bool:
    return (
        diagnostic.get("method") == "creator-api"
        and bool(diagnostic.get("complete"))
        and limit == 0
    )


def main() -> int:
    args = parse_args()
    if args.limit < 0 or args.max_pages < 1 or args.request_interval < 0:
        print("Invalid numeric argument", file=sys.stderr)
        return 2

    now = utc_now()
    base.SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    base.CARD_DIR.mkdir(parents=True, exist_ok=True)

    catalog = load_catalog()
    bootstrapped = bootstrap_catalog(catalog, now)
    articles: dict[str, dict[str, Any]] = catalog["articles"]

    session = requests.Session()
    session.headers.update(
        {"User-Agent": base.USER_AGENT, "Accept-Language": "ja,en;q=0.8"}
    )

    try:
        entries, diagnostic = discovery.discover_from_api(
            args.profile, session, args.max_pages
        )
    except Exception as exc:
        print(f"creator API discovery failed; falling back to RSS: {exc}", file=sys.stderr)
        entries, diagnostic = discovery.discover_from_rss(
            args.profile, session, args.limit
        )
        diagnostic["api_error"] = f"{type(exc).__name__}: {exc}"
        diagnostic["complete"] = False

    if args.limit > 0:
        entries = entries[: args.limit]

    seen_ids: set[str] = set()
    events: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    fetched_count = 0
    source_changed_count = 0
    new_card_count = 0
    metadata_change_count = 0

    for index, entry in enumerate(entries):
        metadata = entry_metadata(entry)
        note_id = metadata["note_id"]
        if not note_id:
            failures.append(
                {"note_id": "", "url": metadata["note_url"], "error": "missing note ID"}
            )
            continue
        seen_ids.add(note_id)
        existing = articles.get(note_id)
        changes = metadata_changes(existing, metadata)
        source_path = base.SOURCE_DIR / f"{note_id}.md"
        needs_fetch = (
            existing is None
            or not source_path.exists()
            or bool(changes)
            or args.verify_all
        )

        if not needs_fetch:
            existing["last_seen_at"] = now
            existing["public_status"] = "public"
            if metadata["source_updated_at"] and not existing.get("source_updated_at"):
                existing["source_updated_at"] = metadata["source_updated_at"]
            continue

        try:
            article = base.build_article(entry, session)
            fetched_count += 1
            current_hash = source_hash(article)
            previous_hash = str(existing.get("content_hash") or "") if existing else ""
            body_changed = previous_hash != current_hash
            is_new = existing is None

            if is_new or body_changed or changes or not source_path.exists():
                base.write_source(article, overwrite=True)

            card_path, analysis_status, card_created = ensure_card(article)
            new_card_count += int(card_created)

            if is_new:
                event_type = "new"
            elif body_changed:
                event_type = "body_changed"
            elif changes:
                event_type = "metadata_changed"
            else:
                event_type = "verified_unchanged"

            if event_type != "verified_unchanged":
                events.append(
                    {
                        "recorded_at": now,
                        "event": event_type,
                        "note_id": note_id,
                        "note_url": metadata["note_url"],
                        "metadata_changes": changes,
                        "content_hash_before": previous_hash,
                        "content_hash_after": current_hash,
                        "card_created": card_created,
                        "analysis_status": analysis_status,
                    }
                )

            first_seen = str(existing.get("first_seen_at") or now) if existing else now
            articles[note_id] = {
                "note_id": note_id,
                "title": article.title,
                "note_url": article.url,
                "published_at": article.published_at,
                "source_updated_at": metadata["source_updated_at"],
                "first_seen_at": first_seen,
                "last_seen_at": now,
                "last_checked_at": now,
                "content_hash": current_hash,
                "public_status": "public",
                "snapshot_path": source_path.relative_to(base.ROOT).as_posix(),
                "card_path": card_path,
                "analysis_status": analysis_status,
            }
            source_changed_count += int(is_new or body_changed)
            metadata_change_count += int(bool(changes) and not body_changed)
        except Exception as exc:
            failures.append(
                {
                    "note_id": note_id,
                    "url": metadata["note_url"],
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            print(f"failed: {metadata['note_url']}: {exc}", file=sys.stderr)

        if index + 1 < len(entries) and args.request_interval and needs_fetch:
            time.sleep(args.request_interval)

    missing_count = 0
    if complete_api_discovery(diagnostic, args.limit):
        for note_id, record in articles.items():
            if note_id in seen_ids:
                continue
            if record.get("public_status") == "missing_from_public_index":
                continue
            previous_status = str(record.get("public_status") or "")
            record["public_status"] = "missing_from_public_index"
            record["last_status_change_at"] = now
            missing_count += 1
            events.append(
                {
                    "recorded_at": now,
                    "event": "missing_from_public_index",
                    "note_id": note_id,
                    "note_url": record.get("note_url", ""),
                    "public_status_before": previous_status,
                    "public_status_after": "missing_from_public_index",
                }
            )

    catalog["schema_version"] = SCHEMA_VERSION
    catalog["updated_at"] = now
    catalog["articles"] = dict(sorted(articles.items()))
    write_json(CATALOG_PATH, catalog)
    append_events(events)
    note_index.write_index()

    report = {
        "recorded_at": now,
        "profile": args.profile,
        "discovery": diagnostic,
        "complete_discovery": complete_api_discovery(diagnostic, args.limit),
        "verify_all": args.verify_all,
        "limit": args.limit,
        "bootstrapped_catalog_records": bootstrapped,
        "discovered_count": len(entries),
        "seen_note_ids": len(seen_ids),
        "fetched_count": fetched_count,
        "source_changed_count": source_changed_count,
        "metadata_change_count": metadata_change_count,
        "new_card_count": new_card_count,
        "missing_from_public_index_count": missing_count,
        "events_written": len(events),
        "failure_count": len(failures),
        "failures": failures,
    }
    write_json(LAST_SYNC_PATH, report)
    discovery.write_diagnostic({**diagnostic, "sync_report": report})

    print(
        "sync complete: "
        f"discovered={len(entries)} fetched={fetched_count} "
        f"source_changed={source_changed_count} new_cards={new_card_count} "
        f"missing={missing_count} failures={len(failures)}"
    )
    return 1 if entries and len(failures) == len(entries) else 0


if __name__ == "__main__":
    raise SystemExit(main())
