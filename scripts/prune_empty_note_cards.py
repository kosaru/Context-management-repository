#!/usr/bin/env python3
"""Delete empty auto-generated note cards already covered elsewhere.

A card is removed only when all of the following are true:
- status is ``unreviewed``;
- coverage state is ``covered``;
- coverage type is not ``individual_card``;
- the body still matches the untouched placeholder structure.

Any unreviewed card containing real analysis is preserved.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import collect_note as base
import note_index

DIAGNOSTIC_PATH = base.SOURCE_DIR / "placeholder-card-pruning.json"

REQUIRED_PLACEHOLDER_BLOCKS = (
    "## 記事の位置づけ\n\n未解析。",
    "## 出発点となる問い\n\n未解析。",
    "## 中心命題\n\n未解析。",
    "## 論理の流れ\n\n未解析。",
    "## 以前の記事から維持したもの\n\n未解析。",
    "## この記事で新しく押し広げたもの\n\n未解析。",
    "## 文脈差分\n\n未解析。",
    "## 棄却した読み\n\n本文だけで確認できない場合は、執筆時の会話記録を参照する。",
    "## 次に残った問い\n\n未解析。",
    "## 関連記事\n\n未解析。",
    "## 解析上の不確実性\n\n未解析。",
)


def is_empty_placeholder(path: Path) -> bool:
    data = base.parse_front_matter(path)
    if data.get("status") != "unreviewed":
        return False
    text = path.read_text(encoding="utf-8")
    return all(block in text for block in REQUIRED_PLACEHOLDER_BLOCKS)


def write_diagnostic(payload: dict[str, Any]) -> None:
    DIAGNOSTIC_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    coverage = note_index.load_articles(note_index.COVERAGE_PATH)
    deleted: list[dict[str, str]] = []
    preserved: list[dict[str, str]] = []

    for path in sorted(base.CARD_DIR.glob("*.md")):
        data = base.parse_front_matter(path)
        note_id = data.get("id", "")
        if not note_id or data.get("status") != "unreviewed":
            continue

        covered = coverage.get(note_id, {})
        covered_elsewhere = (
            isinstance(covered, dict)
            and covered.get("analysis_state") == "covered"
            and covered.get("coverage_type") != "individual_card"
        )
        if not covered_elsewhere:
            preserved.append(
                {
                    "note_id": note_id,
                    "path": path.relative_to(base.ROOT).as_posix(),
                    "reason": "not_covered_elsewhere",
                }
            )
            continue

        if not is_empty_placeholder(path):
            preserved.append(
                {
                    "note_id": note_id,
                    "path": path.relative_to(base.ROOT).as_posix(),
                    "reason": "contains_non_placeholder_content",
                }
            )
            continue

        path.unlink()
        deleted.append(
            {
                "note_id": note_id,
                "path": path.relative_to(base.ROOT).as_posix(),
                "analysis_ref": str(covered.get("analysis_ref") or ""),
            }
        )

    note_index.write_index()
    write_diagnostic(
        {
            "deleted_count": len(deleted),
            "deleted": deleted,
            "preserved_unreviewed_count": len(preserved),
            "preserved_unreviewed": preserved,
        }
    )
    print(
        f"placeholder cards: deleted={len(deleted)} "
        f"preserved_unreviewed={len(preserved)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
