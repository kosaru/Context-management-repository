#!/usr/bin/env python3
"""Build a human review queue from note synchronization change events.

The sync process records facts. This script turns actionable events into a
review queue without deciding their meaning. Human decisions are kept in
sources/note/review-decisions.json and are never overwritten by synchronization.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import collect_note as base
import note_index

CHANGE_LOG_PATH = base.SOURCE_DIR / "change-log.jsonl"
DECISIONS_PATH = base.SOURCE_DIR / "review-decisions.json"
QUEUE_PATH = base.ROOT / "reviews" / "NOTE_REVIEW_QUEUE.md"

ACTIONABLE_EVENTS = {
    "new": "新規記事",
    "body_changed": "本文変更",
    "missing_from_public_index": "公開一覧から消失",
}
INFORMATIONAL_EVENTS = {
    "metadata_changed": "メタデータ変更",
}
CLOSED_STATUSES = {
    "reflected",
    "minor_change",
    "false_positive",
    "no_context_impact",
    "dismissed",
}
VALID_STATUSES = {
    "pending",
    "in_review",
    *CLOSED_STATUSES,
}


def stable_event_id(event: dict[str, Any]) -> str:
    identity = {
        "event": event.get("event", ""),
        "note_id": event.get("note_id", ""),
        "recorded_at": event.get("recorded_at", ""),
        "content_hash_before": event.get("content_hash_before", ""),
        "content_hash_after": event.get("content_hash_after", ""),
        "metadata_changes": event.get("metadata_changes", {}),
        "public_status_after": event.get("public_status_after", ""),
    }
    raw = json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def load_events() -> list[dict[str, Any]]:
    if not CHANGE_LOG_PATH.exists():
        return []
    events: list[dict[str, Any]] = []
    for number, line in enumerate(
        CHANGE_LOG_PATH.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON at {CHANGE_LOG_PATH}:{number}: {exc}") from exc
        if not isinstance(event, dict):
            continue
        event = dict(event)
        event["event_id"] = stable_event_id(event)
        events.append(event)
    return events


def load_decisions() -> dict[str, Any]:
    if not DECISIONS_PATH.exists():
        return {"schema_version": 1, "events": {}}
    payload = json.loads(DECISIONS_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid decisions file: {DECISIONS_PATH}")
    payload.setdefault("schema_version", 1)
    payload.setdefault("events", {})
    if not isinstance(payload["events"], dict):
        raise ValueError(f"Invalid decisions events map: {DECISIONS_PATH}")
    return payload


def decision_for(event_id: str, decisions: dict[str, Any]) -> dict[str, Any]:
    value = decisions["events"].get(event_id, {})
    if not isinstance(value, dict):
        return {}
    status = value.get("status", "pending")
    if status not in VALID_STATUSES:
        status = "pending"
    return {**value, "status": status}


def markdown_escape(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def article_context(note_id: str) -> dict[str, str]:
    card = note_index.canonical_card(note_id)
    if card is None:
        return {
            "title": note_id,
            "card_path": "",
            "analysis_status": "missing",
        }
    return {
        "title": card["title"],
        "card_path": "../articles/" + card["relative_path"],
        "analysis_status": card["status"],
    }


def event_priority(event_type: str) -> int:
    return {
        "missing_from_public_index": 40,
        "body_changed": 30,
        "new": 20,
        "metadata_changed": 10,
    }.get(event_type, 0)


def describe_change(event: dict[str, Any]) -> str:
    event_type = event.get("event", "")
    if event_type == "body_changed":
        before = str(event.get("content_hash_before") or "")[:10]
        after = str(event.get("content_hash_after") or "")[:10]
        return f"本文ハッシュ `{before}` → `{after}`"
    if event_type == "new":
        return "新しいnote IDを検出"
    if event_type == "missing_from_public_index":
        return "完全取得した公開一覧で見つからなかった。削除・非公開確定ではない"
    if event_type == "metadata_changed":
        changes = event.get("metadata_changes", {})
        if not isinstance(changes, dict):
            return "メタデータ変更"
        parts: list[str] = []
        for key, value in sorted(changes.items()):
            if not isinstance(value, dict):
                continue
            parts.append(
                f"{key}: `{markdown_escape(value.get('before'))}` → "
                f"`{markdown_escape(value.get('after'))}`"
            )
        return " / ".join(parts) or "メタデータ変更"
    return markdown_escape(event_type)


def render_event(event: dict[str, Any], decision: dict[str, Any]) -> list[str]:
    note_id = str(event.get("note_id") or "")
    context = article_context(note_id)
    card_link = (
        f"[{markdown_escape(context['title'])}]({context['card_path']})"
        if context["card_path"]
        else markdown_escape(context["title"])
    )
    note_url = str(event.get("note_url") or "")
    note_link = f"[公開本文]({note_url})" if note_url else "-"
    event_type = str(event.get("event") or "")
    label = ACTIONABLE_EVENTS.get(event_type) or INFORMATIONAL_EVENTS.get(event_type) or event_type
    lines = [
        f"## {label}：{card_link}",
        "",
        f"- イベントID：`{event['event_id']}`",
        f"- note ID：`{note_id}`",
        f"- 検出日時：{markdown_escape(event.get('recorded_at'))}",
        f"- 解析状態：{markdown_escape(context['analysis_status'])}",
        f"- 判定状態：`{decision.get('status', 'pending')}`",
        f"- 変更内容：{describe_change(event)}",
        f"- note：{note_link}",
    ]
    reviewer = decision.get("reviewer")
    reviewed_at = decision.get("reviewed_at")
    note = decision.get("note")
    if reviewer:
        lines.append(f"- 確認者：{markdown_escape(reviewer)}")
    if reviewed_at:
        lines.append(f"- 確認日時：{markdown_escape(reviewed_at)}")
    if note:
        lines.append(f"- 判定メモ：{markdown_escape(note)}")

    if event_type in ACTIONABLE_EVENTS and decision.get("status", "pending") not in CLOSED_STATUSES:
        lines.extend(
            [
                "",
                "### 判定チェック",
                "",
                "- [ ] 公開本文またはGit差分を確認した",
                "- [ ] 軽微変更か、論旨へ影響する変更かを分けた",
                "- [ ] 記事の役割を判定した（初出・試行・修正・統合・適用・反例・分岐・破棄）",
                "- [ ] 既存六系譜へ接続できる点と、接続できない抵抗点を分けた",
                "- [ ] 記事カードへの追記要否を判断した",
                "- [ ] CURRENT / LINEAGES / THEMES / CONCEPTS / QUESTIONS / UNRESOLVED の更新要否を判断した",
                "- [ ] `review-decisions.json`へ判定を記録した",
            ]
        )
    return lines


def write_queue() -> None:
    events = load_events()
    decisions = load_decisions()

    pending: list[tuple[dict[str, Any], dict[str, Any]]] = []
    in_review: list[tuple[dict[str, Any], dict[str, Any]]] = []
    informational: list[tuple[dict[str, Any], dict[str, Any]]] = []
    closed_counts: dict[str, int] = defaultdict(int)

    for event in events:
        decision = decision_for(event["event_id"], decisions)
        status = decision.get("status", "pending")
        event_type = event.get("event", "")
        if status in CLOSED_STATUSES:
            closed_counts[status] += 1
            continue
        pair = (event, decision)
        if event_type in ACTIONABLE_EVENTS:
            if status == "in_review":
                in_review.append(pair)
            else:
                pending.append(pair)
        else:
            informational.append(pair)

    sort_key = lambda pair: (
        event_priority(str(pair[0].get("event") or "")),
        str(pair[0].get("recorded_at") or ""),
        str(pair[0].get("note_id") or ""),
    )
    pending.sort(key=sort_key, reverse=True)
    in_review.sort(key=sort_key, reverse=True)
    informational.sort(key=sort_key, reverse=True)

    lines = [
        "# note差分レビューキュー",
        "",
        "このファイルは `scripts/build_note_review_queue.py` が自動生成する。",
        "",
        "同期処理は差分の存在だけを記録する。差分の意味、記事の役割、系譜への影響はここから人間が判断する。",
        "",
        "判定結果は `../sources/note/review-decisions.json` に保存し、同期処理から分離する。",
        "",
        "## 現在の件数",
        "",
        f"- 未確認：{len(pending)}件",
        f"- 確認中：{len(in_review)}件",
        f"- 情報のみ：{len(informational)}件",
        f"- 終了済み：{sum(closed_counts.values())}件",
        "",
    ]

    lines.append("# 未確認")
    lines.append("")
    if pending:
        for event, decision in pending:
            lines.extend(render_event(event, decision))
            lines.extend(["", "---", ""])
    else:
        lines.append("現在、文脈判定が必要な未確認差分はない。")
        lines.append("")

    lines.append("# 確認中")
    lines.append("")
    if in_review:
        for event, decision in in_review:
            lines.extend(render_event(event, decision))
            lines.extend(["", "---", ""])
    else:
        lines.append("現在、確認中の差分はない。")
        lines.append("")

    lines.append("# 情報のみ")
    lines.append("")
    lines.append("メタデータ差異など、原則として文脈更新を要求しないイベント。必要なら判定ファイルで終了状態へ移す。")
    lines.append("")
    if informational:
        for event, decision in informational:
            lines.extend(render_event(event, decision))
            lines.extend(["", "---", ""])
    else:
        lines.append("現在、情報イベントはない。")
        lines.append("")

    lines.extend(
        [
            "# 判定状態",
            "",
            "`review-decisions.json`で使用する状態：",
            "",
            "- `pending`：未確認",
            "- `in_review`：確認中",
            "- `reflected`：必要な文脈更新まで反映済み",
            "- `minor_change`：軽微変更",
            "- `no_context_impact`：変更は確認したが文脈への影響なし",
            "- `false_positive`：誤検出",
            "- `dismissed`：判断のうえ対象外",
            "",
            "終了状態へ移す場合も、イベントログ自体は削除しない。",
        ]
    )

    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    write_queue()
    print(f"wrote {QUEUE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
