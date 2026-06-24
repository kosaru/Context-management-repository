#!/usr/bin/env python3
"""Maintain analysis coverage and generate a managed review queue.

Coverage is separate from card status. A note card may remain ``unreviewed`` at
the individual-card level while the article is already covered by a phase
bundle. Existing covered hashes are never advanced automatically when the
public body changes.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import collect_note as base
import note_index

CATALOG_PATH = base.SOURCE_DIR / "catalog.json"
COVERAGE_JSON_PATH = base.ROOT / "analysis" / "COVERAGE.json"
COVERAGE_MD_PATH = base.ROOT / "analysis" / "COVERAGE.md"
REVIEW_DIR = base.ROOT / "review"
REVIEW_INBOX_PATH = REVIEW_DIR / "INBOX.md"
SCHEMA_VERSION = 1

PHASES = (
    {
        "key": "phase_01",
        "label": "第1期：2026-01-24〜02-10",
        "start": date(2026, 1, 24),
        "end": date(2026, 2, 10),
        "ref": "analysis/PHASE_01_2026-01-24_TO_02-10.md",
    },
    {
        "key": "phase_02",
        "label": "第2期：2026-02-11〜02-27",
        "start": date(2026, 2, 11),
        "end": date(2026, 2, 27),
        "ref": "analysis/PHASE_02_2026-02-11_TO_02-27.md",
    },
    {
        "key": "phase_03",
        "label": "第3期：2026-03-02〜03-13",
        "start": date(2026, 3, 2),
        "end": date(2026, 3, 13),
        "ref": "analysis/PHASE_03_2026-03-02_TO_03-13.md",
    },
    {
        "key": "phase_04",
        "label": "第4期：2026-03-14〜03-21",
        "start": date(2026, 3, 14),
        "end": date(2026, 3, 21),
        "ref": "analysis/PHASE_04_2026-03-14_TO_03-21.md",
    },
    {
        "key": "phase_05",
        "label": "第5期：2026-03-24〜03-31",
        "start": date(2026, 3, 24),
        "end": date(2026, 3, 31),
        "ref": "analysis/PHASE_05_2026-03-24_TO_03-31.md",
    },
)

PHASE_06_IDS = {
    "nb5168c4aa573",
    "n93854c948132",
    "n3997928f2e69",
    "n0ce7ae17c98f",
    "nec0c450f182e",
    "n017615f6812a",
    "n4690a13cff98",
    "nc7ae2d738aca",
    "n394efbe5c522",
    "n735eb8a1538a",
    "nf31f8f683359",
    "n519ffb4416b0",
    "n57ddc084732b",
    "ne9a567f98d25",
    "n4e7fe52fe4e4",
    "n03f382a2f025",
}
PHASE_06_REF = "analysis/PHASE_06_2026-03-23_TO_05-01.md"
PHASE_06_LABEL = "第6期：2026-03-23〜05-01の残り16記事"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accept", metavar="NOTE_ID", help="mark one note as covered")
    parser.add_argument(
        "--analysis-ref",
        default="",
        help="repository-relative analysis reference used with --accept",
    )
    parser.add_argument(
        "--coverage-type",
        choices=("individual_card", "phase_bundle", "cross_index", "other"),
        default="individual_card",
        help="coverage type used with --accept",
    )
    parser.add_argument(
        "--role",
        default="",
        help="article role such as 初出, 修正, 統合稿, 反例, 分岐",
    )
    parser.add_argument("--defer", metavar="NOTE_ID", help="defer one review item")
    parser.add_argument("--defer-reason", default="", help="required with --defer")
    parser.add_argument("--recheck-after", default="", help="ISO date or free-text timing")
    parser.add_argument("--recheck-condition", default="", help="condition that reopens review")
    parser.add_argument("--reopen", metavar="NOTE_ID", help="return a deferred item to pending")
    return parser.parse_args()


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
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


def parse_date(value: str) -> date | None:
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def phase_for(note_id: str, published_at: str) -> tuple[str, str, str] | None:
    if note_id in PHASE_06_IDS:
        return "phase_06", PHASE_06_LABEL, PHASE_06_REF
    published = parse_date(published_at)
    if published is None:
        return None
    for phase in PHASES:
        if phase["start"] <= published <= phase["end"]:
            return str(phase["key"]), str(phase["label"]), str(phase["ref"])
    return None


def initial_coverage(
    note_id: str,
    catalog_record: dict[str, Any],
    now: str,
) -> dict[str, Any]:
    card = note_index.canonical_card(note_id)
    card_status = str(card.get("status") or "unknown") if card else "missing"
    if card and card_status in {"analyzed", "reviewed"}:
        coverage_type = "individual_card"
        analysis_ref = f"articles/{card['relative_path']}"
        analysis_unit = "individual_card"
        analysis_label = "個別記事カード"
        state = "covered"
    else:
        phase = phase_for(note_id, str(catalog_record.get("published_at") or ""))
        if phase:
            analysis_unit, analysis_label, analysis_ref = phase
            coverage_type = "phase_bundle"
            state = "covered"
        else:
            coverage_type = "unassigned"
            analysis_ref = ""
            analysis_unit = "unassigned"
            analysis_label = "未割り当て"
            state = "pending"

    covered = state == "covered"
    return {
        "note_id": note_id,
        "analysis_state": state,
        "coverage_type": coverage_type,
        "analysis_unit": analysis_unit,
        "analysis_label": analysis_label,
        "analysis_ref": analysis_ref,
        "role": "",
        "covered_content_hash": str(catalog_record.get("content_hash") or "") if covered else "",
        "covered_title": str(catalog_record.get("title") or "") if covered else "",
        "covered_published_at": str(catalog_record.get("published_at") or "") if covered else "",
        "covered_public_status": str(catalog_record.get("public_status") or "") if covered else "",
        "covered_at": now if covered else "",
        "defer_reason": "",
        "recheck_after": "",
        "recheck_condition": "",
    }


def accept_entry(
    entry: dict[str, Any],
    current: dict[str, Any],
    args: argparse.Namespace,
    now: str,
) -> None:
    analysis_ref = args.analysis_ref.strip()
    if not analysis_ref:
        card = note_index.canonical_card(str(entry["note_id"]))
        if card is None:
            raise ValueError("--analysis-ref is required when no canonical card exists")
        analysis_ref = f"articles/{card['relative_path']}"
    entry.update(
        {
            "analysis_state": "covered",
            "coverage_type": args.coverage_type,
            "analysis_unit": args.coverage_type,
            "analysis_label": args.role.strip() or args.coverage_type,
            "analysis_ref": analysis_ref,
            "role": args.role.strip(),
            "covered_content_hash": str(current.get("content_hash") or ""),
            "covered_title": str(current.get("title") or ""),
            "covered_published_at": str(current.get("published_at") or ""),
            "covered_public_status": str(current.get("public_status") or ""),
            "covered_at": now,
            "defer_reason": "",
            "recheck_after": "",
            "recheck_condition": "",
        }
    )


def review_reasons(entry: dict[str, Any], current: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if entry.get("analysis_state") == "pending":
        reasons.append("new_or_unassigned")
    if str(current.get("content_hash") or "") != str(entry.get("covered_content_hash") or ""):
        if entry.get("analysis_state") == "covered":
            reasons.append("body_changed_after_coverage")
    if str(current.get("title") or "") != str(entry.get("covered_title") or ""):
        if entry.get("analysis_state") == "covered":
            reasons.append("title_changed_after_coverage")
    if str(current.get("published_at") or "") != str(entry.get("covered_published_at") or ""):
        if entry.get("analysis_state") == "covered":
            reasons.append("published_at_changed_after_coverage")
    if str(current.get("public_status") or "") != str(entry.get("covered_public_status") or ""):
        if entry.get("analysis_state") == "covered":
            reasons.append("public_status_changed_after_coverage")
    return reasons


def markdown_link(repo_path: str, from_dir: str = "analysis") -> str:
    if not repo_path:
        return ""
    if from_dir == "analysis":
        return Path("..") / Path(repo_path)
    return Path("..") / Path(repo_path)


def write_coverage_markdown(
    coverage: dict[str, Any],
    catalog_articles: dict[str, dict[str, Any]],
) -> None:
    entries: dict[str, dict[str, Any]] = coverage["articles"]
    state_counts = Counter(str(entry.get("analysis_state") or "unknown") for entry in entries.values())
    unit_counts = Counter(str(entry.get("analysis_unit") or "unknown") for entry in entries.values())
    review_count = 0
    for note_id, entry in entries.items():
        current = catalog_articles.get(note_id, {})
        if review_reasons(entry, current):
            review_count += 1

    lines = [
        "# 全351記事の解析カバレッジ",
        "",
        "このファイルは `scripts/update_analysis_coverage.py` が生成する。",
        "",
        "個別カードの `unreviewed` は、記事全体が未分析という意味ではない。時期別資料束で文脈解析済みの場合がある。",
        "",
        f"- 台帳登録：{len(entries)}件",
        f"- 文脈解析済み：{state_counts.get('covered', 0)}件",
        f"- 未割り当て・新着：{state_counts.get('pending', 0)}件",
        f"- 責任ある保留：{state_counts.get('deferred', 0)}件",
        f"- 再確認対象：{review_count}件",
        "",
        "## 解析単位別",
        "",
        "| 解析単位 | 件数 |",
        "|---|---:|",
    ]
    labels = {
        "phase_01": "第1期",
        "phase_02": "第2期",
        "phase_03": "第3期",
        "phase_04": "第4期",
        "phase_05": "第5期",
        "phase_06": "第6期",
        "individual_card": "個別記事カード",
        "unassigned": "未割り当て",
    }
    for key in ("phase_01", "phase_02", "phase_03", "phase_04", "phase_05", "phase_06", "individual_card", "unassigned"):
        count = unit_counts.get(key, 0)
        if count:
            lines.append(f"| {labels[key]} | {count} |")

    lines.extend(
        [
            "",
            "## 正本関係",
            "",
            "```text",
            "catalog.json",
            "  → 現在公開されている本文・メタデータの状態",
            "",
            "COVERAGE.json",
            "  → どの本文ハッシュまで、どの解析文書で読んだか",
            "",
            "review/INBOX.md",
            "  → 新着・本文変更・公開状態変更・保留の確認待ち",
            "```",
            "",
            "本文が変わっても `covered_content_hash` は自動更新しない。人間が差分を読み、既存文脈への影響を判定してから更新する。",
        ]
    )
    COVERAGE_MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    COVERAGE_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_review_inbox(
    coverage: dict[str, Any],
    catalog_articles: dict[str, dict[str, Any]],
    last_sync: dict[str, Any],
) -> None:
    pending: list[tuple[str, dict[str, Any], dict[str, Any], list[str]]] = []
    deferred: list[tuple[str, dict[str, Any], dict[str, Any], list[str]]] = []
    for note_id, entry in coverage["articles"].items():
        current = catalog_articles.get(note_id, {})
        reasons = review_reasons(entry, current)
        if entry.get("analysis_state") == "deferred":
            deferred.append((note_id, entry, current, reasons))
        elif reasons:
            pending.append((note_id, entry, current, reasons))

    priority = {
        "new_or_unassigned": 0,
        "body_changed_after_coverage": 1,
        "public_status_changed_after_coverage": 2,
        "title_changed_after_coverage": 3,
        "published_at_changed_after_coverage": 4,
    }
    pending.sort(
        key=lambda row: (
            min(priority.get(reason, 99) for reason in row[3]),
            str(row[2].get("published_at") or ""),
            row[0],
        )
    )

    failures = last_sync.get("failures") if isinstance(last_sync.get("failures"), list) else []
    lines = [
        "# note文脈レビュー待ち",
        "",
        "このファイルは自動生成する。新着カードの件数ではなく、既存の解析カバレッジとの差分だけを表示する。",
        "",
        f"- 確認待ち：{len(pending)}件",
        f"- 責任ある保留：{len(deferred)}件",
        f"- 直近同期の取得失敗：{len(failures)}件",
        "",
    ]

    if failures:
        lines.extend(["## P0：取得失敗", ""])
        for failure in failures:
            lines.append(
                f"- `{failure.get('note_id', '')}` {failure.get('url', '')} — {failure.get('error', '')}"
            )
        lines.append("")

    lines.extend(["## P1〜P2：文脈確認待ち", ""])
    if not pending:
        lines.extend(["現在、文脈確認が必要な新着・本文変更・公開状態変更はない。", ""])
    else:
        for note_id, entry, current, reasons in pending:
            card = note_index.canonical_card(note_id)
            title = str(current.get("title") or note_id)
            card_link = f"../articles/{card['relative_path']}" if card else ""
            title_cell = f"[{title}]({card_link})" if card_link else title
            lines.append(f"### {title_cell}")
            lines.append("")
            lines.append(f"- note ID：`{note_id}`")
            lines.append(f"- 公開日：{current.get('published_at', '')}")
            lines.append(f"- 理由：{', '.join(reasons)}")
            lines.append(f"- 既存解析：{entry.get('analysis_ref') or 'なし'}")
            lines.append(f"- 公開本文：{current.get('note_url', '')}")
            lines.append("")

    lines.extend(["## 責任ある保留", ""])
    if not deferred:
        lines.extend(["現在、保留中の項目はない。", ""])
    else:
        for note_id, entry, current, reasons in deferred:
            lines.append(f"- `{note_id}` {current.get('title', '')}")
            lines.append(f"  - 理由：{entry.get('defer_reason', '')}")
            lines.append(f"  - 再確認時期：{entry.get('recheck_after', '') or '未設定'}")
            lines.append(f"  - 再確認条件：{entry.get('recheck_condition', '') or '未設定'}")
            if reasons:
                lines.append(f"  - 現在の差分：{', '.join(reasons)}")

    lines.extend(
        [
            "",
            "## 判定後の処理",
            "",
            "新着・変更を読んだ後、次を同時に決める。",
            "",
            "1. 今回何を更新するか。",
            "2. 記事の役割は、初出・試行・修正・統合・適用・反例・分岐・破棄のどれか。",
            "3. 既存六系譜へ接続するか、それとも新しい枝か。",
            "4. 今回は決めず保留するものは何か。",
            "5. 保留理由、再確認時期、再確認条件は何か。",
            "",
            "解析を受け入れた後にだけ、COVERAGE.jsonの対象記事を現在の本文ハッシュへ進める。",
        ]
    )
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_INBOX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    now = utc_now()
    catalog = load_json(CATALOG_PATH, {"articles": {}})
    catalog_articles = catalog.get("articles")
    if not isinstance(catalog_articles, dict) or not catalog_articles:
        print(f"No catalog articles found: {CATALOG_PATH}", file=sys.stderr)
        return 2

    coverage = load_json(
        COVERAGE_JSON_PATH,
        {"schema_version": SCHEMA_VERSION, "updated_at": "", "articles": {}},
    )
    entries = coverage.get("articles")
    if not isinstance(entries, dict):
        raise ValueError("COVERAGE.json articles must be an object")

    for note_id, current in sorted(catalog_articles.items()):
        if note_id not in entries:
            entries[note_id] = initial_coverage(note_id, current, now)

    command_ids = [value for value in (args.accept, args.defer, args.reopen) if value]
    if len(command_ids) > 1:
        print("Use only one of --accept, --defer, or --reopen", file=sys.stderr)
        return 2

    if args.accept:
        if args.accept not in entries or args.accept not in catalog_articles:
            print(f"Unknown note ID: {args.accept}", file=sys.stderr)
            return 2
        accept_entry(entries[args.accept], catalog_articles[args.accept], args, now)
    elif args.defer:
        if not args.defer_reason.strip():
            print("--defer-reason is required with --defer", file=sys.stderr)
            return 2
        if args.defer not in entries:
            print(f"Unknown note ID: {args.defer}", file=sys.stderr)
            return 2
        entries[args.defer]["analysis_state"] = "deferred"
        entries[args.defer]["defer_reason"] = args.defer_reason.strip()
        entries[args.defer]["recheck_after"] = args.recheck_after.strip()
        entries[args.defer]["recheck_condition"] = args.recheck_condition.strip()
    elif args.reopen:
        if args.reopen not in entries:
            print(f"Unknown note ID: {args.reopen}", file=sys.stderr)
            return 2
        entries[args.reopen]["analysis_state"] = "pending"
        entries[args.reopen]["defer_reason"] = ""
        entries[args.reopen]["recheck_after"] = ""
        entries[args.reopen]["recheck_condition"] = ""

    coverage["schema_version"] = SCHEMA_VERSION
    coverage["updated_at"] = now
    coverage["articles"] = dict(sorted(entries.items()))
    write_json(COVERAGE_JSON_PATH, coverage)

    last_sync = load_json(base.SOURCE_DIR / "last-sync.json", {})
    write_coverage_markdown(coverage, catalog_articles)
    write_review_inbox(coverage, catalog_articles, last_sync)

    counts = Counter(str(entry.get("analysis_state") or "unknown") for entry in entries.values())
    print(
        "coverage: "
        f"total={len(entries)} covered={counts.get('covered', 0)} "
        f"pending={counts.get('pending', 0)} deferred={counts.get('deferred', 0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
