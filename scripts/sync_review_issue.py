#!/usr/bin/env python3
"""Create, update, or close the single GitHub issue for note review work."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
INBOX_PATH = ROOT / "review" / "INBOX.md"
ISSUE_TITLE = "note文脈レビュー待ち"
LABEL_NAME = "note-review"
LABEL_COLOR = "1d76db"


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def api_request(
    session: requests.Session,
    method: str,
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    allow_status: set[int] | None = None,
) -> requests.Response:
    response = session.request(method, url, json=payload, timeout=30)
    allowed = allow_status or set()
    if response.status_code not in allowed:
        response.raise_for_status()
    return response


def parse_count(text: str, label: str) -> int:
    match = re.search(rf"^- {re.escape(label)}：([0-9]+)件$", text, flags=re.MULTILINE)
    return int(match.group(1)) if match else 0


def queue_active(text: str) -> bool:
    return any(
        (
            parse_count(text, "確認待ち"),
            parse_count(text, "責任ある保留"),
            parse_count(text, "直近同期の取得失敗"),
        )
    )


def ensure_label(session: requests.Session, api_root: str) -> None:
    response = api_request(
        session,
        "POST",
        f"{api_root}/labels",
        payload={
            "name": LABEL_NAME,
            "color": LABEL_COLOR,
            "description": "note記事の新着・変更・保留に対する文脈レビュー",
        },
        allow_status={201, 422},
    )
    if response.status_code == 422:
        print(f"label already exists: {LABEL_NAME}")


def find_open_issue(session: requests.Session, api_root: str) -> dict[str, Any] | None:
    response = api_request(
        session,
        "GET",
        f"{api_root}/issues?state=open&labels={LABEL_NAME}&per_page=100",
    )
    payload = response.json()
    if not isinstance(payload, list):
        raise RuntimeError("Unexpected issues response")
    for issue in payload:
        if isinstance(issue, dict) and issue.get("title") == ISSUE_TITLE:
            return issue
    return None


def issue_body(inbox: str) -> str:
    return (
        "このIssueは定期同期によって自動管理されます。\n\n"
        "新着・本文変更・公開状態変更・取得失敗・責任ある保留がある間だけ開きます。\n"
        "判断後は `Apply note review decision` ワークフローでカバレッジへ反映します。\n\n"
        "---\n\n"
        f"{inbox.rstrip()}\n"
    )


def main() -> int:
    repository = required_env("GITHUB_REPOSITORY")
    token = required_env("GITHUB_TOKEN")
    if not INBOX_PATH.exists():
        print(f"review inbox not found: {INBOX_PATH}", file=sys.stderr)
        return 2

    inbox = INBOX_PATH.read_text(encoding="utf-8")
    active = queue_active(inbox)
    api_root = f"https://api.github.com/repos/{repository}"

    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "note-context-review-bot/1.0",
        }
    )

    ensure_label(session, api_root)
    issue = find_open_issue(session, api_root)

    if active:
        body = issue_body(inbox)
        if issue:
            api_request(
                session,
                "PATCH",
                f"{api_root}/issues/{issue['number']}",
                payload={"body": body, "labels": [LABEL_NAME]},
            )
            print(f"updated review issue #{issue['number']}")
        else:
            response = api_request(
                session,
                "POST",
                f"{api_root}/issues",
                payload={"title": ISSUE_TITLE, "body": body, "labels": [LABEL_NAME]},
            )
            print(f"created review issue #{response.json().get('number')}")
    elif issue:
        api_request(
            session,
            "PATCH",
            f"{api_root}/issues/{issue['number']}",
            payload={"state": "closed", "state_reason": "completed"},
        )
        print(f"closed review issue #{issue['number']}")
    else:
        print("review queue empty; no open issue")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
