#!/usr/bin/env python3
"""Protect the initial analyzed corpus from automatic future assignment.

The first run records the current coverage note IDs as the baseline corpus.
On later runs, entries outside that baseline that were automatically marked
covered in the same run are reset to pending. This prevents a newly discovered,
backdated article from being absorbed into an old phase merely because its
published date falls inside that phase range.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import collect_note as base

COVERAGE_PATH = base.ROOT / "analysis" / "COVERAGE.json"
BASELINE_PATH = base.ROOT / "analysis" / "BASELINE_NOTE_IDS.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    coverage = load_json(COVERAGE_PATH)
    articles = coverage.get("articles")
    if not isinstance(articles, dict):
        raise ValueError("COVERAGE.json articles must be an object")

    if not BASELINE_PATH.exists():
        baseline = {
            "created_at": utc_now(),
            "description": "Initial 351-article corpus analyzed through phase bundles or individual cards",
            "note_ids": sorted(articles),
        }
        write_json(BASELINE_PATH, baseline)
        print(f"baseline initialized: {len(articles)} note IDs")
        return 0

    baseline = load_json(BASELINE_PATH)
    baseline_ids_raw = baseline.get("note_ids")
    if not isinstance(baseline_ids_raw, list):
        raise ValueError("BASELINE_NOTE_IDS.json note_ids must be an array")
    baseline_ids = {str(value) for value in baseline_ids_raw}

    coverage_updated_at = str(coverage.get("updated_at") or "")
    reset_ids: list[str] = []
    for note_id, entry in articles.items():
        if note_id in baseline_ids or not isinstance(entry, dict):
            continue
        auto_covered_same_run = (
            entry.get("analysis_state") == "covered"
            and str(entry.get("covered_at") or "") == coverage_updated_at
            and not str(entry.get("role") or "").strip()
        )
        if not auto_covered_same_run:
            continue
        entry.update(
            {
                "analysis_state": "pending",
                "coverage_type": "unassigned",
                "analysis_unit": "unassigned",
                "analysis_label": "新着・未割り当て",
                "analysis_ref": "",
                "covered_content_hash": "",
                "covered_title": "",
                "covered_published_at": "",
                "covered_public_status": "",
                "covered_at": "",
            }
        )
        reset_ids.append(note_id)

    if reset_ids:
        coverage["updated_at"] = utc_now()
        write_json(COVERAGE_PATH, coverage)
    print(f"baseline protected: reset_to_pending={len(reset_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
