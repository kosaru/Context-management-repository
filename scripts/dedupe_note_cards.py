#!/usr/bin/env python3
"""Remove auto-generated duplicate note cards that share the same note ID.

The collector may observe a different calendar date from an existing card.
The note ID is the primary key; an analyzed card always wins over an
automatically generated unreviewed stub. Protected duplicates are reported
and left untouched for human review.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import collect_note as base
import note_index

STATUS_RANK = note_index.STATUS_RANK
DIAGNOSTIC_PATH = base.SOURCE_DIR / "card-deduplication.json"


def card_info(path: Path) -> dict[str, str]:
    data = base.parse_front_matter(path)
    return {
        "id": data.get("id", ""),
        "status": data.get("status", "unknown"),
        "published_at": data.get("published_at", ""),
        "path": path.as_posix(),
    }


def choose_canonical(items: list[dict[str, str]]) -> dict[str, str]:
    return max(
        items,
        key=lambda item: (
            STATUS_RANK.get(item["status"], 0),
            bool(item["published_at"]),
            item["path"],
        ),
    )


def main() -> int:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    missing_id: list[str] = []

    for path in sorted(base.CARD_DIR.glob("*.md")):
        info = card_info(path)
        if not info["id"]:
            missing_id.append(path.as_posix())
            continue
        grouped[info["id"]].append(info)

    deleted: list[dict[str, str]] = []
    ambiguous: list[dict[str, object]] = []

    for note_id, items in sorted(grouped.items()):
        if len(items) < 2:
            continue

        canonical = choose_canonical(items)
        protected = [
            item
            for item in items
            if item["path"] != canonical["path"]
            and STATUS_RANK.get(item["status"], 0) >= STATUS_RANK["proposed"]
        ]
        if protected:
            ambiguous.append(
                {
                    "note_id": note_id,
                    "canonical": canonical,
                    "protected_duplicates": protected,
                }
            )

        for item in items:
            if item["path"] == canonical["path"]:
                continue
            if item["status"] != "unreviewed":
                continue
            path = Path(item["path"])
            path.unlink()
            deleted.append(
                {
                    "note_id": note_id,
                    "deleted": item,
                    "kept": canonical,
                }
            )

    note_index.write_index()
    diagnostic = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "deleted_count": len(deleted),
        "deleted": deleted,
        "ambiguous_count": len(ambiguous),
        "ambiguous": ambiguous,
        "missing_id": missing_id,
    }
    DIAGNOSTIC_PATH.write_text(
        json.dumps(diagnostic, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"dedupe: deleted={len(deleted)} ambiguous={len(ambiguous)} "
        f"missing_id={len(missing_id)}"
    )
    return 1 if ambiguous else 0


if __name__ == "__main__":
    raise SystemExit(main())
