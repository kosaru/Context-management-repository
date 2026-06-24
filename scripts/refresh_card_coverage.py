#!/usr/bin/env python3
"""Promote coverage references when a detailed card is added.

This script never advances the accepted body hash. It changes only the analysis
reference, and only when:

- the article is already covered;
- a canonical card is analyzed/reviewed; and
- the catalog body hash still equals the previously accepted coverage hash.

If the public body changed after coverage, the review queue remains responsible
for deciding whether the new body can be accepted.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import collect_note as base
import note_index

CATALOG_PATH = base.SOURCE_DIR / "catalog.json"
COVERAGE_PATH = base.ROOT / "analysis" / "COVERAGE.json"
DIAGNOSTIC_PATH = base.SOURCE_DIR / "card-coverage-refresh.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    catalog = load_json(CATALOG_PATH)
    coverage = load_json(COVERAGE_PATH)
    catalog_articles = catalog.get("articles", {})
    entries = coverage.get("articles", {})
    if not isinstance(catalog_articles, dict) or not isinstance(entries, dict):
        raise ValueError("catalog/coverage articles must be objects")

    promoted: list[dict[str, str]] = []
    skipped_changed_body: list[dict[str, str]] = []

    for note_id, entry in entries.items():
        if not isinstance(entry, dict) or entry.get("analysis_state") != "covered":
            continue
        card = note_index.canonical_card(note_id)
        if not card or card.get("status") not in {"analyzed", "reviewed"}:
            continue
        if entry.get("coverage_type") == "individual_card" and entry.get("analysis_ref"):
            continue

        current = catalog_articles.get(note_id, {})
        current_hash = str(current.get("content_hash") or "") if isinstance(current, dict) else ""
        covered_hash = str(entry.get("covered_content_hash") or "")
        if not current_hash or current_hash != covered_hash:
            skipped_changed_body.append(
                {
                    "note_id": note_id,
                    "card_path": str(card.get("relative_path") or ""),
                    "current_hash": current_hash,
                    "covered_hash": covered_hash,
                }
            )
            continue

        previous_ref = str(entry.get("analysis_ref") or "")
        card_ref = f"articles/{card['relative_path']}"
        entry.update(
            {
                "coverage_type": "individual_card",
                "analysis_unit": "individual_card",
                "analysis_label": "個別記事カード",
                "analysis_ref": card_ref,
            }
        )
        promoted.append(
            {
                "note_id": note_id,
                "previous_analysis_ref": previous_ref,
                "analysis_ref": card_ref,
            }
        )

    now = utc_now()
    if promoted:
        coverage["updated_at"] = now
        coverage["articles"] = dict(sorted(entries.items()))
        write_json(COVERAGE_PATH, coverage)

    write_json(
        DIAGNOSTIC_PATH,
        {
            "recorded_at": now,
            "promoted_count": len(promoted),
            "promoted": promoted,
            "skipped_changed_body_count": len(skipped_changed_body),
            "skipped_changed_body": skipped_changed_body,
        },
    )
    print(
        f"card coverage refresh: promoted={len(promoted)} "
        f"skipped_changed_body={len(skipped_changed_body)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
